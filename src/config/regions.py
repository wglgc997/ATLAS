import re

from urllib.parse import urlparse

REGIONS = r"^[a-z]{2}-[a-z]{2}$"
VALID_REGIONS = [
    "en-uk",
    "en-ie",
    "da-dk",
    "de-de",
    "de-at",
    "de-ch",
    "es-es",
    "fr-fr",
    "fr-be",
    "fr-ch",
    "it-it",
    "nl-nl",
    "nl-be",
    "no-no",
    "sv-se",
    "hu-hu",
    "ro-ro",
    "tr-tr",
    "pl-pl",
    "en-ng",
    "en-bg",
    "en-yu",
    "en-hr",
    "ja-jp",
    "ko-kr",
    "zh-cn",
    "zh-tw",
    "zh-hk",
    "en-hk",
    "en-au",
    "en-nz",
    "en-in",
    "en-sg",
    "en-pk",
    "en-ph",
    "en-id",
    "en-vn",
    "en-th",
    "en-us",
    "en-ca",
    "fr-ca",
    "en/es",
    "es/ag",
    "es/ai",
    "es/an",
    "es/ar",
    "es/aw",
    "es/bb",
    "es/bm",
    "es/bo",
    "es/bs",
    "es/bz",
    "es/cl",
    "es/co",
    "es/cr",
    "es/dm",
    "es/do",
    "es/ec",
    "es/es",
    "es/gd",
    "es/gt",
    "es/gy",
    "es/hn",
    "es/ht",
    "es/jm",
    "es/kn",
    "es/ky",
    "es/la",
    "es/lc",
    "es/mx",
    "es/ni",
    "es/pa",
    "es/pe",
    "es/pr",
    "es/py",
    "es/sr",
    "es/sv",
    "es/tc",
    "es/tt",
    "es/ue",
    "es/us",
    "es/uy",
    "es/vc",
    "es/ve",
    "es/vg",
    "es/vi",
]


def extract_region(url):
    """Extract the region from link. Ex :PT-BR"""
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if not parts:
        return "unknown"
    first_part = parts[0].lower()

    if not re.match(REGIONS, first_part):
        return "unknown"

    if first_part in VALID_REGIONS:
        return first_part
    return "unknown"
