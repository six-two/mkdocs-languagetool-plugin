import glob
import os
import shlex
import subprocess
import time
# pip
from mkdocs.exceptions import PluginError
# local
from .languagetool import is_server_reachable
from .config import LanguageToolPluginConfig, get_languagetool_url, MY_DOCKER_IMAGE
from .utils import LOGGER, log_error


class DockerHandler:
    def __init__(self, plugin_config: LanguageToolPluginConfig):
        self.plugin_config = plugin_config
        self.started_container = False
        self.docker = plugin_config.docker_binary
        self.languagetool_url = get_languagetool_url(plugin_config)

        if self.plugin_config.languagetool_host not in ["127.0.0.1", "::1", "localhost"]:
            LOGGER.warning(f"When starting a container, setting the 'languagetool_host' to a localhost value is expected, but '{self.plugin_config.languagetool_host}' was given.")

        if plugin_config.docker_known_words_directory:
            if not plugin_config.docker_create_container:
                LOGGER.warning("The 'docker_known_words_directory' option only works when you set the 'docker_create_container' option to 'true'")

            if plugin_config.docker_image != MY_DOCKER_IMAGE:
                LOGGER.warning(f"The 'docker_known_words_directory' option is designed to be used with the {self.docker} image {MY_DOCKER_IMAGE} and may not work with other images. You specified the image {plugin_config.docker_image}")
            
            if not glob.glob(os.path.join(plugin_config.docker_known_words_directory, "custom_words_*.txt")):
                LOGGER.warning(f"The 'docker_known_words_directory' directory ({plugin_config.docker_known_words_directory}) does not contain any files matching the pattern 'custom_words_*.txt'. Create a file called 'custom_words_any.txt' and add all words to ignore in it (one per line).")

    def start_service(self):
        if self.plugin_config.docker_known_words_directory and is_server_reachable(self.languagetool_url):
            # Stop the current server if one exists, since we want to mount the correcy list of words to ignore
            try:
                self.run_docker_command_and_return_output(["stop", self.plugin_config.docker_container_name])
                if is_server_reachable(self.languagetool_url):
                    LOGGER.info("Stopped already running LanguageTool container")
                else:
                    LOGGER.warning("Stop command successfull but service is still running. Did you manually start a LanguageTool server? You can also try to solve this problem it by adding 'languagetool_port: <SOME_FREE_PORT>' in your mkdocs.yml")
            except subprocess.CalledProcessError:
                LOGGER.warning("Failed to stop already running LanguageTool container")

        if not is_server_reachable(self.languagetool_url):
            LOGGER.info(f"LanguageTool server is not reachable, starting {self.docker} container")
            try:
                mount_known_words = ["-v", f"{self.plugin_config.docker_known_words_directory}:/share:ro"] if self.plugin_config.docker_known_words_directory else []
                self.run_docker_command_and_return_output([
                    # Start a new container
                    "run",
                    # Remove the container when it is stopped
                    "--rm",
                    # Forward the docker containers LanguageTool API to localhost
                    "-p", f"{self.plugin_config.languagetool_port}:8010",
                    # Give the container a name, so that we can easily stop it
                    "--name", self.plugin_config.docker_container_name,
                    # User supplied arguments, for example to set environment variables
                    *self.plugin_config.docker_custom_arguments,
                    # Run the container in the background
                    "-d",
                    # If we mount known words into the container, this is done by this argument
                    *mount_known_words,
                    # The image to base the container on
                    self.plugin_config.docker_image
                ])
                self.started_container = True

                # wait for the container to be started (up to 15 seconds)
                for _ in range(150):
                    if is_server_reachable(self.languagetool_url):
                        LOGGER.info(f"LanguageTool server started successfully with {self.docker}")
                        return
                    time.sleep(0.1)
                
                log_error(f"LanguageTool container was started with {self.docker}, but service can not be reached")
            except subprocess.CalledProcessError as ex:
                (f"Could not start LanguageTool container with {self.docker}. Process exited with code {ex.returncode} and output '{ex.output}'")

    def stop_service(self):
        if self.started_container:
            LOGGER.info("Stopping LanguageTool container")
            try:
                self.run_docker_command_and_return_output(["stop", "mkdocs-languagetool-plugin"])
            except subprocess.CalledProcessError as ex:
                LOGGER.warning(f"Could not stop LanguageTool container with {self.docker}. Process exited with code {ex.returncode} and output '{ex.output}'")


    def run_docker_command_and_return_output(self, arguments: list[str]) -> bytes:
        command = [self.docker, *arguments]
        LOGGER.debug(f"Running command: {shlex.join(command)}")
        try:
            return subprocess.check_output(command, stderr=subprocess.STDOUT)
        except FileNotFoundError:
            raise PluginError(f"FileNotFoundError: The docker binary '{self.docker}' referenced by 'docker_binary' is not an executable file or is not in your PATH")
