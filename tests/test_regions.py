from src.config.regions import extract_region


def test_extract_region_valid_region():
    """Extract valid region from URL path"""

    assert extract_region("https://example.com/da-dk/page") == "da-dk"


def test_extract_region_unknown_when_missing():
    """Return unknown when URL has no region"""

    assert extract_region("https://example.com/page/test") == "unknown"


def test_extract_region_unknown_when_valid():
    """Return unknown for invalid region"""

    assert extract_region("https://example.com/xx-xx/page") == "unknown"