import json
import requests
from typing import NamedTuple


class LanguageToolResultEntry(NamedTuple):
    rule_id: str
    category_id: str
    context: str
    offset: int
    length: int
    raw_dict: dict

    def misspelled_string(self) -> str:
        """
        Returns the word/sequence that causes the error
        """
        end_offset = self.offset + self.length
        return self.context[self.offset:end_offset]

    def colored_context(self) -> str:
        """
        Return the context with the misspelled word highlighted in red using ANSI escape sequences
        """
        end_offset = self.offset + self.length
        return f"{self.context[:self.offset]}\033[0;31m{self.misspelled_string()}\033[0m{self.context[end_offset:]}"

class LanguageToolError(Exception):
    pass


def is_server_reachable(languagetool_url: str):
    try:
        spellcheck_text("test", languagetool_url, "en-US")
        return True
    except LanguageToolError:
        return False

def spellcheck_file(file_path: str, languagetool_url: str, language: str, custom_request_options: dict = {}) -> list[LanguageToolResultEntry]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    return spellcheck_text(text, languagetool_url, language, custom_request_options)


def spellcheck_text(text: str, languagetool_url: str, language: str, custom_request_options: dict = {}) -> list[LanguageToolResultEntry]:
    """
    This function sends a request to the languagetool server and parses the response.

    Parameters:
    - text is the text to check
    - languagetool_url is an URL like "http://localhost:8081/v2/check"
    - language is a string like "en-US"
    """

    http_body = {
        **custom_request_options,
        "language": language,
        "text": text,
    }
    try:
        response = requests.post(languagetool_url, data=http_body)
    except Exception as ex:
        raise LanguageToolError(f"Error connecting to language tool server {languagetool_url}: {ex}")

    if response.status_code == 200:
        result = response.json()
        return [parse_language_tool_match(match) for match in result.get("matches", [])]
    else:
        raise LanguageToolError(f"LanguageTool server at {languagetool_url} returned unexpected status code {response.status_code}: {response.text}")


def parse_language_tool_match(match: dict) -> LanguageToolResultEntry:
    try:
        return LanguageToolResultEntry(
            rule_id=match["rule"]["id"],
            category_id=match["rule"]["category"]["id"],
            context=match["context"]["text"],
            offset=match["context"]["offset"],
            length=match["context"]["length"],
            raw_dict=match,
        )
    except KeyError as e:
        raise LanguageToolError(f"LanguageTool response did not contain the expected key: {e}\nProblematic entry: {json.dumps(match, indent=4)}")
