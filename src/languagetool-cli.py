#!/usr/bin/env python3

import argparse
import sys
# local
from mkdocs_languagetool_plugin.languagetool import spellcheck_text, LanguageToolResultEntry

HIGHLIGHT_COLOR = "\033[0;31m"
HIGHLIGHT_RESET = "\033[0m"


def print_colored_function(text: str, errors: list[LanguageToolResultEntry]) -> None:
    colored_text = text
    # Iterate over reversed results to keep the indexes correct
    for error in reversed(errors):
        error_start = error.raw_dict["offset"]
        error_end = error_start + error.raw_dict["length"]
        colored_text = colored_text[:error_start] + HIGHLIGHT_COLOR + error.misspelled_string + HIGHLIGHT_RESET + colored_text[error_end:]
    
    print(colored_text)


def print_errors_function(text: str, errors: list[LanguageToolResultEntry]) -> None:
    print(f"[*] Found {len(errors)} error(s)")

    for error in errors:
        line_range = f"{error.line_start}" if error.line_start == error.line_end else f"{error.line_start}-{error.line_end}"
        print(f"Line {line_range} | {error.rule_id} | {error.context_colored}")


def print_statistics_function(text: str, errors: list[LanguageToolResultEntry]) -> None:
    rule_id_counters: dict[str,int] = {}

    for error in errors:
        if error.rule_id in rule_id_counters:
            rule_id_counters[error.rule_id] += 1
        else:
            rule_id_counters[error.rule_id] = 1

    print("[*] Error count by rule:\n" + format_counters(rule_id_counters))


def format_counters(counters: dict[str,int]) -> str:
    # Sort counters from hightest to lowest and print one per line
    return "\n".join([
        f"{name}: {count}"
        for name, count in
        sorted(counters.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="the file to spellcheck (default: read from stdin)")
    ap.add_argument("-u", "--url", default="http://localhost:8081/v2/check", help="the URL of the language tool server (default: http://localhost:8081/v2/check)")
    ap.add_argument("-l", "--language", default="en-US", help="the language of the text (default: en-US)")
    action_group = ap.add_argument_group("Actions")
    action_group.add_argument("-c", "--color", action="store_true", help="print the text with errors highlighted in color")
    action_group.add_argument("-e", "--errors", action="store_true", help="show errors descriptions")
    action_group.add_argument("-s", "--statistics", action="store_true", help="show errors statistics")

    args = ap.parse_args()

    if args.file:
        try:
            with open(args.file) as f:
                text = f.read()
        except Exception as ex:
            print(f"[!] Failed to read file {args.file}: {ex}")
    else:
        text = sys.stdin.read()

    print_colors = args.color
    print_errors = args.errors
    print_statistics = args.statistics
    # Default to one action if none are supplied
    if not print_colors and not print_errors and not print_statistics:
        print_colors = True

    errors = spellcheck_text(text, args.url, args.language, {})

    if print_colors:
        print_colored_function(text, errors)
    if print_errors:
        print_errors_function(text, errors)
    if print_statistics:
        print_statistics_function(text, errors)

    error_count = min(len(errors), 128)
    exit(error_count)


if __name__ == "__main__":
    main()
