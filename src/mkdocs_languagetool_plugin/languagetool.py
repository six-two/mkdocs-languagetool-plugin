import json
import requests
from typing import NamedTuple


class LanguageToolResultEntry(NamedTuple):
    rule_id: str
    category_id: str
    misspelled_string: str
    context_text: str
    context_colored: str
    line_start: int
    line_end: int
    raw_dict: dict


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
        return [parse_language_tool_match(match, text) for match in result.get("matches", [])]
    else:
        raise LanguageToolError(f"LanguageTool server at {languagetool_url} returned unexpected status code {response.status_code}: {response.text}")


def parse_language_tool_match(match: dict, full_text: str) -> LanguageToolResultEntry:
    try:
        context_start = match["context"]["offset"]
        context_end = context_start + match["context"]["length"]
        context_text = match["context"]["text"]
        misspelled_string = context_text[context_start:context_end]
        context_colored = f"{context_text[:context_start]}\033[0;31m{misspelled_string}\033[0m{context_text[context_end:]}"

        # Figure out wich lines in the original text the error is in
        full_text_start = match["offset"]
        full_text_end = full_text_start + match["length"]
        match_start_line_index = full_text[:full_text_start].count("\n") + 1
        match_end_line_index = match_start_line_index + full_text[full_text_start:full_text_end].count("\n")

        return LanguageToolResultEntry(
            rule_id=match["rule"]["id"],
            category_id=match["rule"]["category"]["id"],
            misspelled_string=misspelled_string,
            context_text=context_text,
            context_colored=context_colored,
            line_start=match_start_line_index,
            line_end=match_end_line_index,
            raw_dict=match,
        )
    except KeyError as e:
        raise LanguageToolError(f"LanguageTool response did not contain the expected key: {e}\nProblematic entry: {json.dumps(match, indent=4)}")
