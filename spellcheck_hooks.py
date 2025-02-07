# import os
import requests
# import markdown
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

languagetool_url = "http://localhost:8081/v2/check"  # Make sure your server is running at this address

def on_files(files, config):
    # Process markdown files only
    markdown_files = [file for file in files if file.src_path.endswith(".md")]

    # For each markdown file, we will check spelling/grammar
    for markdown_file in markdown_files:
        with open(markdown_file.abs_src_path, "r", encoding="utf-8") as f:
            text = f.read()

        _spellcheck_file(markdown_file, text)

    return files


def _spellcheck_file(markdown_file, text):
    # Send the text to LanguageTool for checking

    # Expected results from languagetool's "matches":
    # {
    #       "message": "This sentence does not start with an uppercase letter.",
    #   "shortMessage": "",
    #   "replacements": [
    #     {
    #       "value": "A"
    #     }
    #   ],
    #   "offset": 0,
    #   "length": 1,
    #   "context": {
    #     "text": "a simple test",
    #     "offset": 0,
    #     "length": 1
    #   },
    #   "sentence": "a simple test",
    #   "type": {
    #     "typeName": "Other"
    #   },
    #   "rule": {
    #     "id": "UPPERCASE_SENTENCE_START",
    #     "description": "Checks that a sentence starts with an uppercase letter",
    #     "issueType": "typographical",
    #     "urls": [
    #       {
    #         "value": "https://languagetool.org/insights/post/spelling-capital-letters/"
    #       }
    #     ],
    #     "category": {
    #       "id": "CASING",
    #       "name": "Capitalization"
    #     }
    #   },
    #   "ignoreForIncompleteSentence": true,
    #   "contextForSureMatch": -1
    # }


    payload = {
        'language': 'en-US',
        'text': text,
    }
    response = requests.post(languagetool_url, data=payload)

    if response.status_code == 200:
        result = response.json()
        matches = result.get("matches", [])

        # If there are spelling or grammar issues, print them
        for match in matches:
            rule_id = match["rule"]["id"]
            category_id = match["rule"]["category"]["id"]
            context = match["context"]["text"]
            offset = match["context"]["offset"]
            length = match["context"]["length"]

            context_before = context[:offset]
            text_to_highlight = context[offset:offset+length]
            context_after = context[offset+length:]
            highlighted_context = f"{context_before}\033[0;31m{text_to_highlight}\033[0m{context_after}"

            print(f"{markdown_file.src_path} | {category_id}->{rule_id} | {highlighted_context}")
    else:
        print(f"Error connecting to LanguageTool server: {response.status_code}")
