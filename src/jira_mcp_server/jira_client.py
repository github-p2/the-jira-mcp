"""JIRA API client for executing JQL queries and managing JIRA operations."""

from typing import Any

import structlog
from jira import JIRA
from jira.exceptions import JIRAError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import JiraConfig

logger = structlog.get_logger(__name__)


class JiraClient:
    """Client for interacting with JIRA API."""

    def __init__(self, config: JiraConfig) -> None:
        """Initialize the JIRA client.

        Args:
            config: JIRA configuration containing URL and authentication details
        """
        self.config = config
        self._client: JIRA | None = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the JIRA client with authentication."""
        try:
            # Try different authentication methods based on configuration
            if self.config.username:
                try:
                    # First try Bearer token authentication (for corporate JIRA)
                    logger.info("Attempting Bearer token authentication")
                    self._client = JIRA(
                        server=self.config.url,
                        token_auth=self.config.token,
                    )
                except Exception:
                    # Fallback to basic auth with username
                    logger.info("Bearer auth failed, trying basic auth")
                    self._client = JIRA(
                        server=self.config.url,
                        basic_auth=(self.config.username, self.config.token),
                    )
            else:
                # Use token auth without username
                self._client = JIRA(
                    server=self.config.url, token_auth=self.config.token
                )
            logger.info("JIRA client initialized successfully", url=self.config.url)

        except Exception as e:
            logger.error(
                "Failed to initialize JIRA client", error=str(e), url=self.config.url
            )
            raise

    @property
    def client(self) -> JIRA:
        """Get the JIRA client instance.

        Returns:
            The JIRA client instance

        Raises:
            RuntimeError: If client is not initialized
        """
        if self._client is None:
            raise RuntimeError("JIRA client is not initialized")
        return self._client

    def test_connection(self) -> bool:
        """Test the connection to JIRA.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get server info as a simple connectivity test
            info = self.client.server_info()
            logger.info(
                "JIRA connection test successful", server_version=info.get("version")
            )
            return True
        except Exception as e:
            logger.error("JIRA connection test failed", error=str(e))
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(JIRAError),
    )
    def execute_jql(
        self,
        jql_query: str,
        max_results: int = 50,
        expand: str | None = None,
    ) -> dict[str, Any]:
        """Execute a JQL query and return results.

        Args:
            jql_query: The JQL query string to execute
            max_results: Maximum number of results to return
            expand: Optional fields to expand in the response

        Returns:
            Dictionary containing query results and metadata

        Raises:
            JIRAError: If the JQL query fails
        """
        try:
            logger.info("Executing JQL query", jql=jql_query, max_results=max_results)

            # Execute the search
            issues = self.client.search_issues(
                jql_str=jql_query,
                maxResults=max_results,
                expand=expand,
            )

            # Convert issues to serializable format
            results = []
            for issue in issues:
                issue_data = {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": getattr(issue.fields.assignee, "displayName", None)
                    if issue.fields.assignee
                    else None,
                    "reporter": getattr(issue.fields.reporter, "displayName", None)
                    if issue.fields.reporter
                    else None,
                    "created": issue.fields.created,
                    "updated": issue.fields.updated,
                    "priority": getattr(issue.fields.priority, "name", None)
                    if issue.fields.priority
                    else None,
                    "issuetype": issue.fields.issuetype.name,
                    "project": issue.fields.project.key,
                }

                # Add description if available
                if hasattr(issue.fields, "description") and issue.fields.description:
                    issue_data["description"] = issue.fields.description

                results.append(issue_data)

            response_data = {
                "jql": jql_query,
                "total": len(results),
                "max_results": max_results,
                "issues": results,
            }

            logger.info(
                "JQL query executed successfully",
                jql=jql_query,
                total_results=len(results),
            )

            return response_data

        except JIRAError as e:
            logger.error("JQL query failed", jql=jql_query, error=str(e))
            raise
        except Exception as e:
            logger.error("Unexpected error executing JQL", jql=jql_query, error=str(e))
            raise JIRAError(f"Unexpected error: {str(e)}") from e

    def get_projects(self) -> list[dict[str, Any]]:
        """Get list of available projects.

        Returns:
            List of project information dictionaries
        """
        try:
            projects = self.client.projects()
            return [
                {
                    "key": project.key,
                    "name": project.name,
                    "description": getattr(project, "description", ""),
                    "lead": getattr(project.lead, "displayName", None)
                    if hasattr(project, "lead") and project.lead
                    else None,
                }
                for project in projects
            ]
        except Exception as e:
            logger.error("Failed to get projects", error=str(e))
            raise

    def get_issue_types(self) -> list[dict[str, Any]]:
        """Get list of available issue types.

        Returns:
            List of issue type information dictionaries
        """
        try:
            issue_types = self.client.issue_types()
            return [
                {
                    "id": issue_type.id,
                    "name": issue_type.name,
                    "description": getattr(issue_type, "description", ""),
                }
                for issue_type in issue_types
            ]
        except Exception as e:
            logger.error("Failed to get issue types", error=str(e))
            raise
