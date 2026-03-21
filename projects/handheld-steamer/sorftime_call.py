"""
Sorftime MCP 调用辅助脚本
通过 Streamable HTTP 协议调用 Sorftime MCP 工具
"""
import json
import urllib.request
import ssl
import sys
import os

MCP_URL = "https://mcp.sorftime.com/?key=cdm0v2vknhneyurmumrra0hgutftut09"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def call_tool(tool_name, arguments, call_id=1):
    """调用 Sorftime MCP 工具"""
    payload = {
        "jsonrpc": "2.0",
        "id": call_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(MCP_URL, data=data, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })

    try:
        response = urllib.request.urlopen(req, context=ssl_ctx, timeout=60)
        raw = response.read().decode('utf-8')
        # SSE format: "event: message\ndata: {...}"
        for line in raw.split('\n'):
            if line.startswith('data:'):
                return json.loads(line[5:].strip())
        return {"raw": raw}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:500]
        return {"error": f"HTTP {e.code}", "body": body}
    except Exception as e:
        return {"error": str(e)}


def save_result(filename, data):
    """保存结果到文件"""
    os.makedirs("C:/Users/Administrator/vacuum_steamer_research/data", exist_ok=True)
    filepath = f"C:/Users/Administrator/vacuum_steamer_research/data/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filepath}")
    return filepath


if __name__ == "__main__":
    tool_name = sys.argv[1] if len(sys.argv) > 1 else "get_time"
    args_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    arguments = json.loads(args_json)
    print(f"Calling: {tool_name}")
    print(f"Args: {json.dumps(arguments, ensure_ascii=False)}")

    result = call_tool(tool_name, arguments)

    if output_file:
        save_result(output_file, result)

    # Print result (truncated for readability)
    result_str = json.dumps(result, ensure_ascii=False, indent=2)
    if len(result_str) > 3000:
        print(result_str[:3000])
        print(f"\n... [truncated, total {len(result_str)} chars]")
    else:
        print(result_str)
