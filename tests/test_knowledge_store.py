"""Tests for knowledge store functionality."""

import tempfile
from pathlib import Path

import pytest
import yaml

from jira_mcp_server.knowledge_store import (
    KnowledgeStoreFactory,
    QueryMapping,
    YamlKnowledgeStore,
)


class TestQueryMapping:
    """Test suite for QueryMapping model."""

    def test_valid_query_mapping(self) -> None:
        """Test valid query mapping creation."""
        mapping = QueryMapping(
            question_patterns=["test pattern"],
            jql_query="project = TEST",
            description="Test mapping",
            examples=["example 1"],
        )

        assert mapping.question_patterns == ["test pattern"]
        assert mapping.jql_query == "project = TEST"
        assert mapping.description == "Test mapping"
        assert mapping.examples == ["example 1"]

    def test_query_mapping_without_examples(self) -> None:
        """Test query mapping without examples."""
        mapping = QueryMapping(
            question_patterns=["test pattern"],
            jql_query="project = TEST",
            description="Test mapping",
        )

        assert mapping.examples is None


class TestYamlKnowledgeStore:
    """Test suite for YamlKnowledgeStore."""

    def test_load_valid_yaml(self) -> None:
        """Test loading valid YAML knowledge store."""
        data = {
            "queries": [
                {
                    "question_patterns": ["open bugs", "active bugs"],
                    "jql_query": "type = Bug AND status != Done",
                    "description": "Find open bugs",
                    "examples": ["Show me open bugs"],
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            store = YamlKnowledgeStore(temp_path)
            mappings = store.list_available_queries()

            assert len(mappings) == 1
            assert mappings[0].question_patterns == ["open bugs", "active bugs"]
            assert mappings[0].jql_query == "type = Bug AND status != Done"
            assert mappings[0].description == "Find open bugs"
        finally:
            Path(temp_path).unlink()

    def test_load_empty_file(self) -> None:
        """Test loading empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            store = YamlKnowledgeStore(temp_path)
            mappings = store.list_available_queries()
            assert len(mappings) == 0
        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading non-existent file."""
        store = YamlKnowledgeStore("/non/existent/path.yaml")
        mappings = store.list_available_queries()
        assert len(mappings) == 0

    def test_load_invalid_yaml(self) -> None:
        """Test loading invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Failed to load knowledge store"):
                YamlKnowledgeStore(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_get_jql_for_question_found(self) -> None:
        """Test getting JQL for a matched question."""
        data = {
            "queries": [
                {
                    "question_patterns": ["open bugs", "active bugs"],
                    "jql_query": "type = Bug AND status != Done",
                    "description": "Find open bugs",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            store = YamlKnowledgeStore(temp_path)

            # Test exact match
            jql = store.get_jql_for_question("show me open bugs")
            assert jql == "type = Bug AND status != Done"

            # Test partial match
            jql = store.get_jql_for_question("I need to see active bugs")
            assert jql == "type = Bug AND status != Done"

            # Test case insensitive
            jql = store.get_jql_for_question("OPEN BUGS")
            assert jql == "type = Bug AND status != Done"
        finally:
            Path(temp_path).unlink()

    def test_get_jql_for_question_not_found(self) -> None:
        """Test getting JQL for a question that doesn't match."""
        data = {
            "queries": [
                {
                    "question_patterns": ["open bugs"],
                    "jql_query": "type = Bug AND status != Done",
                    "description": "Find open bugs",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            store = YamlKnowledgeStore(temp_path)
            jql = store.get_jql_for_question("closed issues")
            assert jql is None
        finally:
            Path(temp_path).unlink()

    def test_reload(self) -> None:
        """Test reloading the knowledge store."""
        data = {
            "queries": [
                {
                    "question_patterns": ["test"],
                    "jql_query": "project = TEST",
                    "description": "Test query",
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            store = YamlKnowledgeStore(temp_path)
            assert len(store.list_available_queries()) == 1

            # Update the file
            data["queries"].append(
                {
                    "question_patterns": ["new test"],
                    "jql_query": "project = NEW",
                    "description": "New test query",
                }
            )

            with open(temp_path, "w") as f:
                yaml.dump(data, f)

            # Reload and check
            store.reload()
            assert len(store.list_available_queries()) == 2
        finally:
            Path(temp_path).unlink()


class TestKnowledgeStoreFactory:
    """Test suite for KnowledgeStoreFactory."""

    def test_create_yaml_store(self) -> None:
        """Test creating YAML knowledge store."""
        store = KnowledgeStoreFactory.create_yaml_store("test.yaml")
        assert isinstance(store, YamlKnowledgeStore)

    def test_create_store_yaml(self) -> None:
        """Test creating store with yaml type."""
        store = KnowledgeStoreFactory.create_store("yaml", file_path="test.yaml")
        assert isinstance(store, YamlKnowledgeStore)

    def test_create_store_invalid_type(self) -> None:
        """Test creating store with invalid type."""
        with pytest.raises(ValueError, match="Unsupported knowledge store type"):
            KnowledgeStoreFactory.create_store("invalid")

    def test_create_store_missing_file_path(self) -> None:
        """Test creating YAML store without file_path."""
        with pytest.raises(ValueError, match="file_path is required"):
            KnowledgeStoreFactory.create_store("yaml")
