# pip
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import File, Files
# local
from .config import LanguageToolPluginConfig
from .languagetool import spellcheck_file, LanguageToolError, LanguageToolResultEntry
from .tasks import LanguageToolTasks, print_results_summary, print_individual_errors

LOGGER = get_plugin_logger(__name__)


class LanguageToolPlugin(BasePlugin[LanguageToolPluginConfig]):
    def on_files(self, files: Files, config) -> Files:
        self.all_spelling_complaints: dict[str,list[LanguageToolResultEntry]] = {} # file path -> spelling results

        # Process markdown files only
        markdown_files = [file for file in files if file.src_path.endswith(".md")]

        try:
            if self.config.async_threads > 0:
                # Run in parallel in the background
                self.tasks = LanguageToolTasks(self.config.languagetool_url, self.config.language, self.config.print_summary, self.config.print_errors)
                self.tasks.start_parallel(markdown_files, self.config.async_threads)
            else:
                self.tasks = None
                # For each markdown file, we will check spelling/grammar
                for markdown_file in markdown_files:
                    self.check_markdown_file(markdown_file)

                if self.config.print_summary:
                    print_results_summary(self.all_spelling_complaints)

            return files
        except LanguageToolError as ex:
            raise PluginError(f"LanguageToolError: {ex}")

    def on_post_build(self, config) -> None:
        if self.tasks:
            self.tasks.wait_for_parallel()

    def check_markdown_file(self, file: File) -> None:
        results = spellcheck_file(file.abs_src_path, self.config.languagetool_url, self.config.language)
        if self.config.print_errors:
            print_individual_errors(file, results)

        self.all_spelling_complaints[file.src_uri] = results
