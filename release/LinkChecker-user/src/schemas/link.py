from enum import Enum

from pydantic import BaseModel


class LinkType(str, Enum):
    ANCHOR = "anchor"
    RESOURCE = "resource"
    SCRIPT = "script"
    IMAGE = "image"
    IFRAME = "iframe"


class InteractionStatus(str, Enum):
    INTERACTIVE = "interactive"
    ERROR = "error"
    NAVIGATED = "navigated"


class ExtractedLink(BaseModel):
    url: str | None = None
    raw_url: str | None = None
    link_text: str | None = None
    link_type: LinkType
    source_attribute: str | None = None
    source_location: str | None = None
    ignored: bool = False
    element_index: int | None = None
    interaction_status: InteractionStatus | None = None
    interaction_detail: str | None = None
    interaction_error: str | None = None
    invalid_reason: str | None = None

    model_config = {
        "use_enum_values": True,
    }
