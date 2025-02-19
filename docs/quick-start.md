# Quick start guide

This shows how to get a minimal spell checking setup running.

## Docker installation

You need to have docker installed and running:

- On macOS just download and start [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- For Linux install docker as described either on [dockers page](https://docs.docker.com/engine/install/) or follow instructions in your distro's wiki.
- For Windows you probably also want [Docker Desktop](https://www.docker.com/products/docker-desktop/), but I never used it before.

If you have docker compatible software like [Podman](https://podman.io/), it should work too.
But you need to specify the executable's name or path in your `mkdocs.yml` like this:
```yaml
plugins:
- languagetool:
    docker_binary: podman
```

## Plugin installation

You can install the plugin with pip:
```bash
pip install mkdocs-languagetool-plugin
```

## Enable the plugin

As with all MkDocs plugins, add it to your `mkdocs.yml`:
```yaml
plugins:
- search
- languagetool
```

If this is your ownly plugin you likely want to add the `search` plugin, since otherwise your site's search function will be disabled.

Now when you run `mkdocs serve` or `mkdocs build`, the plugin should start a local LanguageTool server with docker and use it to perform spellchecking.
The spell checking results will be output as colored text (ANSI colors) in the mkdocs output.
The first run may take a while (and require a lot of bandwith), since the docker image likely needs to be downloaded first.
