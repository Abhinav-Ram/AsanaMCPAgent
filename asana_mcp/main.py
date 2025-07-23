import logging
import sys

from .server import mcp, asana_api_manager

logger = logging.getLogger("asana-mcp")

if __name__ == "__main__":
    if asana_api_manager:
        logger.info("Starting FastMCP server...")
        mcp.run(transport="stdio")
    else:
        logger.error("Cannot start FastMCP – Asana client is not ready.")
        sys.exit(1)
