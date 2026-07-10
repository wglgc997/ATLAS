from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

"""
Esse arquivo define o contrato 
da API: o que o frontend envia 
e o que o backend responde.
"""

LinkStatus = Literal["Good", "Redirected", "Broken", "Error"]


class ScanRequest(BaseModel):
    """Payload received for API"""

    url: HttpUrl
    timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Maximum request timeout in seconds",
    )

class LinkResult(BaseModel):
    """
    Pattern response of each
    link analyzed inside the page
    """

    url: str
    final_url: Optional[str] = None
    http_status: Optional[int] = None
    status: LinkStatus
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    source_page: str
    link_text: Optional[str] = None
    link_type: Optional[str] = None
    source_attribute: Optional[str] = None
    source_location: Optional[str] = None


class ScanResponse(BaseModel):
    """Summary of the complete analyze"""

    source_page: str
    total_links: int
    good: int
    redirected: int
    broken: int
    error: int
    results: list[LinkResult]
