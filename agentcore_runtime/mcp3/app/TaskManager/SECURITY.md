# Security Checklist ✅

## Credentials Storage

- ✅ **NO hardcoded credentials** in source code
- ✅ **NO credentials in git history**
- ✅ Database URL stored in `.env.local` (gitignored)
- ✅ `.env.local.example` template provided (no actual credentials)
- ✅ `test_db.py` reads from environment variable only

## Files That Should NEVER Be Committed

```
agentcore/.env.local         # Contains actual database credentials
```

## Safe to Commit

```
agentcore/.env.local.example # Template only
agentcore/agentcore.json     # References ${AIVEN_DB_URL} variable
app/TaskManager/main.py      # Reads os.getenv('DATABASE_URL')
app/TaskManager/test_db.py   # Reads os.getenv('AIVEN_DB_URL')
```

## Pre-Push Verification

Run this command before pushing to verify no credentials leaked:

```bash
# Check for hardcoded credentials
grep -r "AVNS_\|avnadmin.*pgservice" \
  --include="*.py" --include="*.json" --include="*.md" \
  --exclude="*.local" \
  agentcore_runtime/

# Should output nothing or only find this SECURITY.md file
```

## How Credentials Flow in Production

1. **Local Development**: 
   - Developer creates `agentcore/.env.local` with `AIVEN_DB_URL`
   - Never committed to git (gitignored)

2. **AgentCore Deployment**: 
   - CLI reads `AIVEN_DB_URL` from `.env.local` during deploy
   - Stores securely in AWS Secrets Manager
   - Configured in `agentcore.json` as: `"value": "${AIVEN_DB_URL}"`

3. **MCP Server Runtime**: 
   - AgentCore injects `DATABASE_URL` environment variable
   - Python code reads `os.getenv('DATABASE_URL')`
   - No hardcoded credentials anywhere

## What If Credentials Leaked?

If you accidentally committed credentials:

1. **Immediately rotate the password** in Aiven console
2. **Remove from git history**:
   ```bash
   git filter-branch --tree-filter 'rm -f path/to/file' HEAD
   # Or use git-filter-repo (recommended)
   ```
3. **Update `.env.local`** with new credentials
4. **Force push** (if repository is private and safe to do so)

## Environment Variable Names

- `AIVEN_DB_URL` - Used locally and in agentcore `.env.local`
- `DATABASE_URL` - Injected into MCP server runtime by agentcore

Both point to the same PostgreSQL connection string.
