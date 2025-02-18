# MkDocs LanguageTool Plugin

This is currently a prototype.
It aims to provide high quality spell checking for your documentation.

## Installation

Install it with pip:
```bash
pip install mkdocs-languagetool-plugin
```

## Usage

First as with all MkDocs plugins, add it to your `mkdocs.yml`:
```yaml
plugins:
- search
- languagetool
```

In addition to adding the plugin to your docs, you need to run (or specify) a languagetool server.

### Local languagetool server with docker

You can easily do this with docker:
```bash
docker run --rm -it -p 8081:8010 --name mkdocs-languagetool -e Java_Xmx=2g -d erikvl87/languagetool
```

After you are done, you can stop the languagetool container:
```bash
docker stop mkdocs-languagetool
```

### Remote languagetool server

This can for example be useful if your company / network has a shared languagetool server running somewhere.
You can specify it like this in your `mkdocs.yml`:
```yaml
plugins:
- search
- languagetool:
    languagetool_url: http://YOUR_SERVERS_IP_OR_HOSTNAME:8081/v2/check
```

### Conditional spell checking

Spellchecking causes a lot of CPU load and slows down site builds.
So you may want to only run it at certain times (like before creating a new release).
This can be done using environment variables that enable or disable the plugin.
For example you could use the following snippet in your `mkdocs.yml`:
```yaml
plugins:
- search
- languagetool:
    enabled: !ENV [SPELLCHECK, false]
    languagetool_url: http://YOUR_SERVERS_IP_OR_HOSTNAME:8081/v2/check
```

Then a normal build (`mkdocs build`) would not enable the plugin.
But if you want to do the spell checking, you can set the `SPELLCHECK` variable:
```bash
SPELLCHECK=true mkdocs serve
```

## Notable changes

### Head

- Added option `custom_known_words_directory` to add known words to all or specific languages.
- Added option `languagetool_docker_image` to overwrite which docker image (or tag) to use.
- Added option `write_unknown_words_to_file` to automatically generate a list of unknown / potentially misspelled words.
- Added options to ignore specific files (`ignore_files`) and specific spelling rules (`ignore_rules`).
- Added support for automatically starting the LanguageTool server via docker (`start_languagetool` setting).
- Added parallelized spell checking (via `async_threads`) and enabled it by default.
