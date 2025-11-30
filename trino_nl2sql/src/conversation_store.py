"""
Conversation storage abstraction with optional Azure Cosmos DB persistence.
Falls back to an in-memory dict when Cosmos configuration or dependency
is unavailable so the API keeps working in all environments.
"""
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Optional dependency: azure-cosmos
try:
    from azure.cosmos import CosmosClient, PartitionKey, exceptions as cosmos_exceptions
except ImportError:  # pragma: no cover - handled gracefully at runtime
    CosmosClient = None  # type: ignore
    PartitionKey = None  # type: ignore
    cosmos_exceptions = None  # type: ignore


class ConversationStore:
    """Store conversations with optional Cosmos DB persistence."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self.storage_backend = "memory"
        self.container = None
        self._init_cosmos()

    def _init_cosmos(self):
        """Initialize Cosmos DB client if configuration and dependency are present."""
        endpoint = os.environ.get("COSMOS_ENDPOINT")
        key = os.environ.get("COSMOS_KEY")
        database_name = os.environ.get("COSMOS_DATABASE", "trino-nl2sql")
        container_name = os.environ.get("COSMOS_CONTAINER", "conversations")

        if not endpoint or not key:
            self.logger.info("COSMOS_ENDPOINT/KEY not set; using in-memory conversation store.")
            return

        if CosmosClient is None or PartitionKey is None:
            self.logger.warning("azure-cosmos not installed; using in-memory conversation store.")
            return

        try:
            client = CosmosClient(endpoint, credential=key)
            database = client.create_database_if_not_exists(id=database_name)
            container = database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path="/conversation_id"),
                offer_throughput=400,
            )
            self.container = container
            self.storage_backend = "cosmos"
            self.logger.info(
                "Conversation store initialized with Cosmos DB database=%s container=%s",
                database_name,
                container_name,
            )
        except Exception as exc:  # pragma: no cover - external service handling
            self.logger.warning(
                "Failed to initialize Cosmos DB conversation store (%s); falling back to memory.",
                exc,
            )
            self.container = None
            self.storage_backend = "memory"

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _blank_record(self, conversation_id: str, topic: Optional[str] = None) -> Dict[str, Any]:
        return {
            "id": conversation_id,
            "conversation_id": conversation_id,
            "topic": topic or "New conversation",
            "created_at": self._timestamp(),
            "updated_at": self._timestamp(),
            "messages": [],
        }

    def create_conversation(self, topic: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        conversation_id = str(uuid.uuid4())
        record = self._blank_record(conversation_id, topic)

        if self.storage_backend == "cosmos" and self.container:
            try:
                self.container.upsert_item(record)
            except Exception as exc:  # pragma: no cover
                self.logger.warning("Failed to persist new conversation to Cosmos: %s", exc)
                self.storage_backend = "memory"
                self.memory_store[conversation_id] = record
        else:
            self.memory_store[conversation_id] = record

        return conversation_id

    def append_message(
        self,
        conversation_id: str,
        *,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Add a message to a conversation. Creates the conversation if missing."""
        if not conversation_id:
            return

        metadata = metadata or {}
        message = {
            "role": role,
            "content": content,
            "metadata": metadata,
            "timestamp": self._timestamp(),
        }

        if self.storage_backend == "cosmos" and self.container:
            try:
                try:
                    doc = self.container.read_item(
                        item=conversation_id, partition_key=conversation_id
                    )
                except Exception as read_exc:
                    # Create if not found
                    if cosmos_exceptions and isinstance(
                        read_exc, cosmos_exceptions.CosmosResourceNotFoundError
                    ):
                        doc = self._blank_record(conversation_id)
                    else:
                        raise

                doc["messages"].append(message)
                doc["updated_at"] = self._timestamp()
                self.container.upsert_item(doc)
                return
            except Exception as exc:  # pragma: no cover
                self.logger.warning(
                    "Failed to append message to Cosmos store; falling back to memory. Error: %s",
                    exc,
                )
                self.storage_backend = "memory"

        record = self.memory_store.get(conversation_id) or self._blank_record(conversation_id)
        record["messages"].append(message)
        record["updated_at"] = self._timestamp()
        self.memory_store[conversation_id] = record

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation record if available."""
        if not conversation_id:
            return None

        if self.storage_backend == "cosmos" and self.container:
            try:
                return self.container.read_item(
                    item=conversation_id, partition_key=conversation_id
                )
            except Exception:  # pragma: no cover - best-effort read
                return None

        return self.memory_store.get(conversation_id)

