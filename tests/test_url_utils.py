from src.utils.url_utils import get_depth, is_skippable, is_internal, normalize_link, url_https



def test_url_https_true():
    """Return True for HTTPS URLs."""
    assert url_https("https://example.com") is True



def test_url_false_https():
    """Return False for HTTP  URLs."""

    assert url_https("http://example.com") is False


def test_get_depth_root_url():
    """Root URL should have depth zero."""

    assert get_depth("https://example.com") == 0


def test_is_internal_true_same_domain():
    """Identify same-domain links as internal"""

    assert is_internal(
        "https://example.com/page",
        "https://example.com/contact",
    ) is True

def test_is_internal_false_different_domain():
    """Should identify different-domain links as external."""
    assert is_internal(
        "https://example.com/page",
        "https://another.com/contact",
    ) is False


def test_is_skippable_empty_href():
    """Empty href should be skipped."""
    assert is_skippable("") is True


def test_is_skippable_anchor():
    """Anchor links should be skipped."""
    assert is_skippable("#section") is True


def test_is_skippable_mailto():
    """mailto links should be skipped."""
    assert is_skippable("mailto:test@example.com") is True


def test_normalize_link_relative_url():
    """Relative URLs should become absolute URLs."""
    assert normalize_link(
        "https://example.com/base/",
        "/contact",
    ) == "https://example.com/contact"


def test_normalize_link_removes_fragment():
    """URL fragments should be removed."""
    assert normalize_link(
        "https://example.com",
        "/contact#team",
    ) == "https://example.com/contact"