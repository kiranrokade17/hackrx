import os
import logging
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DatabaseService:
    """MongoDB database service for storing query results and metadata"""
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.database_name = os.getenv("MONGODB_DATABASE", "llm_query_system")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        # Collection names
        self.queries_collection = "queries"
        self.documents_collection = "documents"
        self.metadata_collection = "metadata"
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    async def store_query_result(self, query_data: Dict[str, Any]) -> str:
        """
        Store query result in database
        """
        try:
            if self.db is None:
                raise Exception("Database not connected")
                
            query_id = str(uuid.uuid4())
            
            query_record = {
                "_id": query_id,
                "query_id": query_id,
                "document_url": query_data.get("document_url"),
                "questions": query_data.get("questions", []),
                "answers": query_data.get("answers", []),
                "document_id": query_data.get("document_id"),
                "api_key_used": query_data.get("api_key_used"),
                "processed_at": datetime.utcnow(),
                "processing_time_ms": query_data.get("processing_time_ms"),
                "status": "completed"
            }
            
            collection = self.db[self.queries_collection]
            await collection.insert_one(query_record)
            
            logger.info(f"Stored query result with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Error storing query result: {str(e)}")
            raise Exception(f"Failed to store query result: {str(e)}")
    
    async def store_document_metadata(self, document_data: Dict[str, Any]) -> str:
        """
        Store document metadata
        """
        try:
            document_id = document_data.get("document_id") or str(uuid.uuid4())
            
            document_record = {
                "_id": document_id,
                "document_id": document_id,
                "url": document_data.get("url"),
                "title": document_data.get("title"),
                "file_type": document_data.get("file_type"),
                "size_bytes": document_data.get("size_bytes"),
                "chunk_count": document_data.get("chunk_count", 0),
                "processed_at": datetime.utcnow(),
                "status": document_data.get("status", "processed"),
                "metadata": document_data.get("metadata", {})
            }
            
            collection = self.db[self.documents_collection]
            await collection.replace_one(
                {"_id": document_id}, 
                document_record, 
                upsert=True
            )
            
            logger.info(f"Stored document metadata with ID: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"Error storing document metadata: {str(e)}")
            raise Exception(f"Failed to store document metadata: {str(e)}")
    
    async def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document metadata by ID
        """
        try:
            collection = self.db[self.documents_collection]
            document = await collection.find_one({"_id": document_id})
            
            if document:
                # Remove MongoDB _id for response
                document.pop("_id", None)
            
            return document
            
        except Exception as e:
            logger.error(f"Error retrieving document metadata: {str(e)}")
            return None
    
    async def get_query_history(self, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get query history with pagination
        """
        try:
            collection = self.db[self.queries_collection]
            
            cursor = collection.find({}).sort("processed_at", -1).skip(skip).limit(limit)
            queries = []
            
            async for query in cursor:
                query.pop("_id", None)  # Remove MongoDB _id
                queries.append(query)
            
            return queries
            
        except Exception as e:
            logger.error(f"Error retrieving query history: {str(e)}")
            return []
    
    async def get_query_by_id(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific query by ID
        """
        try:
            collection = self.db[self.queries_collection]
            query = await collection.find_one({"_id": query_id})
            
            if query:
                query.pop("_id", None)
            
            return query
            
        except Exception as e:
            logger.error(f"Error retrieving query: {str(e)}")
            return None
    
    async def update_query_status(self, query_id: str, status: str, error_message: Optional[str] = None):
        """
        Update query status
        """
        try:
            collection = self.db[self.queries_collection]
            
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            await collection.update_one(
                {"_id": query_id},
                {"$set": update_data}
            )
            
            logger.info(f"Updated query {query_id} status to: {status}")
            
        except Exception as e:
            logger.error(f"Error updating query status: {str(e)}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get basic analytics about the system usage
        """
        try:
            queries_collection = self.db[self.queries_collection]
            documents_collection = self.db[self.documents_collection]
            
            # Count total queries
            total_queries = await queries_collection.count_documents({})
            
            # Count total documents
            total_documents = await documents_collection.count_documents({})
            
            # Count queries by status
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_counts = {}
            async for result in queries_collection.aggregate(status_pipeline):
                status_counts[result["_id"]] = result["count"]
            
            # Recent activity (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_queries = await queries_collection.count_documents({
                "processed_at": {"$gte": yesterday}
            })
            
            return {
                "total_queries": total_queries,
                "total_documents": total_documents,
                "status_counts": status_counts,
                "recent_queries_24h": recent_queries,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            return {}
    
    async def health_check(self) -> str:
        """Health check for database service"""
        try:
            if not self.client:
                return "unhealthy - not connected"
            
            # Test database connection
            await self.client.admin.command('ping')
            return "healthy"
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return "unhealthy"
