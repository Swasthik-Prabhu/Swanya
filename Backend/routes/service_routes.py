from fastapi import APIRouter, HTTPException, Depends
from models.service_models import ServiceCreate, ServiceSearch, ServiceResponse
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from database import get_database, db
from bson import ObjectId

router = APIRouter()

# MongoDB client setup
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["your_database_name"]
services_collection = db["services"]

# Route for service providers to create a service
@router.post("/create", response_model=ServiceResponse)
async def create_service(service: ServiceCreate, db = Depends(get_database)) -> ServiceResponse:
    """
    Endpoint for service providers to create a service.
    """
    services_collection = db["services"]
    service_data = service.dict()
    
    # Generate a random provider_id
    service_data["provider_id"] = str(ObjectId())   # instead try to give the service_provider_id
    
    result = await services_collection.insert_one(service_data)
    service_data["_id"] = str(result.inserted_id)
    return ServiceResponse(**service_data)




# Route for customers to view all services
@router.get("/", response_model=List[ServiceResponse])
async def list_services(db = Depends(get_database)) -> List[ServiceResponse]:
    """
    Endpoint for customers to list all available services.
    """
    services_collection = db["services"]
    services = await services_collection.find().to_list(100)
    for service in services:
        service["_id"] = str(service["_id"])
    return [ServiceResponse(**service) for service in services]

# Route for customers to search and filter services
@router.post("/search", response_model=List[ServiceResponse])
async def search_services(filters: ServiceSearch, db = Depends(get_database)) -> List[ServiceResponse]:
    """
    Endpoint for customers to search and filter services.
    """
    services_collection = db["services"]
    query = {}
    if filters.category:
        query["category"] = filters.category
    if filters.min_price is not None:
        query["price"] = {"$gte": filters.min_price}
    if filters.max_price is not None:
        query.setdefault("price", {})["$lte"] = filters.max_price
    if filters.availability is not None:
        query["availability"] = filters.availability

    services = await services_collection.find(query).to_list(100)
    for service in services:
        service["_id"] = str(service["_id"])
    return [ServiceResponse(**service) for service in services]