"""
allen-product-design — 图片生成脚本
支持两种 API 后端:
  1. NanoBanana API (异步任务模式)
  2. Gemini via OpenAI-compatible API (同步 chat completions 模式, 如 new.suxi.ai)
通过环境变量 IMAGE_API_MODE 切换: "nanobanana" (默认) 或 "gemini"
"""

import argparse
import json
import os
import sys
import io
import re
import time
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Install: pip install requests")
    sys.exit(1)


# ─── 配置 ─────────────────────────────────────────────────────
def get_api_mode():
    return os.environ.get("IMAGE_API_MODE", "gemini").lower()

def get_headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

def download_image(url: str, save_path: Path) -> bool:
    """下载图片到本地"""
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [ERROR] Download failed: {url} -> {e}", file=sys.stderr)
        return False


# ═══════════════════════════════════════════════════════════════
# GEMINI MODE (OpenAI-compatible chat completions, e.g. new.suxi.ai)
# ═══════════════════════════════════════════════════════════════

GEMINI_BASE_URL = os.environ.get("GEMINI_API_BASE", "https://new.suxi.ai")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-image-preview")

GEMINI_MODEL_MAP = {
    "nanobanana":     "gemini-3.1-flash-image-preview",
    "nanobanana-2":   "gemini-3.1-flash-image-preview",
    "nanobanana-pro": "gemini-3-pro-image-preview",
}


def gemini_generate(api_key: str, prompt: str, model_key: str) -> dict:
    """通过 Gemini chat completions 生成图片，返回 {status, url, error}"""
    gemini_model = GEMINI_MODEL_MAP.get(model_key, GEMINI_MODEL)
    url = f"{GEMINI_BASE_URL}/v1/chat/completions"

    body = {
        "model": gemini_model,
        "messages": [
            {"role": "user", "content": f"Generate an image: {prompt}"}
        ],
    }

    try:
        resp = requests.post(url, headers=get_headers(api_key), json=body, timeout=180)
        data = resp.json()

        if "error" in data:
            return {"status": "ERROR", "error": data["error"].get("message", str(data["error"]))}

        if "choices" not in data:
            return {"status": "ERROR", "error": f"Unexpected response: {str(data)[:300]}"}

        content = data["choices"][0].get("message", {}).get("content", "")

        # Case 1: content is a list (multimodal parts)
        if isinstance(content, list):
            for part in content:
                if part.get("type") == "image_url":
                    img_url = part["image_url"]["url"]
                    if img_url.startswith("data:"):
                        return {"status": "SUCCESS", "b64": img_url.split(",", 1)[1]}
                    else:
                        return {"status": "SUCCESS", "url": img_url}
            return {"status": "ERROR", "error": "No image in response parts"}

        # Case 2: content is a string with markdown image
        if isinstance(content, str):
            # Extract URL from ![image](https://...)
            match = re.search(r'!\[.*?\]\((https?://[^\)]+)\)', content)
            if match:
                return {"status": "SUCCESS", "url": match.group(1)}
            # Extract base64
            match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
            if match:
                return {"status": "SUCCESS", "b64": match.group(1)}
            return {"status": "ERROR", "error": f"No image found in response: {content[:200]}"}

        return {"status": "ERROR", "error": "Unknown content format"}

    except requests.Timeout:
        return {"status": "ERROR", "error": "Request timeout (180s)"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}


def process_single_gemini(api_key: str, model_key: str, idx: int, entry: dict, output_dir: Path) -> dict:
    """处理单个 Gemini 生成任务"""
    label = entry.get("label", f"image_{idx:03d}")
    group = entry.get("group", "ungrouped")
    prompt = entry["prompt"]

    print(f"  [{idx+1}] Generating: {label}")
    result = {"index": idx, "label": label, "group": group, "prompt": prompt}

    gen_result = gemini_generate(api_key, prompt, model_key)
    result["status"] = gen_result["status"]

    if gen_result["status"] == "SUCCESS":
        ext = "jpg"
        filename = f"{label}.{ext}"
        save_path = output_dir / group / filename

        if "url" in gen_result:
            if download_image(gen_result["url"], save_path):
                result["file"] = str(save_path)
                result["url"] = gen_result["url"]
                print(f"  [{idx+1}] SUCCESS -> {save_path}")
            else:
                result["status"] = "DOWNLOAD_FAILED"
                result["url"] = gen_result["url"]
                print(f"  [{idx+1}] DOWNLOAD_FAILED")
        elif "b64" in gen_result:
            try:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                img_bytes = base64.b64decode(gen_result["b64"])
                with open(save_path, "wb") as f:
                    f.write(img_bytes)
                result["file"] = str(save_path)
                print(f"  [{idx+1}] SUCCESS -> {save_path} ({len(img_bytes)} bytes)")
            except Exception as e:
                result["status"] = "SAVE_FAILED"
                result["error"] = str(e)
                print(f"  [{idx+1}] SAVE_FAILED: {e}")
    else:
        result["error"] = gen_result.get("error", "Unknown")
        print(f"  [{idx+1}] {result['status']}: {result.get('error')}")

    return result


# ═══════════════════════════════════════════════════════════════
# NANOBANANA MODE (async task-based API)
# ═══════════════════════════════════════════════════════════════

NB_API_BASE = os.environ.get("NANOBANANA_API_BASE", "https://api.nanobananaapi.ai/api/v1/nanobanana")

NB_ENDPOINTS = {
    "nanobanana":     f"{NB_API_BASE}/generate",
    "nanobanana-2":   f"{NB_API_BASE}/generate-2",
    "nanobanana-pro": f"{NB_API_BASE}/generate-pro",
}


def nb_submit_task(api_key: str, model: str, prompt_entry: dict) -> str:
    prompt = prompt_entry["prompt"]
    aspect_ratio = prompt_entry.get("aspect_ratio", "4:3")
    resolution = prompt_entry.get("resolution", "2K")
    output_format = prompt_entry.get("output_format", "jpg")

    if model == "nanobanana":
        body = {"prompt": prompt, "type": "TEXTTOIAMGE", "numImages": 1,
                "image_size": aspect_ratio, "callBackUrl": "https://noop.callback.local/noop"}
    elif model == "nanobanana-2":
        body = {"prompt": prompt, "imageUrls": [], "aspectRatio": aspect_ratio,
                "resolution": resolution, "googleSearch": False, "outputFormat": output_format}
    elif model == "nanobanana-pro":
        body = {"prompt": prompt, "imageUrls": [], "resolution": resolution, "aspectRatio": aspect_ratio}
    else:
        raise ValueError(f"Unknown model: {model}")

    endpoint = NB_ENDPOINTS[model]
    resp = requests.post(endpoint, headers=get_headers(api_key), json=body, timeout=30)
    data = resp.json()
    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {data}")
    code = data.get("code")
    if code != 200:
        raise RuntimeError(f"API returned code {code}: {data.get('msg') or data.get('message')}")
    task_id = data.get("data", {}).get("taskId")
    if not task_id:
        raise RuntimeError(f"No taskId in response: {data}")
    return task_id


def nb_poll_task(api_key: str, task_id: str, max_wait: int = 300, interval: int = 3) -> dict:
    status_url = f"{NB_API_BASE}/record-info"
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(status_url, params={"taskId": task_id},
                                headers=get_headers(api_key), timeout=15)
            task_data = resp.json().get("data", {})
            flag = task_data.get("successFlag")
            if flag == 1:
                return {"status": "SUCCESS",
                        "resultImageUrl": task_data.get("response", {}).get("resultImageUrl")}
            elif flag in (2, 3):
                return {"status": "GENERATE_FAILED", "error": task_data.get("errorMessage", "Unknown")}
        except Exception as e:
            print(f"  [WARN] Poll error for {task_id}: {e}", file=sys.stderr)
        time.sleep(interval)
    return {"status": "TIMEOUT", "error": f"Task {task_id} timed out"}


def process_single_nanobanana(api_key: str, model: str, idx: int, entry: dict, output_dir: Path) -> dict:
    label = entry.get("label", f"image_{idx:03d}")
    group = entry.get("group", "ungrouped")
    result = {"index": idx, "label": label, "group": group, "prompt": entry["prompt"]}
    print(f"  [{idx+1}] Submitting: {label}")
    try:
        task_id = nb_submit_task(api_key, model, entry)
        result["taskId"] = task_id
        print(f"  [{idx+1}] TaskId: {task_id}, polling...")
        poll_result = nb_poll_task(api_key, task_id)
        result["status"] = poll_result["status"]
        if poll_result["status"] == "SUCCESS":
            image_url = poll_result["resultImageUrl"]
            ext = entry.get("output_format", "jpg")
            save_path = output_dir / group / f"{label}.{ext}"
            if download_image(image_url, save_path):
                result["file"] = str(save_path)
                result["url"] = image_url
                print(f"  [{idx+1}] SUCCESS -> {save_path}")
            else:
                result["status"] = "DOWNLOAD_FAILED"
        else:
            result["error"] = poll_result.get("error", "Unknown")
            print(f"  [{idx+1}] {result['status']}: {result.get('error')}")
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        print(f"  [{idx+1}] ERROR: {e}", file=sys.stderr)
    return result


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Product Design Image Generator")
    parser.add_argument("--prompts", required=True, help="Path to prompts.json")
    parser.add_argument("--api-key-env", default="NANOBANANA_API_KEY", help="Env var name for API key")
    parser.add_argument("--model", default="nanobanana-2",
                        choices=["nanobanana", "nanobanana-2", "nanobanana-pro"])
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--output-dir", default="output/images", help="Output directory for images")
    parser.add_argument("--max-concurrent", type=int, default=3, help="Max concurrent API calls")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts but don't call API")
    args = parser.parse_args()

    api_mode = get_api_mode()

    # 1. API Key
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        print(f"ERROR: Environment variable {args.api_key_env} is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Load prompts
    prompts_path = Path(args.prompts)
    if not prompts_path.exists():
        print(f"ERROR: Prompts file not found: {prompts_path}", file=sys.stderr)
        sys.exit(1)

    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts_data = json.load(f)

    entries = prompts_data if isinstance(prompts_data, list) else prompts_data.get("prompts", [])
    if not entries:
        print("ERROR: No prompts found in file.", file=sys.stderr)
        sys.exit(1)

    for entry in entries:
        if "resolution" not in entry:
            entry["resolution"] = args.resolution

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mode_label = f"Gemini ({GEMINI_BASE_URL})" if api_mode == "gemini" else f"NanoBanana ({NB_API_BASE})"
    print(f"=== Allen Product Design Image Generator ===")
    print(f"API Mode:   {mode_label}")
    print(f"Model:      {args.model}")
    print(f"Resolution: {args.resolution}")
    print(f"Prompts:    {len(entries)}")
    print(f"Output:     {output_dir}")
    print(f"Concurrent: {args.max_concurrent}")
    print()

    if args.dry_run:
        print("=== DRY RUN ===")
        for i, entry in enumerate(entries):
            print(f"\n--- [{i+1}] {entry.get('label', 'unnamed')} ---")
            print(f"Group: {entry.get('group', 'ungrouped')}")
            print(f"Prompt: {entry['prompt'][:200]}...")
        print(f"\n=== {len(entries)} prompts ready. Remove --dry-run to generate. ===")
        return

    # 3. Execute generation
    results = []
    process_fn = process_single_gemini if api_mode == "gemini" else process_single_nanobanana

    with ThreadPoolExecutor(max_workers=args.max_concurrent) as executor:
        futures = {
            executor.submit(process_fn, api_key, args.model, i, entry, output_dir): i
            for i, entry in enumerate(entries)
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    results.sort(key=lambda x: x["index"])

    # 4. Write results
    results_path = output_dir.parent / "generation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 5. Summary
    success = sum(1 for r in results if r["status"] == "SUCCESS")
    failed = len(results) - success

    summary = {
        "api_mode": api_mode,
        "model": args.model,
        "resolution": args.resolution,
        "total": len(results),
        "success": success,
        "failed": failed,
        "output_dir": str(output_dir),
    }

    summary_path = output_dir.parent / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n=== Generation Complete ===")
    print(f"Success: {success}/{len(results)}")
    print(f"Failed:  {failed}/{len(results)}")
    print(f"Results: {results_path}")
    print(f"Images:  {output_dir}")

    if failed > 0:
        print(f"\nFailed tasks:")
        for r in results:
            if r["status"] != "SUCCESS":
                print(f"  - [{r['index']+1}] {r['label']}: {r['status']} -- {r.get('error', 'N/A')}")

    sys.exit(0 if success > 0 else 1)


if __name__ == "__main__":
    main()
