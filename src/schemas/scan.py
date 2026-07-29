from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from src.config.settings import HTTP_TIMEOUT

"""
Esse arquivo define o contrato 
da API: o que o frontend envia 
e o que o backend responde.
"""

class LinkStatus(str, Enum):
    GOOD = "Valid"
    REDIRECTED = "Redirected"
    BROKEN = "Broken"
    UNAUTHORIZED = "Unauthorized"
    FORBIDDEN = "Forbidden"
    GONE = "Gone"
    SERVER_ERROR = "Server Error"
    INVALID_LINK = "Invalid Link"
    INTERACTIVE_ELEMENT = "Interactive Element"
    REDIRECT_LOOP = "Redirect Loop"
    SSL_ERROR = "SSL Error"
    TIMEOUT = "Timeout"
    CONNECTION_ERROR = "Connection Error"
    DNS_ERROR = "DNS Error"
    INTERACTION_ERROR = "Interaction Error"
    UNKNOWN_ERROR = "Unknown Error"

class ScanRequest(BaseModel):
    """Payload received for API"""

    url: HttpUrl
    timeout: int = Field(
        default=HTTP_TIMEOUT,
        ge=1,
        le=60,
        description="Maximum HTTP request timeout in seconds",
    )

    max_workers: int = Field(
        default=12,
        ge=1,
        le=32,
        description="Maximum number of links checked in parallel",
    )
    
    include_assets: bool = Field(
        default=False,
        description="Include technical assets such as scripts and stylesheets",
    )
    
    include_external: bool = Field(
        default=True,
        description="Include links pointing to external domains",
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
    redirect_chain: list[dict[str, int | str | None]] = Field(default_factory=list)
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_description: Optional[str] = None
    technical_details: Optional[str] = None
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
