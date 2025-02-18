import glob
import os
import shlex
import subprocess
import time
# pip
from mkdocs.plugins import get_plugin_logger
# local
from .languagetool import is_server_reachable
from .config import LanguageToolPluginConfig, DEFAULT_LANGUAGE_TOOL_URL, MY_DOCKER_IMAGE

LOGGER = get_plugin_logger(__name__)


class DockerHandler:
    def __init__(self, plugin_config: LanguageToolPluginConfig):
        self.plugin_config = plugin_config
        self.started_container = False
        self.languagetool_url = plugin_config.languagetool_url

        if self.languagetool_url != DEFAULT_LANGUAGE_TOOL_URL:
            LOGGER.warning(f"When starting a container, the default LanguageTool URL {DEFAULT_LANGUAGE_TOOL_URL} is expected. But the URL {self.languagetool_url} was given.")

        if plugin_config.custom_known_words_directory:
            if not plugin_config.start_languagetool:
                LOGGER.warning(f"The 'custom_known_words_directory' option only works when you set the 'start_languagetool' option to 'true'")

            if plugin_config.languagetool_docker_image != MY_DOCKER_IMAGE:
                LOGGER.warning(f"The 'custom_known_words_directory' option is designed to be used with the docker image {MY_DOCKER_IMAGE} and may not work with other images. You specified the image {plugin_config.languagetool_docker_image}")
            
            if not glob.glob(os.path.join(plugin_config.custom_known_words_directory, "custom_words_*.txt")):
                LOGGER.warning(f"The 'custom_known_words_directory' directory ({plugin_config.custom_known_words_directory}) does not contain any files matching the pattern 'custom_words_*.txt'. Create a file called 'custom_words_any.txt' and add all words to ignore in it (one per line).")

    def start_service(self):
        if self.plugin_config.custom_known_words_directory:
            # Stop the current server if one exists, since we want to mount the correcy list of words to ignore
            try:
                subprocess.check_output(["docker", "stop", "mkdocs-languagetool-plugin"], stderr=subprocess.STDOUT)
                LOGGER.info("Stopped already running LanguageTool container")
            except subprocess.CalledProcessError as ex:
                pass

        if not is_server_reachable(self.languagetool_url):
            LOGGER.info("LanguageTool server is not reachable, starting docker container")
            try:
                mount_known_words = ["-v", f"{self.plugin_config.custom_known_words_directory}:/share:ro"] if self.plugin_config.custom_known_words_directory else []
                run_command_and_return_output(["docker", "run", "--rm", "-p", "8081:8010", "--name", "mkdocs-languagetool-plugin", "-e", "Java_Xmx=2g", "-d", *mount_known_words, self.plugin_config.languagetool_docker_image])
                self.started_container = True

                # wait for the container to be started (up to 15 seconds)
                for _ in range(150):
                    if is_server_reachable(self.languagetool_url):
                        LOGGER.info("LanguageTool server started successfully")
                        return
                    time.sleep(0.1)
                
                LOGGER.warning("LanguageTool container was started, but can not be reached")
            except subprocess.CalledProcessError as ex:
                LOGGER.error(f"Could not start LanguageTool container with docker. Process exited with code {ex.returncode} and output '{ex.output}'")

    def stop_service(self):
        if self.started_container:
            LOGGER.info("Stopping LanguageTool container")
            try:
                run_command_and_return_output(["docker", "stop", "mkdocs-languagetool-plugin"])
            except subprocess.CalledProcessError as ex:
                LOGGER.error(f"Could not stop LanguageTool container with docker. Process exited with code {ex.returncode} and output '{ex.output}'")


def run_command_and_return_output(command: list[str]) -> bytes:
    LOGGER.debug(f"Running command: {shlex.join(command)}")
    subprocess.check_output(command, stderr=subprocess.STDOUT)
