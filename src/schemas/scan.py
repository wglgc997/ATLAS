from pydantic import BaseModel, HttpUrl
from typing import Optional

"""
Esse arquivo define o contrato 
da API: o que o frontend envia 
e o que o backend responde.
"""

class ScanRequest(BaseModel):
    """Payload received for API"""

    url : HttpUrl
    timeout: int = 10

class LinkResult(BaseModel):
    """
    Pattern response of each
    link analyzed inside the page
    """

    url: str
    final_url: Optional[str]
    http_status: Optional[str]
    status: str
    response_time_ms: int
    error_message: Optional[str]
    source_page: str
    link_text: Optional[str] = None
    link_type: Optional[str] = None
    source_attribute: Optional[str] = None


class ScanResponse(BaseModel):
    """Summary of the complete analyze"""

    source_page: str
    total_links: int
    good: int
    redirected: int
    broken: int
    results: list[LinkResult]
