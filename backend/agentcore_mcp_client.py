"""
AgentCore MCP Client Wrapper
Provides compatibility layer between Strands MCPClient and AWS Bedrock AgentCore Runtime
"""

import boto3
import json
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError


class AgentCoreMCPClient:
    """
    Wrapper for AWS Bedrock AgentCore Runtime that implements MCPClient-compatible interface
    """

    def __init__(self, runtime_arn: str, region: str = "us-east-1", server_name: str = "agentcore"):
        self.runtime_arn = runtime_arn
        self.region = region
        self.server_name = server_name
        self.client = boto3.client('bedrock-agentcore', region_name=region)
        self._tools_cache = None

    def list_tools_sync(self) -> List[Any]:
        """
        List tools from AgentCore runtime (synchronous)
        Compatible with Strands MCPClient.list_tools_sync()

        Note: MCP is a standard protocol, so AgentCore and Strands use the same format.
        No conversion needed if both follow MCP spec correctly.
        """
        if self._tools_cache:
            return self._tools_cache

        try:
            # Call AgentCore runtime to list tools using MCP protocol
            payload = json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 1
            })

            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                payload=payload,
                contentType='application/json',
                mcpProtocolVersion='2024-11-05'
            )

            # Parse streaming response
            result_text = ""
            if 'completion' in response:
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk_data = event['chunk'].get('bytes', b'')
                        result_text += chunk_data.decode('utf-8')

            result = json.loads(result_text) if result_text else {}
            tools = result.get('result', {}).get('tools', [])

            # MCP standard format - should work directly with Strands
            # Both use: {name, description, inputSchema}
            self._tools_cache = tools
            return self._tools_cache

        except ClientError as e:
            print(f"Error listing tools from AgentCore: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error listing tools: {e}")
            return []

    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on AgentCore runtime (synchronous)
        Compatible with Strands MCPClient.call_tool_sync()
        """
        try:
            # Call AgentCore runtime to execute tool using MCP protocol
            payload = json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 2
            })

            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                payload=payload,
                contentType='application/json',
                mcpProtocolVersion='2024-11-05'
            )

            # Parse streaming response
            result_text = ""
            if 'completion' in response:
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk_data = event['chunk'].get('bytes', b'')
                        result_text += chunk_data.decode('utf-8')

            result = json.loads(result_text) if result_text else {}
            return result.get('result', {}).get('content', [])

        except ClientError as e:
            error_msg = f"AgentCore tool call error: {e}"
            print(error_msg)
            return [{"type": "text", "text": error_msg}]
        except Exception as e:
            error_msg = f"Unexpected error calling tool: {e}"
            print(error_msg)
            return [{"type": "text", "text": error_msg}]


    def start(self):
        """Compatibility method - AgentCore is already running"""
        pass

    def stop(self):
        """Compatibility method - AgentCore runtime persists"""
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
