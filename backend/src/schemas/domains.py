from pydantic import BaseModel

class DomainsResponse(BaseModel):
    domains: list[str]