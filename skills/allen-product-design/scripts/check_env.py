"""
环境检查脚本 -- 验证 NanoBanana API 调用环境是否就绪。
"""

import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_all():
    errors = []
    warnings = []

    # 1. Check API Key
    api_key = os.environ.get("NANOBANANA_API_KEY")
    if not api_key:
        errors.append(
            "NANOBANANA_API_KEY not set.\n"
            "  Set it: set NANOBANANA_API_KEY=your_api_key\n"
            "  Get key: https://nanobananaapi.ai/dashboard"
        )
    else:
        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
        print(f"[OK] NANOBANANA_API_KEY = {masked}")

    # 2. Check requests library
    try:
        import requests
        print(f"[OK] requests library v{requests.__version__}")
    except ImportError:
        errors.append("Python requests not installed.\n  Install: pip install requests")

    # 3. Test API Key (if available)
    if api_key:
        try:
            import requests
            resp = requests.get(
                "https://api.nanobananaapi.ai/api/v1/common/get-credits",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            data = resp.json()
            if resp.status_code == 200 and data.get("code") == 200:
                print(f"[OK] API Key valid, account: {data.get('data', 'N/A')}")
            elif resp.status_code == 401:
                errors.append("API Key invalid or expired. Get new key: https://nanobananaapi.ai/dashboard")
            else:
                warnings.append(f"API returned non-200: {data}")
        except Exception as e:
            warnings.append(f"Cannot connect to NanoBanana API: {e}")

    # 4. Check output directory writability
    test_dir = os.path.join("output", "images")
    try:
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, ".write_test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"[OK] Output dir writable: {test_dir}")
    except Exception as e:
        errors.append(f"Output dir not writable: {test_dir} -- {e}")

    # Report
    print()
    if warnings:
        print("[WARN] Warnings:")
        for w in warnings:
            print(f"  - {w}")
        print()

    if errors:
        print("[FAIL] Environment check failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("[PASS] Environment check passed -- ready to generate images")
        sys.exit(0)


if __name__ == "__main__":
    check_all()
