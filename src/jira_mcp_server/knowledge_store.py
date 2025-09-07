"""Knowledge store abstraction for question-to-JQL mapping."""

from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from pydantic import BaseModel


class QueryMapping(BaseModel):
    """Represents a mapping from a question pattern to JQL query."""

    question_patterns: list[str]
    jql_query: str
    description: str
    examples: list[str] | None = None


class KnowledgeStoreInterface(ABC):
    """Abstract interface for knowledge stores."""

    @abstractmethod
    def get_jql_for_question(self, question: str) -> str | None:
        """Get the appropriate JQL query for a given question.

        Args:
            question: The user's question

        Returns:
            The corresponding JQL query, or None if no match found
        """
        pass

    @abstractmethod
    def list_available_queries(self) -> list[QueryMapping]:
        """List all available query mappings.

        Returns:
            List of all query mappings in the knowledge store
        """
        pass

    @abstractmethod
    def reload(self) -> None:
        """Reload the knowledge store from its source."""
        pass


class YamlKnowledgeStore(KnowledgeStoreInterface):
    """YAML-based implementation of the knowledge store."""

    def __init__(self, file_path: str) -> None:
        """Initialize the YAML knowledge store.

        Args:
            file_path: Path to the YAML knowledge store file
        """
        self.file_path = Path(file_path)
        self._mappings: list[QueryMapping] = []
        self.reload()

    def reload(self) -> None:
        """Reload the knowledge store from the YAML file."""
        if not self.file_path.exists():
            self._mappings = []
            return

        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "queries" not in data:
                self._mappings = []
                return

            self._mappings = [QueryMapping(**mapping) for mapping in data["queries"]]
        except (yaml.YAMLError, ValueError) as e:
            raise ValueError(
                f"Failed to load knowledge store from {self.file_path}: {e}"
            ) from e

    def get_jql_for_question(self, question: str) -> str | None:
        """Get the appropriate JQL query for a given question.

        Args:
            question: The user's question

        Returns:
            The corresponding JQL query, or None if no match found
        """
        question_lower = question.lower().strip()

        for mapping in self._mappings:
            for pattern in mapping.question_patterns:
                if pattern.lower() in question_lower:
                    return mapping.jql_query

        return None

    def list_available_queries(self) -> list[QueryMapping]:
        """List all available query mappings.

        Returns:
            List of all query mappings in the knowledge store
        """
        return self._mappings.copy()


class KnowledgeStoreFactory:
    """Factory for creating knowledge store instances."""

    @staticmethod
    def create_yaml_store(file_path: str) -> YamlKnowledgeStore:
        """Create a YAML-based knowledge store.

        Args:
            file_path: Path to the YAML knowledge store file

        Returns:
            YamlKnowledgeStore instance
        """
        return YamlKnowledgeStore(file_path)

    @staticmethod
    def create_store(store_type: str, **kwargs: str) -> KnowledgeStoreInterface:
        """Create a knowledge store of the specified type.

        Args:
            store_type: Type of knowledge store to create ('yaml', etc.)
            **kwargs: Additional arguments for the knowledge store

        Returns:
            KnowledgeStoreInterface instance

        Raises:
            ValueError: If store_type is not supported
        """
        if store_type == "yaml":
            file_path = kwargs.get("file_path")
            if not file_path:
                raise ValueError("file_path is required for YAML knowledge store")
            return YamlKnowledgeStore(file_path)
        else:
            raise ValueError(f"Unsupported knowledge store type: {store_type}")
