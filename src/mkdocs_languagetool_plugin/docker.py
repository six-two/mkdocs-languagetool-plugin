import subprocess
import time
# pip
from mkdocs.plugins import get_plugin_logger
# local
from .languagetool import is_server_reachable
from .config import DEFAULT_LANGUAGE_TOOL_URL

LOGGER = get_plugin_logger(__name__)


class DockerHandler:
    def __init__(self, languagetool_url):
        self.started_container = False
        self.languagetool_url = languagetool_url

        if self.languagetool_url != DEFAULT_LANGUAGE_TOOL_URL:
            LOGGER.warning(f"When starting a container, the default LanguageTool URL {DEFAULT_LANGUAGE_TOOL_URL} is expected. But the URL {self.languagetool_url} was given.")

    def start_service(self):
        if not is_server_reachable(self.languagetool_url):
            LOGGER.info("LanguageTool server is not reachable, starting docker container")
            try:
                subprocess.check_output(["docker", "run", "--rm", "-p", "8081:8010", "--name", "mkdocs-languagetool-plugin", "-e", "Java_Xmx=2g", "-d", "erikvl87/languagetool"], stderr=subprocess.STDOUT)
                self.started_container = True

                # wait for the container to be started (up to 15 minutes)
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
                subprocess.check_output(["docker", "stop", "mkdocs-languagetool-plugin"], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as ex:
                LOGGER.error(f"Could not stop LanguageTool container with docker. Process exited with code {ex.returncode} and output '{ex.output}'")

