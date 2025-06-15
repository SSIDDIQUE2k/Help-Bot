import re
import logging
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLExtractor:
    def clean_html(self, html_content: str) -> str:
        """Cleans HTML to a text string, preserving line breaks for structure."""
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # Use a newline separator to maintain the document's structure
            text = soup.get_text(separator='\n')
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_content

    def extract_error_entries(self, content: str) -> List[Dict[str, str]]:
        """
        The final multi-format engine. It tries different patterns to extract
        structured error entries from any known Confluence page format.
        """
        clean_content = self.clean_html(content)
        entries = []

        # --- Pattern 1: Direct Error Log format (from actual content) ---
        pattern1 = re.compile(
            r"Error Log\s*(\d+):\s*(.*?)\s*Issue:\s*(.*?)\s*Solutions?:\s*(.*?)(?=Error Log\s*\d+:|\Z)",
            re.DOTALL | re.IGNORECASE
        )
        for match in pattern1.finditer(clean_content):
            log_num, title, issue, solution_block = match.groups()
            # Clean up the solution block by removing extra whitespace and joining lines
            solutions = ' '.join([line.strip() for line in solution_block.split('\n') if line.strip()])
            entries.append({
                'id': log_num.strip(),
                'error_code': f"Error Log {log_num.strip()}: {title.strip()}",
                'explanation': issue.strip(),
                'resolution': solutions.strip(),
            })
        if entries:
            logger.info(f"SUCCESS: Extractor found {len(entries)} entries using 'Direct Error Log' format.")
            return entries

        # --- Pattern 2: "Error Log #..." ---
        pattern2 = re.compile(
            r"Error Log\s*#(\d+):\s*(.*?)\s*Issue:\s*(.*?)\s*Resolution:\s*(.*?)(?=(?:\s*Error Log\s*#\d+|$))",
            re.DOTALL | re.IGNORECASE
        )
        for match in pattern2.finditer(clean_content):
            log_num, title, issue, resolution = match.groups()
            entries.append({
                'id': log_num.strip(),
                'error_code': f"Error Log #{log_num.strip()}: {title.strip()}",
                'explanation': issue.strip(),
                'resolution': resolution.strip(),
            })
        if entries:
            logger.info(f"SUCCESS: Extractor found {len(entries)} entries using 'Error Log #' format.")
            return entries

        # --- Pattern 3: "Timestamp ERROR..." ---
        pattern3 = re.compile(
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\s+ERROR\s+.*?)\s+Explanation:\s+(.*?)\s+Solution:\s+(.*?)(?=(?:\s*\d{4}-\d{2}-\d{2}T|$))",
            re.DOTALL | re.IGNORECASE
        )
        for match in pattern3.finditer(clean_content):
            error_line, explanation, solution = match.groups()
            entries.append({
                'id': error_line.split(' ')[0],
                'error_code': error_line.strip(),
                'explanation': explanation.strip(),
                'resolution': solution.strip(),
            })
        if entries:
            logger.info(f"SUCCESS: Extractor found {len(entries)} entries using 'Timestamp ERROR' format.")
            return entries

        logger.error("FAILURE: Could not detect any known structured error log formats in the content.")
        return []

    def find_best_match(self, user_query: str, entries: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Finds the best matching error entry based on semantic similarity, keywords, and exact ID."""
        if not entries:
            return None

        user_query_lower = user_query.lower().strip()

        # First, check for exact "Error Log #<number>" matches
        exact_match = re.search(r'error log\s*#?(\d+)', user_query_lower)
        if exact_match:
            query_log_num = exact_match.group(1)
            for entry in entries:
                if entry.get('id') == query_log_num:
                    logger.info(f"Found direct match for log #{query_log_num}")
                    return entry

        # Enhanced semantic matching for error descriptions
        best_match = None
        highest_score = 0
        
        # Extract meaningful words from user query (filter out common words)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'cant', 'im', 'having', 'getting', 'error', 'log'}
        query_words = set(word for word in re.findall(r'\b\w{3,}\b', user_query_lower) if word not in stop_words)
        
        # Define error type keywords for better categorization
        error_types = {
            'connection': ['connection', 'connect', 'timeout', 'network', 'socket', 'unreachable', 'refused', 'disconnected'],
            'authentication': ['auth', 'login', 'password', 'credential', 'unauthorized', 'forbidden', 'access', 'permission'],
            'database': ['database', 'sql', 'query', 'table', 'connection', 'db', 'mysql', 'postgres', 'oracle'],
            'file': ['file', 'directory', 'path', 'folder', 'missing', 'not found', 'permission', 'read', 'write'],
            'server': ['server', 'internal', '500', 'service', 'unavailable', 'down', 'maintenance'],
            'validation': ['validation', 'invalid', 'format', 'required', 'missing', 'empty', 'null'],
            'api': ['api', 'endpoint', 'request', 'response', 'json', 'xml', 'rest', 'soap'],
            'configuration': ['config', 'configuration', 'setting', 'property', 'parameter', 'variable']
        }

        logger.info(f"Searching for semantic matches with query words: {query_words}")

        for entry in entries:
            score = 0
            title = entry.get('error_code', '').lower()
            explanation = entry.get('explanation', '').lower()
            resolution = entry.get('resolution', '').lower()
            
            # Extract words from entry content
            title_words = set(re.findall(r'\b\w{3,}\b', title))
            explanation_words = set(re.findall(r'\b\w{3,}\b', explanation))
            resolution_words = set(re.findall(r'\b\w{3,}\b', resolution))
            
            # Basic keyword matching (weighted by importance)
            score += len(query_words.intersection(title_words)) * 5  # Title matches are most important
            score += len(query_words.intersection(explanation_words)) * 3  # Explanation matches are important
            score += len(query_words.intersection(resolution_words)) * 1  # Resolution matches are helpful
            
            # Error type matching - boost score if query and entry are same error type
            query_error_types = set()
            entry_error_types = set()
            
            for error_type, keywords in error_types.items():
                if any(keyword in user_query_lower for keyword in keywords):
                    query_error_types.add(error_type)
                if any(keyword in title or keyword in explanation for keyword in keywords):
                    entry_error_types.add(error_type)
            
            # Boost score for matching error types
            common_types = query_error_types.intersection(entry_error_types)
            score += len(common_types) * 4
            
            # Fuzzy matching for common error patterns
            fuzzy_patterns = [
                (r'timeout|time.*out', r'timeout|time.*out', 3),
                (r'connection.*failed|failed.*connection', r'connection.*failed|failed.*connection', 3),
                (r'not.*found|missing|does.*not.*exist', r'not.*found|missing|does.*not.*exist', 3),
                (r'unauthorized|access.*denied|permission.*denied', r'unauthorized|access.*denied|permission.*denied', 3),
                (r'internal.*server.*error|500.*error', r'internal.*server.*error|500.*error', 3),
                (r'invalid.*format|format.*invalid', r'invalid.*format|format.*invalid', 2),
                (r'database.*error|sql.*error', r'database.*error|sql.*error', 3),
                (r'network.*error|network.*issue', r'network.*error|network.*issue', 3)
            ]
            
            for query_pattern, entry_pattern, boost in fuzzy_patterns:
                if re.search(query_pattern, user_query_lower) and re.search(entry_pattern, title + ' ' + explanation):
                    score += boost
            
            # Partial word matching for technical terms
            for query_word in query_words:
                if len(query_word) > 4:  # Only for longer words
                    for entry_word in title_words.union(explanation_words):
                        if len(entry_word) > 4:
                            # Check if words share significant portion
                            if query_word in entry_word or entry_word in query_word:
                                score += 1
                            # Check for similar technical terms (e.g., "conn" matches "connection")
                            elif len(query_word) >= 4 and len(entry_word) >= 4:
                                if query_word[:4] == entry_word[:4]:
                                    score += 0.5

            if score > highest_score:
                highest_score = score
                best_match = entry

        if highest_score > 0:
            logger.info(f"Found best semantic match with score {highest_score}: {best_match.get('error_code')}")
            logger.info(f"Match details - Title: {best_match.get('error_code')[:100]}...")
            return best_match
        
        logger.warning("No semantic match found, returning first entry as fallback.")
        return entries[0] if entries else None

    def _clean_html_and_get_blocks(self, html_content: str) -> List[str]:
        """Cleans HTML and splits it into logical text blocks."""
        text = self.clean_html(html_content)
        # Split by one or more newlines, and filter out any empty strings
        return [block.strip() for block in re.split(r'\n\s*\n+', text) if block.strip()]

    def find_best_solution(self, user_query: str, page_content: str) -> Dict[str, str]:
        """
        The main universal parsing function. It finds the best explanation and
        resolution from any page based on semantic proximity to the user's query.
        """
        blocks = self._clean_html_and_get_blocks(page_content)
        if not blocks:
            return {
                "user_issue": user_query,
                "explanation": "Could not find any readable content on the Confluence page.",
                "resolution_steps": "Please check the page directly. It may be empty or use a format the parser cannot read."
            }

        user_query_lower = user_query.lower().strip()
        query_words = set(re.findall(r'\b\w{3,}\b', user_query_lower)) # Extract significant words

        best_block_index = -1
        highest_score = 0

        # Find the single block that best matches the user's query. This is our "explanation".
        for i, block in enumerate(blocks):
            block_lower = block.lower()
            block_words = set(re.findall(r'\b\w{3,}\b', block_lower))
            
            # Calculate a relevance score based on shared keywords
            score = len(query_words.intersection(block_words))
            
            # Boost score for blocks containing key indicators
            if any(kw in block_lower for kw in ['error', 'failed', 'issue', 'unable', 'exception', 'problem']):
                score += 3
            
            if score > highest_score:
                highest_score = score
                best_block_index = i

        if best_block_index != -1:
            explanation = blocks[best_block_index]
            
            # Assume the resolution is the very next block of text
            resolution = "No specific resolution found immediately following the explanation."
            if best_block_index + 1 < len(blocks):
                resolution = blocks[best_block_index + 1]

            # Trim overly long explanation / resolution so the UI only shows relevant info
            explanation = self._trim_text(explanation, max_lines=3, max_chars=400)
            resolution = self._trim_text(resolution, max_lines=8, max_chars=700)

            logger.info(f"Universal parser found best match at block {best_block_index} with score {highest_score}.")
            return {
                "user_issue": user_query,
                "explanation": explanation,
                "resolution_steps": resolution,
            }

        # This is a fallback if no block matches the query at all.
        logger.warning("No relevant blocks found. Returning page summary as a last resort.")
        return {
            "user_issue": user_query,
            "explanation": "Could not find a specific section matching your query.",
            "resolution_steps": " ".join(blocks[:2]) # Return the first couple of blocks as a summary
        }

    # Helper to shorten long text blocks
    def _trim_text(self, text: str, max_lines: int = 5, max_chars: int = 500) -> str:
        """Trim text to a reasonable length for UI display."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        trimmed_lines = []
        char_count = 0
        for line in lines:
            if char_count + len(line) > max_chars or len(trimmed_lines) >= max_lines:
                break
            trimmed_lines.append(line)
            char_count += len(line)
        result = ' '.join(trimmed_lines)
        if len(lines) > len(trimmed_lines):
            result += ' …'
        return result 