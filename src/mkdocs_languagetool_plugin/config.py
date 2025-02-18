from mkdocs.config.config_options import Type, ListOfItems
from mkdocs.config.base import Config

DEFAULT_LANGUAGE_TOOL_URL = "http://localhost:8081/v2/check"

class LanguageToolPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # The language tool server to connect to (full URL)
    languagetool_url = Type(str, default=DEFAULT_LANGUAGE_TOOL_URL)

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
