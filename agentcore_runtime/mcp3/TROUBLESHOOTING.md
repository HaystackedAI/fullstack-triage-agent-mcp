# TaskManager PostgreSQL Connection Troubleshooting

## Problem
TaskManager MCP server times out after 30 seconds during initialization when trying to connect to Aiven PostgreSQL.

## Root Cause
**Network connectivity issue**: AgentCore runtime in PUBLIC mode cannot reach Aiven PostgreSQL endpoint.

- Aiven endpoint: `pgservice-tooproj.c.aivencloud.com:26061`
- AgentCore network mode: `PUBLIC`
- Connection attempts timeout (tested with 5s, 10s timeouts - all fail)

## Evidence
```
Runtime initialization time exceeded. Please make sure that initialization completes in 30s.
```

The asyncpg connection hangs indefinitely, never completing or throwing an error.

## Solutions

### Option 1: Switch to VPC Mode (Recommended)
Configure AgentCore to use VPC mode to access private network resources:

```json
{
  "runtimes": [{
    "networkMode": "VPC",
    "networkConfig": {
      "subnets": ["subnet-xxx", "subnet-yyy"],
      "securityGroups": ["sg-xxx"]
    }
  }]
}
```

**Requirements:**
- VPC with subnets in us-east-1
- Security group allowing outbound to Aiven (port 26061)
- NAT Gateway or VPC endpoints for internet access

### Option 2: Whitelist AgentCore IPs in Aiven
Add AgentCore's public IP ranges to Aiven's allowed IP list.

**Steps:**
1. Get AgentCore runtime public IPs (check CloudWatch logs for connection attempts)
2. Add to Aiven console: Settings → Allowed IP Addresses
3. Redeploy TaskManager

### Option 3: Use AWS RDS PostgreSQL
Switch to AWS RDS PostgreSQL which AgentCore can reach directly:

```bash
# Create RDS instance in same region
aws rds create-db-instance \
  --db-instance-identifier agentcore-tasks \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --publicly-accessible
```

Then update `DATABASE_URL` environment variable.

### Option 4: Use Session Storage (Fallback)
If PostgreSQL isn't critical, use AgentCore's session storage:

```json
{
  "runtimes": [{
    "filesystemConfigurations": [{
      "sessionStorage": {
        "mountPath": "/mnt/tasks"
      }
    }]
  }]
}
```

Then modify code to use file-based storage on `/mnt/tasks/tasks.json`.

## Current Configuration

**Environment Variables (set in AWS Console):**
- `DATABASE_URL`: `postgresql://avnadmin:***@pgservice-tooproj.c.aivencloud.com:26061/agentcoredb`
- `AIVEN_DB_URL`: (same)

**Code Settings:**
- SSL: Enabled with custom context (CERT_NONE)
- Connection timeout: 5-10 seconds
- Pool size: min=1, max=10

**AgentCore Config:**
- Network mode: PUBLIC ❌ (needs VPC)
- Region: us-east-1
- Runtime: PYTHON_3_14

## Next Steps

1. **Check Aiven firewall settings** - Does it allow connections from anywhere? Or specific IPs only?
2. **Try VPC mode** - This is the most reliable solution for private database access
3. **Or switch to AWS RDS** - Simpler integration with AgentCore

## Test Commands

```bash
# Check runtime status
cd agentcore_runtime/mcp3
agentcore status

# Test invocation
agentcore invoke --runtime TaskManager --prompt "list tasks"

# Check logs
agentcore logs --runtime TaskManager --limit 100
```

## Files Modified
- `app/TaskManager/main.py` - Added PostgreSQL connection with SSL
- `agentcore/agentcore.json` - Added environment variables
- `agentcore/.env.local` - Contains database credentials (gitignored)
