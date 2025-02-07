# MkDocs LanguageTool Plugin

This is currently a prototype.
It aims to provide high quality spell checking for your documentation.

## Usage

In addition to adding the plugin to your docs, you need to run a languagetool server.
You can easily do this with docker:
```bash
docker run --rm -it -p 8081:8010 --name mkdocs-languagetool -e Java_Xmx=2g -d erikvl87/languagetool
```

After you are done, you can stop the container:
```bash
docker stop mkdocs-languagetool
```
