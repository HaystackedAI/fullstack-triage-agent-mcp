"""
Quick test script for AgentCore MCP connection
Run this to verify the AgentCore calculator is accessible
"""

import boto3
import json
from agentcore_mcp_client import AgentCoreMCPClient

# Test configuration
RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:822206589627:runtime/mcp1_Cal-3WVTZZ55XO"
REGION = "us-east-1"

def test_agentcore_connection():
    print("🧪 Testing AgentCore MCP Connection...")
    print(f"Runtime ARN: {RUNTIME_ARN}")
    print(f"Region: {REGION}\n")

    try:
        # Create client
        client = AgentCoreMCPClient(
            runtime_arn=RUNTIME_ARN,
            region=REGION,
            server_name="calculator"
        )

        # Test 1: List tools
        print("📋 Test 1: Listing tools...")
        tools = client.list_tools_sync()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.get('name')}: {tool.get('description')}")
        print()

        # Test 2: Call add tool
        print("🔢 Test 2: Calling add(10, 5)...")
        result = client.call_tool_sync("add", {"x": 10, "y": 5})
        print(f"✅ Result: {result}")
        print()

        # Test 3: Call multiply tool
        print("🔢 Test 3: Calling multiply(7, 8)...")
        result = client.call_tool_sync("multiply", {"x": 7, "y": 8})
        print(f"✅ Result: {result}")
        print()

        print("🎉 All tests passed! AgentCore calculator is working.")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agentcore_connection()
