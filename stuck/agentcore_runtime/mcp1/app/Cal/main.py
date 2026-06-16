from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator Server", host="0.0.0.0", stateless_http=True)


@mcp.tool(description="Add two numbers together")
def add(x: float, y: float) -> float:
    """Add two numbers and return the result."""
    return x + y

@mcp.tool(description="Subtract second number from first number")
def subtract(x: float, y: float) -> float:
    """Subtract y from x and return the result."""
    return x - y

@mcp.tool(description="Multiply two numbers together")
def multiply(x: float, y: float) -> float:
    """Multiply two numbers and return the result."""
    return x * y

@mcp.tool(description="Divide first number by second number")
def divide(x: float, y: float) -> float:
    """Divide x by y and return the result."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

    
@mcp.tool(description="Greet a user by name")
def greet_user(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}! Nice to meet you."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
