import concurrent.futures
import traceback
# pip
from mkdocs.structure.files import File, Files
from mkdocs.plugins import get_plugin_logger
# local
from .languagetool import spellcheck_file, LanguageToolResultEntry
from .config import LanguageToolPluginConfig, get_languagetool_url


LOGGER = get_plugin_logger(__name__)


class ParallelLanguageToolTasks:
    def __init__(self, plugin_config):
        self.plugin_config = plugin_config
        self.languagetool_url = get_languagetool_url(plugin_config)
        self.custom_request_options = {
            "disabledRules": ",".join(plugin_config.ignore_rules),
        }

        self.results: dict[File,list[LanguageToolResultEntry]] = {}

    def start_parallel(self, file_list: list[File], max_parallel_tasks: int):
        LOGGER.info(f"Starting parallel spell checking with {max_parallel_tasks} threads")
        # Use ThreadPoolExecutor to run tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_tasks) as executor:
            # Submit tasks asynchronously
            self.future_to_task = {executor.submit(spellcheck_file, file.abs_src_path, self.languagetool_url, self.plugin_config.language, self.custom_request_options): file for file in file_list}

    def wait_for_parallel(self):
        # Wait for all futures to complete and get the results
        for future in concurrent.futures.as_completed(self.future_to_task):
            task_file_argument = self.future_to_task[future]
            try:
                result = future.result()
                self.results[task_file_argument] = result
                if self.plugin_config.print_errors:
                    print_individual_errors(task_file_argument, result)
            except Exception as e:
                LOGGER.error(f"File {task_file_argument.src_uri} generated an exception: {traceback.format_exc()}")
        
        result_post_processing(self.plugin_config, self.results)


def process_sequential_languagetool_tasks(file_list: list[File], plugin_config: LanguageToolPluginConfig):
    all_spelling_complaints: dict[str,list[LanguageToolResultEntry]] = {} # file path -> spelling results
    languagetool_url = get_languagetool_url(plugin_config)
    custom_request_options = {
        "disabledRules": ",".join(plugin_config.ignore_rules),
    }

    for file in file_list:
        results = spellcheck_file(file.abs_src_path, languagetool_url, plugin_config.language, custom_request_options)
        if plugin_config.print_errors:
            print_individual_errors(file, results)

        all_spelling_complaints[file.src_uri] = results

    result_post_processing(plugin_config, all_spelling_complaints)


def result_post_processing(plugin_config: LanguageToolPluginConfig, all_spelling_complaints: dict[str,list[LanguageToolResultEntry]]) -> None:
    if plugin_config.print_summary:
        print_results_summary(all_spelling_complaints)

    if plugin_config.write_unknown_words_to_file:
        write_unknown_words_to_file(plugin_config.write_unknown_words_to_file, all_spelling_complaints)


def print_individual_errors(file: File, spellcheck_results: list[LanguageToolResultEntry]) -> None:
    for result in spellcheck_results:
        line_range = f"{result.line_start}" if result.line_start == result.line_end else f"{result.line_start}-{result.line_end}"
        LOGGER.info(f"{file.src_uri}:{line_range} | {result.rule_id} | {result.context_colored}")


def print_results_summary(results: dict[File,list[LanguageToolResultEntry]]) -> None:
    rule_id_counters: dict[str,int] = {}
    file_error_count: dict[str,int] = {file_path: len(error_list) for file_path, error_list in results.items()}

    for error_list in results.values():
        for error in error_list:
            if error.rule_id in rule_id_counters:
                rule_id_counters[error.rule_id] += 1
            else:
                rule_id_counters[error.rule_id] = 1

    LOGGER.info("Suggestion count by rule:\n" + format_counters(rule_id_counters))
    LOGGER.info("Suggestion count per file:\n" + format_counters(file_error_count))


def write_unknown_words_to_file(output_path: str, results: dict[File,list[LanguageToolResultEntry]]) -> None:
    unknown_words: set[str] = set()
    for error_list in results.values():
        for error in error_list:
            if error.rule_id.startswith("MORFOLOGIK_RULE_"):
                unknown_words.add(error.misspelled_string)

    file_contents = "\n".join(sorted(unknown_words)) + "\n"
    with open(output_path, "w") as f:
        f.write(file_contents)


def format_counters(counters: dict[str,int]) -> str:
    # Sort counters from hightest to lowest and print one per line
    return "\n".join([
        f"{name}: {count}"
        for name, count in
        sorted(counters.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    ])
