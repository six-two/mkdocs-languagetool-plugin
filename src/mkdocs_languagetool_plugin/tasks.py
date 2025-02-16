import concurrent.futures
import traceback
# pip
from mkdocs.structure.files import File, Files
from mkdocs.plugins import get_plugin_logger
# local
from .languagetool import spellcheck_file, LanguageToolResultEntry


LOGGER = get_plugin_logger(__name__)


class LanguageToolTasks:
    def __init__(self, languagetool_url, language, print_summary, print_errors):
        self.languagetool_url = languagetool_url
        self.language = language
        self.print_summary = print_summary
        self.print_errors = print_errors
        self.results: dict[File,list[LanguageToolResultEntry]] = {}

    def start_parallel(self, file_list: list[File], max_parallel_tasks: int):
        LOGGER.info(f"Starting parallel spell checking with {max_parallel_tasks} threads")
        # Use ThreadPoolExecutor to run tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_tasks) as executor:
            # Submit tasks asynchronously
            self.future_to_task = {executor.submit(spellcheck_file, file.abs_src_path, self.languagetool_url, self.language): file for file in file_list}

    def wait_for_parallel(self):
        # Wait for all futures to complete and get the results
        for future in concurrent.futures.as_completed(self.future_to_task):
            task_file_argument = self.future_to_task[future]
            try:
                result = future.result()  # This will block until the task is finished
                self.results[task_file_argument] = result
                if self.print_errors:
                    print_individual_errors(task_file_argument, result)
                # print(f"File {task_file_argument.src_uri} result: {result}")
            except Exception as e:
                LOGGER.error(f"File {task_file_argument.src_uri} generated an exception: {traceback.format_exc()}")
        
        if self.print_summary:
            print_results_summary(self.results)


def print_individual_errors(file: File, spellcheck_results: list[LanguageToolResultEntry]) -> None:
    for result in spellcheck_results:
        LOGGER.info(f"{file.src_uri} | {result.rule_id} | {result.colored_context()}")


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

def format_counters(counters: dict[str,int]) -> str:
    # Sort counters from hightest to lowest and print one per line
    return "\n".join([
        f"{name}: {count}"
        for name, count in
        sorted(counters.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    ])