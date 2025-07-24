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

        self.client = asana.Client.access_token(access_token)
        self.workspaces = self.client.workspaces
        self.projects = self.client.projects
        self.users = self.client.users
        self.portfolios = self.client.portfolios
        self.goals = self.client.goals
        self.teams = self.client.teams

        logger.info("Asana API client initialized.")

# Global Asana client initialization
ASANA_ACCESS_TOKEN = os.getenv("ASANA_ACCESS_TOKEN")
DEFAULT_WORKSPACE_ID = os.getenv("DEFAULT_WORKSPACE_ID")
asana_api_manager = None

if not ASANA_ACCESS_TOKEN:
    logger.error("ASANA_ACCESS_TOKEN not set.")
else:
    try:
        asana_api_manager = AsanaAPIClientManager(ASANA_ACCESS_TOKEN)
    except Exception as e:
        logger.exception(f"Failed to initialize Asana client: {e}")


@mcp.tool(title="List all the workspaces in Asana")
async def list_workspaces() -> list:
    """
    Retrieves a list of all workspaces accessible by the Asana API token.
    This tool requires no arguments.
    """
    workspaces = []
    try:
        workspaces = list(await asyncio.to_thread(asana_api_manager.workspaces.get_workspaces))
    except Exception as e:
        logger.exception("Failed to list workspaces.")
    return workspaces


@mcp.tool(title="List projects in a specific Asana workspace.")
async def list_projects(workspace_gid: str) -> list:
    """
    Retrieves a list of projects within the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list projects from.
    """
    projects = []
    try:
        projects = list(await asyncio.to_thread(
            asana_api_manager.projects.get_projects_for_workspace,
            workspace_gid,
            {"opt_fields": "gid,name"}
        ))
    except Exception as e:
        logger.exception(f"Failed to list projects for workspace {workspace_gid}.")
    return projects


@mcp.tool(title="Get a single project by ID.")
async def get_project(project_gid: str) -> dict:
    """
    Retrieves detailed information for a single Asana project.

    Args:
        project_gid (str): The Global ID (GID) of the project to retrieve details for.
    """
    project_details = {}
    try:
        project_details = await asyncio.to_thread(asana_api_manager.projects.get_project, project_gid)
    except Exception as e:
        logger.exception(f"Failed to get details for project {project_gid}.")
    return project_details

@mcp.tool(title="List portfolios in a specific Asana workspace.")
async def list_portfolios(workspace_gid: str) -> list:
    """
    Retrieves a list of portfolios within the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list portfolios from.
    """
    portfolios = []
    try:
        portfolios = await asyncio.to_thread(asana_api_manager.portfolios.get_portfolios, {"workspace": workspace_gid})
        portfolios = list(portfolios)
    except Exception as e:
        logger.exception(f"Failed to list portfolios in workspace {workspace_gid}.")
    return portfolios


@mcp.tool(title="Get details of a portfolio by ID.")
async def get_portfolio(portfolio_gid: str) -> dict:
    """
    Retrieves detailed information for a single Asana portfolio.

    Args:
        portfolio_gid (str): The Global ID (GID) of the portfolio to retrieve details for.
    """
    portfolio_details = {}
    try:
        portfolio_details = await asyncio.to_thread(asana_api_manager.portfolios.get_portfolio, portfolio_gid)
    except Exception as e:
        logger.exception(f"Failed to get details for portfolio {portfolio_gid}.")
    return portfolio_details


@mcp.tool(title="List goals in a specific Asana workspace.")
async def list_goals(workspace_gid: str) -> list:
    """
    Retrieves a list of goals within the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list goals from.
    """
    goals = []
    try:
        goals = await asyncio.to_thread(asana_api_manager.goals.get_goals, {"workspace": workspace_gid})
        goals = list(goals)
    except Exception as e:
        logger.exception(f"Failed to list goals in workspace {workspace_gid}.")
    return goals


@mcp.tool(title="Get a single goal by ID.")
async def get_goal(goal_gid: str) -> dict:
    """
    Retrieves detailed information for a single Asana goal.

    Args:
        goal_gid (str): The Global ID (GID) of the goal to retrieve details for.
    """
    goal_details = {}
    try:
        goal_details = await asyncio.to_thread(asana_api_manager.goals.get_goal, goal_gid)
    except Exception as e:
        logger.exception(f"Failed to get details for goal {goal_gid}.")
    return goal_details


@mcp.tool(title="List users in a specific Asana workspace.")
async def list_users(workspace_gid: str) -> list:
    """
    Retrieves a list of all users associated with the specified Asana workspace.

    Args:
        workspace_gid (str): The Global ID (GID) of the workspace to list users from.
    """
    users = []
    try:
        users = await asyncio.to_thread(asana_api_manager.users.get_users, workspace_gid=workspace_gid)
        users = list(users)
    except Exception as e:
        logger.exception(f"Failed to list users in workspace {workspace_gid}.")
    return users


@mcp.tool(title="Get a specific user by ID.")
async def get_user(user_gid: str) -> dict:
    """
    Retrieves detailed information for a single Asana user.

    Args:
        user_gid (str): The Global ID (GID) of the user to retrieve details for.
    """
    user_details = {}
    try:
        user_details = await asyncio.to_thread(asana_api_manager.users.get_user, user_gid)
    except Exception as e:
        logger.exception(f"Failed to get details for user {user_gid}.")
    return user_details


@mcp.tool(title="Get current authenticated user's details.")
async def get_me() -> dict:
    """
    Retrieves details for the currently authenticated Asana user (Who am I?).
    This tool requires no arguments.
    """
    me_details = {}
    try:
        me_details = await asyncio.to_thread(asana_api_manager.users.me)
    except Exception as e:
        logger.exception("Failed to get current authenticated user details.")
    return me_details


@mcp.tool(title="Get teams in an organization (workspace).")
async def get_teams_for_organization(organization_gid: str) -> list:
    """
    Retrieves a list of teams within the specified Asana organization (workspace).

    Args:
        organization_gid (str): The Global ID (GID) of the organization (workspace) to list teams from.
    """
    teams = []
    try:
        teams = await asyncio.to_thread(asana_api_manager.teams.get_teams_for_organization, organization_gid)
        teams = list(teams)
    except Exception as e:
        logger.exception(f"Failed to get teams for organization {organization_gid}.")
    return teams


@mcp.tool(title="Get a single team by ID.")
async def get_team(team_gid: str) -> dict:
    """
    Retrieves detailed information for a single Asana team.

    Args:
        team_gid (str): The Global ID (GID) of the team to retrieve details for.
    """
    team_details = {}
    try:
        team_details = await asyncio.to_thread(asana_api_manager.teams.get_team, team_gid)
    except Exception as e:
        logger.exception(f"Failed to get details for team {team_gid}.")
    return team_details
