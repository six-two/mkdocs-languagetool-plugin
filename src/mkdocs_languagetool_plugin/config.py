from mkdocs.config.config_options import Type, ListOfItems
from mkdocs.config.base import Config

MY_DOCKER_IMAGE = "ghcr.io/six-two/languagetool"

class LanguageToolPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # The language tool server to connect to (full URL)
    languagetool_host = Type(str, default="127.0.0.1")

    # Port to use and bind to
    languagetool_port = Type(int, default=8081)

    # Protocol to use (http for localhost)
    languagetool_protocol = Type(str, default="http")

    # The language to use for spell checking
    language = Type(str, default="en-US")

    # Whether to print a summary of results
    print_summary = Type(bool, default=False)

    # Whether to print individual results (spelling errors)
    print_errors = Type(bool, default=True)

    # When this is >= 0, the spell checking is done in the background usinx X threads
    async_threads = Type(int, default=10)

    # When this is enabled, the plugin will start a language tool instance if the server is not reachable
    start_languagetool = Type(bool, default=False)

    # Ignore these files and spelling rules
    ignore_rules = ListOfItems(Type(str), default=[])
    ignore_files = ListOfItems(Type(str), default=[])

    # Output unknown words to this file (make it easier to create a known words file)
    write_unknown_words_to_file = Type(str, default="")

    # Docker image of languagetool to use
    # The most popular seems to be: erikvl87/languagetool
    # My image ghcr.io/six-two/languagetool is based on erikvl87/languagetool, but adds an script to add custom words to the dictionaries
    languagetool_docker_image = Type(str, default=MY_DOCKER_IMAGE)

    # Directory with known word lists to use for the languagetool container.
    # This only works if the plugin starts the docker container.
    custom_known_words_directory = Type(str, default="")


def get_languagetool_url(plugin_config: LanguageToolPluginConfig) -> str:
    return f"{plugin_config.languagetool_protocol}://{plugin_config.languagetool_host}:{plugin_config.languagetool_port}/v2/check"
