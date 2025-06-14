import re
from bs4 import BeautifulSoup
from typing import List, Dict

# This single regex is designed to capture the three key parts from a paragraph.
# It looks for "Error Log #<ID>:", then "Issue:" or "Explanation:", and finally "Resolution:" or "Solution:".
# It handles cases where "Resolution:" is missing.
LOG_PATTERN = re.compile(
    r"Error Log\s*#(\d+):"
    r".*?"
    r"(?:Issue|Explanation):\s*(?P<issue>.*?)\.?"
    r"(?:\s*(?:Resolution|Solution):\s*(?P<resolution>.*?)\.?)?$",
    re.IGNORECASE | re.DOTALL
)

def extract_issues_from_html(html_content: str) -> List[Dict[str, str]]:
    """
    Parses HTML from a Confluence page and extracts structured error log data.

    Args:
        html_content: The HTML string of the Confluence page body.

    Returns:
        A list of dictionaries, where each dictionary represents one found error log.
        Example:
        [
            {
                "id": "3999",
                "issue": "can not find cat",
                "resolution": "find cat"
            },
            ...
        ]
    """
    if not html_content:
        return []
        
    soup = BeautifulSoup(html_content, "html.parser")
    found_issues = []

    # The most common format is one error log per paragraph <p> tag.
    for p in soup.find_all("p"):
        text = p.get_text(separator=" ", strip=True)
        match = LOG_PATTERN.search(text)
        if match:
            found_issues.append({
                "id": match.group(1),
                "issue": match.group("issue").strip(),
                "resolution": (match.group("resolution") or "Not specified").strip()
            })
            
    return found_issues 