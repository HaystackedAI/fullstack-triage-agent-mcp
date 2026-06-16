# Task Manager MCP Server - PostgreSQL Setup

## ✅ What's Been Configured

This Task Manager now uses **Aiven PostgreSQL** for persistent storage instead of file-based JSON.

### Changes Made:

1. **Database Connection**
   - Using `asyncpg` for async PostgreSQL connections
   - Connection pool configured (min: 1, max: 10)
   - Connection string stored securely in `.env.local`

2. **Database Schema**
   ```sql
   CREATE TABLE tasks (
       id SERIAL PRIMARY KEY,
       description TEXT NOT NULL,
       priority TEXT NOT NULL DEFAULT 'medium',
       completed BOOLEAN NOT NULL DEFAULT FALSE,
       created_at TIMESTAMP NOT NULL DEFAULT NOW()
   )
   ```

3. **Environment Configuration**
   - `agentcore/agentcore.json`: Added `envVars` with `DATABASE_URL=${AIVEN_DB_URL}`
   - `agentcore/.env.local`: Contains `AIVEN_DB_URL` (gitignored)
   - No need for `credentials` section - just using environment variables

4. **CRUD Operations**
   - All operations now use async PostgreSQL queries
   - Lazy database initialization on first tool call
   - Auto-creates table if it doesn't exist

## 🔧 Local Testing

Before deploying to agentcore, test the database connection:

```bash
cd agentcore_runtime/mcp3/app/TaskManager
python test_db.py
```

This will:
- Connect to Aiven PostgreSQL
- Create the `tasks` table
- Insert a test task
- Verify data retrieval

## 🚀 Deployment

Validate and deploy to AgentCore runtime:

```bash
cd agentcore_runtime/mcp3/agentcore

# First, validate the configuration
agentcore validate

# If valid, deploy
agentcore deploy
```

The environment variables will be automatically injected from `.env.local` during deployment. AgentCore will:
1. Read `AIVEN_DB_URL` from `.env.local`
2. Store it securely in AWS Secrets Manager
3. Inject it as `DATABASE_URL` into the MCP server runtime

## 🔐 Security Notes

- ✅ `.env.local` is gitignored (never committed)
- ✅ Connection uses SSL (Aiven default)
- ✅ Credentials stored in AWS Secrets Manager when deployed
- ✅ Database password not exposed in code

## 📊 Database Info

- **Provider**: Aiven
- **Host**: `<your-aiven-host>:26061`
- **Database**: `agentcoredb`
- **User**: `<configured in .env.local>`
- **Connection**: SSL enabled (default)

## 🔍 How CRUD Works in AgentCore Runtime

```
Claude Code (Client)
    ↓ MCP Protocol
TaskManager MCP Server (AgentCore Runtime)
    ↓ asyncpg connection pool
PostgreSQL Database (Aiven Cloud)
```

All CRUD operations happen **inside the MCP server** running in agentcore runtime. The database connection persists across MCP tool calls within the same session.

## 📝 Available MCP Tools

1. `add_task(task_description, priority="medium")` - Creates a new task
2. `list_tasks()` - Lists all tasks with status
3. `complete_task(task_id)` - Marks task as completed
4. `delete_task(task_id)` - Deletes a task

## 🐛 Troubleshooting

**Connection errors:**
- Verify `AIVEN_DB_URL` in `.env.local` is correct
- Check Aiven firewall allows connections from agentcore IPs
- Ensure SSL is enabled (Aiven requires it)

**Table not found:**
- The table auto-creates on first tool call
- If issues persist, run `test_db.py` to manually create it

**Environment variable not found:**
- Verify `agentcore.json` has `envVars` configured
- Check `.env.local` exists in `agentcore/` directory
- Redeploy with `agentcore deploy`
