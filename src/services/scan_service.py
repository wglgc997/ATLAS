from src.crawler.extractor import extract_links
from src.checker.link_checker import check_link


def build_summary(source_page: str, results: list[dict]) -> dict:
    """Build the summary at the final of scan"""

    return{
        "source_page": source_page,
        "total_links": len(results),
        "good": sum(1 for item in results if item["status"] == "Good"),
        "redirected": sum(1 for item in results if item["status"] == "Redirected"),
        "broken": sum(1 for item in results if item["status"] == "Broken"),
        "results": results,
    }

def scan_page(page_url: str, timeout: int = 10) -> dict:


   extracted_links = extract_links(page_url=page_url, timeout=timeout)

   results = []

   for link in extracted_links:
       result = check_link(
           url=link["abs_url"],
           timeout=timeout,
       )

       result["source_page"] = page_url
       result["link_text"] = link.get("text")
       result["link_type"] = link.get("link_type")
       result["source_attribute"] = link.get("source_attribute")

       results.append(result)

       return build_summary(
           source_page=page_url,
           results=results,
       )