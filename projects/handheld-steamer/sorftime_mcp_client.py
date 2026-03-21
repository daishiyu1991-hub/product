"""
Sorftime MCP SSE Client - 通过 SSE 协议调用 Sorftime MCP 工具
"""
import json
import urllib.request
import urllib.parse
import ssl
import sys
import time
import threading
import uuid

MCP_BASE_URL = "https://mcp.sorftime.com"
API_KEY = "cdm0v2vknhneyurmumrra0hgutftut09"

# Create SSL context that accepts all certs (for testing)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def sse_connect():
    """Connect to SSE endpoint and get the message endpoint URL"""
    url = f"{MCP_BASE_URL}/sse?key={API_KEY}"
    req = urllib.request.Request(url, headers={
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    })

    try:
        response = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
        # Read the first SSE event to get the message endpoint
        message_url = None
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('data:'):
                data = line[5:].strip()
                # The first event should contain the message endpoint URL
                message_url = data
                break
            elif line.startswith('event:'):
                event_type = line[6:].strip()

        return message_url, response
    except Exception as e:
        print(f"SSE connection error: {e}")
        return None, None


def call_tool_via_post(message_url, tool_name, arguments):
    """Call a tool via the MCP message endpoint"""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(message_url, data=data, headers={
        "Content-Type": "application/json",
    })

    try:
        response = urllib.request.urlopen(req, context=ssl_ctx, timeout=30)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Tool call error: {e}")
        return None


def try_direct_api(tool_name, arguments):
    """Try calling Sorftime via direct REST API patterns"""
    patterns = [
        f"{MCP_BASE_URL}/api/{tool_name}",
        f"{MCP_BASE_URL}/tools/{tool_name}",
        f"{MCP_BASE_URL}/v1/{tool_name}",
        f"{MCP_BASE_URL}/call/{tool_name}",
    ]

    for url in patterns:
        url_with_key = f"{url}?key={API_KEY}"
        data = json.dumps(arguments).encode('utf-8')
        req = urllib.request.Request(url_with_key, data=data, headers={
            "Content-Type": "application/json",
        })
        try:
            response = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
            result = response.read().decode('utf-8')
            print(f"Success with URL pattern: {url}")
            return json.loads(result)
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8', errors='replace')[:200]
            print(f"  {url} -> HTTP {status}: {body}")
        except Exception as e:
            print(f"  {url} -> Error: {e}")

    return None


def try_jsonrpc(tool_name, arguments):
    """Try JSON-RPC style call"""
    endpoints = [
        f"{MCP_BASE_URL}/message?key={API_KEY}",
        f"{MCP_BASE_URL}/messages?key={API_KEY}",
        f"{MCP_BASE_URL}/rpc?key={API_KEY}",
        f"{MCP_BASE_URL}/jsonrpc?key={API_KEY}",
        f"{MCP_BASE_URL}/mcp?key={API_KEY}",
    ]

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    for url in endpoints:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            "Content-Type": "application/json",
        })
        try:
            response = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
            result = response.read().decode('utf-8')
            print(f"Success with JSON-RPC endpoint: {url}")
            return json.loads(result)
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8', errors='replace')[:200]
            print(f"  {url} -> HTTP {status}: {body}")
        except Exception as e:
            print(f"  {url} -> Error: {e}")

    return None


def try_sse_with_post():
    """Try SSE connection followed by POST to message endpoint"""
    url = f"{MCP_BASE_URL}/sse?key={API_KEY}"
    req = urllib.request.Request(url, headers={
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    })

    try:
        response = urllib.request.urlopen(req, context=ssl_ctx, timeout=10)
        print(f"SSE Response status: {response.status}")
        print(f"SSE Response headers: {dict(response.headers)}")

        # Read first few lines
        lines_read = 0
        for line in response:
            decoded = line.decode('utf-8', errors='replace').strip()
            if decoded:
                print(f"SSE line: {decoded}")
            lines_read += 1
            if lines_read > 10:
                break

        return True
    except urllib.error.HTTPError as e:
        print(f"SSE HTTP Error: {e.code}")
        body = e.read().decode('utf-8', errors='replace')[:500]
        print(f"SSE Response body: {body}")
        return False
    except Exception as e:
        print(f"SSE Error: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Sorftime MCP Connection")
    print("=" * 60)

    # Test 1: SSE connection
    print("\n--- Test 1: SSE Connection ---")
    try_sse_with_post()

    # Test 2: JSON-RPC calls
    print("\n--- Test 2: JSON-RPC Endpoints ---")
    result = try_jsonrpc("tools/list", {})
    if result:
        print(f"Tools list result: {json.dumps(result, indent=2)[:500]}")

    # Test 3: Direct API
    print("\n--- Test 3: Direct API ---")
    result = try_direct_api("category_search_from_product_name", {
        "product_name": "vacuum steamer",
        "site": "US"
    })
    if result:
        print(f"Category search result: {json.dumps(result, indent=2)[:500]}")
