import asyncio
import logging
import os

import asana
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("asana-mcp")

mcp = FastMCP("asana-mcp")

class AsanaAPIClientManager:
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("ASANA_ACCESS_TOKEN must be provided.")

        # Using asana.Client.access_token is correct for initializing with PAT
        self.client = asana.Client.access_token(access_token)
        self.workspaces = self.client.workspaces
        self.projects = self.client.projects
        self.tasks = self.client.tasks
        self.users = self.client.users # Added users API client

        logger.info("Asana API client initialized.")

# Global Asana client initialization
ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN")
asana_api_manager = None

if not ASANA_ACCESS_TOKEN:
    logger.error("ASANA_ACCESS_TOKEN not set.")
else:
    try:
        asana_api_manager = AsanaAPIClientManager(ASANA_ACCESS_TOKEN)
    except Exception as e: # Catch specific exception for better logging
        logger.exception(f"Failed to initialize Asana client: {e}")


@mcp.tool(title="List all the workspaces in Asana")
async def list_workspaces() -> list:
    """
    Retrieves a list of all workspaces accessible by the Asana API token.
    This tool requires no arguments.
    """
    if not asana_api_manager:
        return [{"error": "Asana client not initialized. ASANA_ACCESS_TOKEN might be missing or invalid."}]
    try:
        # get_workspaces is the correct method for Asana's WorkspacesApi
        return list(await asyncio.to_thread(asana_api_manager.workspaces.get_workspaces))
    except Exception as e:
        logger.exception("Failed to list workspaces.")
        return [{"error": str(e)}]


@mcp.tool(title="List projects in a specific Asana workspace.")
async def list_projects(workspace_gid: str) -> list:
    """
    Retrieves a list of projects within the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list projects from.
    """
    if not asana_api_manager:
        return [{"error": "Asana client not initialized. ASANA_ACCESS_TOKEN might be missing or invalid."}]
    try:
        # Using get_projects_for_workspace is the correct method
        # Added opt_fields to explicitly request gid and name
        return list(await asyncio.to_thread(
            asana_api_manager.projects.get_projects_for_workspace, # Corrected method name
            workspace_gid,
            {"opt_fields": "gid,name"}
        ))
    except Exception as e:
        logger.exception(f"Failed to list projects for workspace {workspace_gid}.")
        return [{"error": str(e)}]


@mcp.tool(title="List tasks within a specific Asana project.")
async def list_tasks(project_gid: str) -> list: # Changed to accept project_gid
    """
    Retrieves a list of tasks from the specified Asana project.

    Args:
        project_gid (str): The Global ID (GID) of the project to list tasks from.
    """
    if not asana_api_manager:
        return [{"error": "Asana client not initialized. ASANA_ACCESS_TOKEN might be missing or invalid."}]
    try:
        # get_tasks_for_project is the correct method
        return list(await asyncio.to_thread(
            asana_api_manager.tasks.get_tasks_for_project,
            project_gid,
            {"opt_fields": "gid,name,completed,due_on,assignee.name"}
        ))
    except Exception as e:
        logger.exception(f"Failed to list tasks for project {project_gid}.")
        return [{"error": str(e)}]


@mcp.tool(title="Get detailed information for a specific Asana task.")
async def get_task_details(task_gid: str) -> dict: # Changed to accept task_gid
    """
    Retrieves comprehensive details for a single Asana task.

    Args:
        task_gid (str): The Global ID (GID) of the task to retrieve details for.
    """
    if not asana_api_manager:
        return {"error": "Asana client not initialized. ASANA_ACCESS_TOKEN might be missing or invalid."}
    try:
        # get_task is the correct method for TasksApi
        task_details = await asyncio.to_thread(asana_api_manager.tasks.get_task, task_gid)
        return task_details # This should already be a dict
    except Exception as e:
        logger.exception(f"Failed to get details for task {task_gid}.")
        return {"error": str(e)}


@mcp.tool(title="List all users in a specific Asana workspace.")
async def list_users_in_workspace(workspace_gid: str) -> list:
    """
    Retrieves a list of all users associated with the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list users from.
    """
    if not asana_api_manager:
        return [{"error": "Asana client not initialized. ASANA_ACCESS_TOKEN might be missing or invalid."}]
    try:
        # The Asana client's UsersApi has a get_users method that can be filtered by workspace
        users = await asyncio.to_thread(asana_api_manager.users.get_users, workspace_gid=workspace_gid)
        return list(users)
    except Exception as e:
        logger.exception(f"Failed to list users in workspace {workspace_gid}.")
        return [{"error": str(e)}]

