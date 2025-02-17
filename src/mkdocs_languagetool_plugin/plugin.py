import os
# pip
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.files import Files
# local
from .config import LanguageToolPluginConfig
from .languagetool import LanguageToolError
from .tasks import ParallelLanguageToolTasks, process_sequential_languagetool_tasks
from .docker import DockerHandler

LOGGER = get_plugin_logger(__name__)


class LanguageToolPlugin(BasePlugin[LanguageToolPluginConfig]):
    def on_config(self, config):
        if self.config.start_languagetool:
            self.docker_handler = DockerHandler(self.config.languagetool_url)
            self.docker_handler.start_service()
        else:
            self.docker_handler = None

        self.ignore_files = [os.path.normpath(x) for x in self.config.ignore_files]

    def on_files(self, files: Files, config) -> Files:
        # Process markdown files only
        markdown_files = [file for file in files
                          if file.src_uri.endswith(".md")
                             and os.path.normpath(file.src_uri) not in self.ignore_files]

        try:
            if self.config.async_threads > 0:
                # Run in parallel in the background
                self.tasks = ParallelLanguageToolTasks(self.config.languagetool_url, self.config)
                self.tasks.start_parallel(markdown_files, self.config.async_threads)
            else:
                self.tasks = None
                # Run sequential right now
                process_sequential_languagetool_tasks(markdown_files, self.config)

            return files
        except LanguageToolError as ex:
            raise PluginError(f"LanguageToolError: {ex}")

    def on_post_build(self, config) -> None:
        if self.tasks:
            self.tasks.wait_for_parallel()
        
        if self.docker_handler:
            self.docker_handler.stop_service()
