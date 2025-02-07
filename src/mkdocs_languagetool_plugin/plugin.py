# pip
from mkdocs.config import config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File
# local
from .languagetool import spellcheck_text, LanguageToolError

# @TODO: make it config options
languagetool_url = "http://localhost:8081/v2/check"  # Make sure your server is running at this address
language = "en-US"


class LanguageToolPlugin(BasePlugin):
    def on_files(self, files, config):
        # Process markdown files only
        markdown_files = [file for file in files if file.src_path.endswith(".md")]

        try:
            # For each markdown file, we will check spelling/grammar
            for markdown_file in markdown_files:
                with open(markdown_file.abs_src_path, "r", encoding="utf-8") as f:
                    text = f.read()

                results = spellcheck_text(text, languagetool_url, language)
                for result in results:
                    print(f"{markdown_file.src_uri} | {result.rule_id} | {result.colored_context()}")

            return files
        except LanguageToolError as ex:
            raise PluginError(f"LanguageToolError: {ex}")
