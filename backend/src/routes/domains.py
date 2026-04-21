from fastapi import APIRouter

from ..schemas import DomainsResponse
from ..lib.urls import get_domains

router = APIRouter()

@router.get("/domains", response_model=DomainsResponse)
def domains():
    return DomainsResponse(domains=get_domains())
