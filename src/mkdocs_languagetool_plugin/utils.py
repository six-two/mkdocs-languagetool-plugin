# pip
from mkdocs.plugins import get_plugin_logger
from mkdocs.exceptions import PluginError
# local
from .config import LanguageToolPluginConfig

LOGGER = get_plugin_logger(__name__)

def log_error(message: str, plugin_config: LanguageToolPluginConfig) -> None:
    """
    This is a wrapper around the error logging function that will enforce the exit_on_error rule
    """
    LOGGER.error(message)

    if plugin_config.exit_on_error:
        raise PluginError("mkdocs_languagetool_plugin: An error occured and 'exit_on_error' is enabled")
