import argparse


def parse_args():
    """Create the CLI environment and catch the URL"""
    parser = argparse.ArgumentParser(
        description="Check broken links from CVC pre-live environment."
    )
    parser.add_argument(
        "--url",
        nargs="?",
        default=None,
        help="Page URL to scan. Example: https://example.com",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=20,
        help="Number of links to check at the same time. Default: 20",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Seconds to wait before a link request fails. Default: 10",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        help="Optional path to save the result as CSV.",
    )
    parser.add_argument(
        "--only-broken",
        action="store_true",
        help="Print only broken links and errors.",
    )

    parser.add_argument("--file", help="Read a file")
    return parser.parse_args()
