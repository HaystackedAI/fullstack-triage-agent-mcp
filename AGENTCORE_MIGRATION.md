# AgentCore Migration Guide

## Current Status: Calculator (mcp1) Migration

### ✅ What's Done

1. **Calculator deployed to AgentCore**
   - Runtime ARN: `arn:aws:bedrock-agentcore:us-east-1:822206589627:runtime/mcp1_Cal-3WVTZZ55XO`
   - Location: `B:\fullstack-triage-agent-mcp\agentcore_runtime\mcp1\`

2. **Backend updated to support AgentCore**
   - `mcp.json` - Calculator now uses AgentCore transport
   - `main.py` - Added AgentCore transport support
   - `agentcore_mcp_client.py` - Created compatibility wrapper

3. **Files modified:**
   - ✅ `backend/mcp.json` - Updated calculator config
   - ✅ `backend/main.py` - Added AgentCore transport logic
   - ✅ `backend/agentcore_mcp_client.py` - New file (AgentCore client wrapper)
   - ✅ `backend/test_agentcore.py` - Test script

### 🧪 Testing

**Step 1: Test AgentCore connection directly**
```bash
cd B:\fullstack-triage-agent-mcp\backend
python test_agentcore.py
```

Expected output:
```
✅ Found 5 tools: add, subtract, multiply, divide, greet_user
✅ add(10, 5) = 15
✅ multiply(7, 8) = 56
```

**Step 2: Restart backend**
```bash
python main.py
```

Look for:
```
INFO: Setting up AgentCore MCP server: arn:aws:bedrock-agentcore:...
INFO: AgentCore MCP server ready
```

**Step 3: Test from frontend**
Open browser and ask:
```
What is 50 times 12?
```

Should call AgentCore calculator and return `600`.

---

## Configuration

### Current `mcp.json`

```json
{
  "mcpServers": {
    "calculator": {
      "transport": "agentcore",
      "runtime_arn": "arn:aws:bedrock-agentcore:us-east-1:822206589627:runtime/mcp1_Cal-3WVTZZ55XO",
      "region": "us-east-1",
      "enabled": true
    },
    "task_manager": {
      "command": "python",
      "args": ["mcp_servers/task_manager_server.py"],
      "enabled": true
    },
    "weather": {
      "command": "python",
      "args": ["mcp_servers/weather/weather_server.py"],
      "enabled": true
    },
    "calendar": {
      "command": "python",
      "args": ["mcp_servers/calendar/calendar_server.py"],
      "enabled": true
    },
    "email_history": {
      "command": "python",
      "args": ["mcp_servers/email_history/email_history_server.py"],
      "enabled": true
    }
  }
}
```

---

## Next Steps (One by One)

### 📋 Remaining MCP Servers

Once calculator works, migrate these one-by-one:

1. ❌ **Task Manager** → `mcp2`
2. ❌ **Weather** → `mcp3`
3. ❌ **Calendar** → `mcp4`
4. ❌ **Email History** → `mcp5`

### Migration Pattern (For Each Server)

**Step 1: Create AgentCore project**
```bash
cd B:\fullstack-triage-agent-mcp\agentcore_runtime\
agentcore create mcp2
cd mcp2
```

**Step 2: Copy MCP server code**
```bash
# Copy from backend/mcp_servers/task_manager_server.py
# to agentcore_runtime/mcp2/app/TaskManager/main.py
```

**Step 3: Update transport**
Make sure `main.py` uses:
```python
mcp.run(transport="streamable-http")  # NOT stdio
```

**Step 4: Deploy**
```bash
agentcore deploy
```

**Step 5: Get runtime ARN**
```bash
agentcore status
```

**Step 6: Update backend `mcp.json`**
Replace stdio config with:
```json
{
  "transport": "agentcore",
  "runtime_arn": "arn:aws:bedrock-agentcore:...",
  "region": "us-east-1",
  "enabled": true
}
```

**Step 7: Test**
```bash
python main.py  # Restart backend
# Test from frontend
```

---

## Architecture

### Before (Local MCP Servers)
```
Frontend → Backend → [stdio] → Local MCP Servers (Python processes)
```

### After (AgentCore Runtime)
```
Frontend → Backend → [AWS SDK] → AgentCore Runtime (AWS Managed)
                                       ├─ Calculator (mcp1)
                                       ├─ Task Manager (mcp2)
                                       ├─ Weather (mcp3)
                                       ├─ Calendar (mcp4)
                                       └─ Email History (mcp5)
```

### Hybrid (Current State)
```
Frontend → Backend → ├─ [AWS SDK] → AgentCore Calculator (mcp1)
                     ├─ [stdio] → Local Task Manager
                     ├─ [stdio] → Local Weather
                     ├─ [stdio] → Local Calendar
                     └─ [stdio] → Local Email History
```

---

## Benefits of AgentCore

✅ **Scalability** - AWS manages scaling, no local processes  
✅ **Reliability** - AWS handles failures and restarts  
✅ **Monitoring** - CloudWatch logs and metrics  
✅ **Security** - IAM roles and VPC integration  
✅ **Cost** - Pay per invocation, not per running process  

---

## Troubleshooting

### Error: "Module 'agentcore_mcp_client' not found"
```bash
# Make sure file exists:
ls backend/agentcore_mcp_client.py
```

### Error: "Runtime ARN not found"
```bash
# Check AgentCore status:
cd agentcore_runtime/mcp1
agentcore status
```

### Error: "Boto3 ClientError"
```bash
# Check AWS credentials:
aws sts get-caller-identity

# Should show:
# Account: 822206589627
# Region: us-east-1
```

### Calculator not being called
Check server logs in UI. Should see:
```
INFO: AgentCore MCP server ready: arn:aws:bedrock-agentcore:...
INFO: Loaded 5 tools from calculator
```

---

## Contact & Support

- AgentCore Docs: https://github.com/aws/agentcore-cli
- Backend Code: `B:\fullstack-triage-agent-mcp\backend\`
- AgentCore Projects: `B:\fullstack-triage-agent-mcp\agentcore_runtime\`

**Current Focus: Calculator only**  
**Next: Task Manager (after calculator confirmed working)**
