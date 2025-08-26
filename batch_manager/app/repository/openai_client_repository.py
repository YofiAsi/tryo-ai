
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.entity.openai_client_entity import OpenAiClient, OpenAiClientStatus
from app.consts.ai_models import AIModel
from app.errors.business_exception import BusinessException, ErrorCodes

_log = logging.getLogger(__name__)


class OpenAiClientRepository:
    """
    OpenAiClient Repository class

    This class is responsible for handling all the database operations related to the OpenAiClient entity.
    OpenAiClient entity is a beanie document model and all the operations are performed using the beanie library.
    """

    def __init__(self) -> None:
        _log.debug("OpenAiClientRepository Connecting to database")

    async def create(self, openai_client: OpenAiClient) -> OpenAiClient:
        _log.debug(f"OpenAiClientRepository Creating openai_client: {openai_client.name}")
        await OpenAiClient.insert(openai_client)
        _log.debug("OpenAiClientRepository OpenAiClient created")
        return openai_client

    async def bulk_create(self, openai_clients: List[OpenAiClient]) -> List[OpenAiClient]:
        """
        Create multiple openai_clients in a single database operation.
        
        Args:
            openai_clients: List of OpenAiClient entities to create
            
        Returns:
            List of created OpenAiClient entities with assigned IDs
            
        Raises:
            BusinessException: If bulk creation fails
        """
        if not openai_clients:
            _log.warning("OpenAiClientRepository No openai_clients to create")
            return []
        
        _log.debug(f"OpenAiClientRepository Creating {len(openai_clients)} openai_clients in bulk")
        
        try:
            # Use Beanie's insert_many for bulk insertion
            await OpenAiClient.insert_many(openai_clients)
            _log.info(f"OpenAiClientRepository Successfully created {len(openai_clients)} openai_clients")
            return openai_clients
        except Exception as e:
            _log.error(f"OpenAiClientRepository Failed to bulk create openai_clients: {str(e)}")
            raise BusinessException(ErrorCodes.INTERNAL_SERVER_ERROR, f"Failed to create openai_clients: {str(e)}")

    async def update(self, openai_client: OpenAiClient) -> OpenAiClient:
        _log.debug(f"OpenAiClientRepository Updating openai_client: {openai_client.name}")
        if openai_client.id is None:
            raise BusinessException(ErrorCodes.INVALID_PAYLOAD, "OpenAiClient id is required for update")
        await openai_client.replace()
        _log.debug("OpenAiClientRepository OpenAiClient updated")
        return openai_client

    async def delete(self, id: PydanticObjectId) -> None:
        _log.debug(f"OpenAiClientRepository Deleting openai_client: {id}")
        result = await OpenAiClient.find_one({"_id": id})
        if not result:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"OpenAiClient not found: {id}")

        await result.delete()
        _log.debug("OpenAiClientRepository OpenAiClient deleted")

    async def find_all(self) -> List[OpenAiClient]:
        """
        Retrieve all OpenAI clients
        
        Returns:
            List of all OpenAiClient entities
        """
        _log.debug("OpenAiClientRepository Finding all openai_clients")
        clients = await OpenAiClient.find_all().to_list()
        _log.debug(f"OpenAiClientRepository Found {len(clients)} openai_clients")
        return clients

    async def count(self, query: dict[str, Any]) -> int:
        _log.debug(f"OpenAiClientRepository Counting openai_clients with query: {query}")
        doc = OpenAiClient.find(query)
        result = await doc.count()
        _log.debug("OpenAiClientRepository OpenAiClients counted")
        return result

    async def retrieve(self, id: PydanticObjectId) -> OpenAiClient:
        _log.debug(f"OpenAiClientRepository Retrieving openai_client: {id}")
        doc = await OpenAiClient.find_one({"_id": id})
        if not doc:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"OpenAiClient not found: {id}")
        _log.debug("OpenAiClientRepository OpenAiClient retrieved")
        return doc

    async def retrieve_by_name(self, name: str) -> Optional[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Retrieving openai_client by name: {name}")
        doc = await OpenAiClient.find_one({"name": name})
        _log.debug("OpenAiClientRepository OpenAiClient retrieved by name")
        return doc

    async def retrieve_by_names(self, names: List[str]) -> List[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Retrieving openai_clients by names: {names}")
        doc = await OpenAiClient.find({"name": {"$in": names}}).to_list()
        _log.debug(f"OpenAiClientRepository Found {len(doc)} openai_clients by names")
        return doc

    async def find_by_status(self, status: OpenAiClientStatus) -> List[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Finding openai_clients by status: {status}")
        query = {"status": status.value}
        clients = await OpenAiClient.find(query).to_list()
        _log.debug(f"OpenAiClientRepository Found {len(clients)} openai_clients by status")
        return clients

    async def find_active_clients(self) -> List[OpenAiClient]:
        """
        Find all active OpenAI clients
        
        Returns:
            List of active OpenAiClient entities
        """
        _log.debug("OpenAiClientRepository Finding active openai_clients")
        return await self.find_by_status(OpenAiClientStatus.ACTIVE)

    async def find_by_organization(self, organization: str) -> List[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Finding openai_clients by organization: {organization}")
        query = {"organization": organization}
        clients = await OpenAiClient.find(query).to_list()
        _log.debug(f"OpenAiClientRepository Found {len(clients)} openai_clients by organization")
        return clients

    async def find_by_project(self, project: str) -> List[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Finding openai_clients by project: {project}")
        query = {"project": project}
        clients = await OpenAiClient.find(query).to_list()
        _log.debug(f"OpenAiClientRepository Found {len(clients)} openai_clients by project")
        return clients

    async def find_clients_with_capacity(self, model: AIModel, tokens: int) -> List[OpenAiClient]:
        """
        Find active clients that can handle the specified token count for the given model
        
        Args:
            model: The AI model to check capacity for
            tokens: Number of tokens needed
            
        Returns:
            List of OpenAiClient entities that can handle the request
        """
        _log.debug(f"OpenAiClientRepository Finding clients with capacity for {tokens} tokens of {model}")
        
        # Get all active clients
        active_clients = await self.find_active_clients()
        
        # Filter clients that can handle the request
        capable_clients = [client for client in active_clients if client.can_use(tokens, model)]
        
        _log.debug(f"OpenAiClientRepository Found {len(capable_clients)} capable clients")
        return capable_clients

    async def update_client_status(self, client_id: PydanticObjectId, status: OpenAiClientStatus) -> OpenAiClient:
        _log.debug(f"OpenAiClientRepository Updating client status: {client_id} -> {status}")
        client = await self.retrieve(client_id)
        client.status = status
        await client.replace()
        _log.debug("OpenAiClientRepository Client status updated")
        return client

    async def update_model_usage(self, client_id: PydanticObjectId, model: AIModel, tokens: int) -> OpenAiClient:
        """
        Update the model usage for a specific client
        
        Args:
            client_id: UUID of the client
            model: The AI model that was used
            tokens: Number of tokens to add to usage
            
        Returns:
            Updated OpenAiClient entity
        """
        _log.debug(f"OpenAiClientRepository Updating model usage for client {client_id}: {model} +{tokens} tokens")
        client = await self.retrieve(client_id)
        client.register_usage(model, tokens)
        await client.replace()
        _log.debug("OpenAiClientRepository Model usage updated")
        return client

    async def reset_daily_usage(self, client_name: str) -> None:
        _log.debug(f"OpenAiClientRepository Resetting daily usage for client {client_name}")
        client: Optional[OpenAiClient] = await self.retrieve_by_name(client_name)
        if client is None:
            raise BusinessException(ErrorCodes.NOT_FOUND, f"OpenAiClient not found: {client_name}")
        client.model_usage = {model: 0 for model in AIModel}
        client.last_reset_at = datetime.now(timezone.utc)
        await client.replace()
        _log.debug("OpenAiClientRepository Daily usage reset")

    async def bulk_reset_daily_usage(self, client_names: List[str]) -> int:
        """
        Reset daily usage for all clients (typically called daily via cron job)
        
        Returns:
            Number of clients updated
        """
        _log.debug("OpenAiClientRepository Bulk resetting daily usage for all clients")
        
        # Get all clients
        all_clients = await self.retrieve_by_names(client_names)
        updated_count = 0
        
        for client in all_clients:
            client.model_usage = {model: 0 for model in AIModel}
            client.last_reset_at = datetime.now(timezone.utc)
            await client.replace()
            updated_count += 1
        
        _log.info(f"OpenAiClientRepository Reset daily usage for {updated_count} clients")
        return updated_count

    async def find_clients_created_after(self, after_date: datetime) -> List[OpenAiClient]:
        _log.debug(f"OpenAiClientRepository Finding clients created after: {after_date}")
        query = {"created_at": {"$gte": after_date}}
        clients = await OpenAiClient.find(query).to_list()
        _log.debug(f"OpenAiClientRepository Found {len(clients)} clients by creation date")
        return clients

    async def count_by_status(self, status: OpenAiClientStatus) -> int:
        _log.debug(f"OpenAiClientRepository Counting clients by status: {status}")
        query = {"status": status.value}
        result = await OpenAiClient.find(query).count()
        _log.debug("OpenAiClientRepository Clients counted by status")
        return result

    async def get_usage_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get a summary of usage across all clients by model
        
        Returns:
            Dictionary with client names as keys and model usage as values
        """
        _log.debug("OpenAiClientRepository Getting usage summary")
        
        all_clients = await self.find_all()
        usage_summary = {}
        
        for client in all_clients:
            usage_summary[client.name] = {
                model.value: usage for model, usage in client.model_usage.items()
            }
        
        _log.debug("OpenAiClientRepository Usage summary generated")
        return usage_summary
