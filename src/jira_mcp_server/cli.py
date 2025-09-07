"""Command line interface for JIRA MCP Server."""

import asyncio
import sys

import click
import structlog
from structlog.stdlib import LoggerFactory

from .config import Config
from .mcp_server import JiraMCPServer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@click.group()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set the logging level",
)
@click.pass_context
def cli(ctx: click.Context, log_level: str) -> None:
    """JIRA MCP Server - Model Context Protocol server for JIRA integration."""
    # Set up logging level
    import logging

    logging.basicConfig(level=getattr(logging, log_level))

    # Store log level in context
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level


@cli.command()
@click.option(
    "--knowledge-store",
    default="knowledge_store.yaml",
    help="Path to the knowledge store YAML file",
)
@click.pass_context
def stdio(ctx: click.Context, knowledge_store: str) -> None:
    """Run the server in STDIO mode for MCP client integration."""

    async def run_server() -> None:
        try:
            # Load configuration
            config = Config.from_env()
            config.server.knowledge_store_path = knowledge_store
            config.server.log_level = ctx.obj["log_level"]

            # Create and run server
            server = JiraMCPServer(config)
            await server.run_stdio()

        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error("Server error", error=str(e))
            sys.exit(1)

    # Run the async server
    asyncio.run(run_server())


@cli.command()
@click.pass_context
def test_connection(ctx: click.Context) -> None:
    """Test the JIRA connection configuration."""

    async def test() -> None:
        try:
            config = Config.from_env()
            from .jira_client import JiraClient

            client = JiraClient(config.jira)

            click.echo("Testing JIRA connection...")
            if client.test_connection():
                click.echo("✅ JIRA connection successful!")

                # Get some basic info
                projects = client.get_projects()
                click.echo(f"Found {len(projects)} projects")

                if projects:
                    click.echo("\nSample projects:")
                    for project in projects[:3]:
                        click.echo(f"  - {project['key']}: {project['name']}")

            else:
                click.echo("❌ JIRA connection failed!")
                sys.exit(1)

        except Exception as e:
            click.echo(f"❌ Error testing connection: {str(e)}")
            sys.exit(1)

    asyncio.run(test())


@cli.command()
@click.option(
    "--knowledge-store",
    default="knowledge_store.yaml",
    help="Path to the knowledge store YAML file",
)
def validate_knowledge_store(knowledge_store: str) -> None:
    """Validate the knowledge store configuration."""
    try:
        from .knowledge_store import KnowledgeStoreFactory

        click.echo(f"Validating knowledge store: {knowledge_store}")

        store = KnowledgeStoreFactory.create_store("yaml", file_path=knowledge_store)
        mappings = store.list_available_queries()

        if not mappings:
            click.echo("⚠️  Knowledge store is empty or file not found")
            return

        click.echo(
            f"✅ Knowledge store loaded successfully with {len(mappings)} query mappings"
        )

        click.echo("\nAvailable query mappings:")
        for i, mapping in enumerate(mappings, 1):
            click.echo(f"{i}. {mapping.description}")
            click.echo(f"   Patterns: {', '.join(mapping.question_patterns)}")
            click.echo(f"   JQL: {mapping.jql_query}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Error validating knowledge store: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()
