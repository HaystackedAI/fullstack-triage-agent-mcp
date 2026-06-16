from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Task", host="0.0.0.0", stateless_http=True)

BACKEND_URL = "https://haystackedai.fastapicloud.dev"

@mcp.tool()
def list_tasks() -> str:
    """List all tasks from the database"""
    try:
        response = httpx.get(f"{BACKEND_URL}/api/tasks", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        tasks = data["tasks"]

        if not tasks:
            return "No tasks found."

        result = "Current Tasks:\n"
        for task in tasks:
            status = "✅" if task["completed"] else "⏳"
            result += f"{status} ID {task['id']}: {task['description']} (Priority: {task['priority']})\n"

        return result
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def add_task(task_description: str, priority: str = "medium") -> str:
    """Add a new task with optional priority (low, medium, high)"""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/tasks",
            json={"description": task_description, "priority": priority},
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        task = data["task"]
        return f"Task '{task_description}' added with ID {task['id']} and priority '{priority}'"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark a task as completed by its ID"""
    try:
        response = httpx.patch(
            f"{BACKEND_URL}/api/tasks/{task_id}",
            json={"completed": True},
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        task = data["task"]
        return f"Task '{task['description']}' marked as completed!"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Task with ID {task_id} not found."
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task by its ID"""
    try:
        response = httpx.delete(f"{BACKEND_URL}/api/tasks/{task_id}", timeout=5.0)
        response.raise_for_status()
        data = response.json()
        task = data["task"]
        return f"Task '{task['description']}' deleted successfully!"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Task with ID {task_id} not found."
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
