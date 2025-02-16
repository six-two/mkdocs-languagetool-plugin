from mkdocs.config.config_options import Type
from mkdocs.config.base import Config

class LanguageToolPluginConfig(Config):
    """
    The plugin config, that will be parsed from the settings supplied in `mkdocs.yaml`
    """
    # The language tool server to connect to (full URL)
    languagetool_url = Type(str, default="http://localhost:8081/v2/check")

    # The language to use for spell checking
    language = Type(str, default="en-US")

    # Whether to print a summary of results
    print_summary = Type(bool, default=False)

    # Whether to print individual results (spelling errors)
    print_errors = Type(bool, default=True)

    # When this is >= 0, the spell checking is done in the background usinx X threads
    async_threads = Type(int, default=10)
