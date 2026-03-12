"""JSM (Jira Service Management) tracking endpoints."""

from fastapi import APIRouter

from ...services.jsm.service_desks import (
    get_all_service_desks,
    get_service_desk_detail,
    get_request_types,
    get_queues,
    get_jsm_overview,
)
from ...services.jsm.organizations import get_all_organizations

router = APIRouter(prefix="/jsm", tags=["Jira Service Management"])


@router.get("/overview")
async def jsm_overview():
    return await get_jsm_overview()


@router.get("/service-desks")
async def list_service_desks():
    return await get_all_service_desks()


@router.get("/service-desks/{service_desk_id}")
async def service_desk_detail(service_desk_id: str):
    return await get_service_desk_detail(service_desk_id)


@router.get("/service-desks/{service_desk_id}/request-types")
async def request_types(service_desk_id: str):
    return await get_request_types(service_desk_id)


@router.get("/service-desks/{service_desk_id}/queues")
async def queues(service_desk_id: str):
    return await get_queues(service_desk_id)


@router.get("/organizations")
async def list_organizations():
    return await get_all_organizations()
