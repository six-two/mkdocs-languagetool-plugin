# pip
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import File, Files
# local
from .config import LanguageToolPluginConfig
from .languagetool import spellcheck_text, LanguageToolError, LanguageToolResultEntry

LOGGER = get_plugin_logger(__name__)


class LanguageToolPlugin(BasePlugin[LanguageToolPluginConfig]):
    def on_files(self, files: Files, config) -> Files:
        self.all_spelling_complaints: dict[str,list[LanguageToolResultEntry]] = {} # file path -> spelling results

        # Process markdown files only
        markdown_files = [file for file in files if file.src_path.endswith(".md")]

        try:
            # For each markdown file, we will check spelling/grammar
            for markdown_file in markdown_files:
                self.check_markdown_file(markdown_file)

            if self.config.print_summary:
                self.print_results_summary()

            return files
        except LanguageToolError as ex:
            raise PluginError(f"LanguageToolError: {ex}")


    def check_markdown_file(self, file: File) -> None:
        with open(file.abs_src_path, "r", encoding="utf-8") as f:
            text = f.read()

        results = spellcheck_text(text, self.config.languagetool_url, self.config.language)
        if self.config.print_errors:
            for result in results:
                LOGGER.info(f"{file.src_uri} | {result.rule_id} | {result.colored_context()}")

        self.all_spelling_complaints[file.src_uri] = results

    def print_results_summary(self) -> None:
        rule_id_counters: dict[str,int] = {}
        file_error_count: dict[str,int] = {file_path: len(error_list) for file_path, error_list in self.all_spelling_complaints.items()}

        for error_list in self.all_spelling_complaints.values():
            for error in error_list:
                if error.rule_id in rule_id_counters:
                    rule_id_counters[error.rule_id] += 1
                else:
                    rule_id_counters[error.rule_id] = 1

        LOGGER.info("Suggestion count by rule:\n" + format_counters(rule_id_counters))
        LOGGER.info("Suggestion count per file:\n" + format_counters(file_error_count))

def format_counters(counters: dict[str,int]) -> str:
    # Sort counters from hightest to lowest and print one per line
    return "\n".join([
        f"{name}: {count}"
        for name, count in
        sorted(counters.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    ])