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
