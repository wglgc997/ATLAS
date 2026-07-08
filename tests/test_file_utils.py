from src.utils.file_utils import read_file


def test_read_file_ignores_empty_lines(tmp_path):
    """Read only non-empty lines from input file."""

    file_path = tmp_path / "links.txt"

    file_path.write_text(
        "https://example.com\n\nhttps://google.com\n",
        encoding="utf-8",
    )

    result = read_file(file_path)

    assert result == [
        "https://example.com",
        "https://google.com",
    ]

