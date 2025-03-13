# kash-media-kit

See the main [kash](https://github.com/jlevy/kash) repo for general instructions.

To run media kit, ensure you have uv set up then:

```shell
# Install all deps and run tests:
make
# Run kash with media kit actions enabled:
uv run kash
```

## Installing uv and Python

This project is set up to use [**uv**](https://docs.astral.sh/uv/), the new package
manager for Python.

This is a quick cheat sheet for one of the simplest and most reliable ways to set up uv
and Python.

For macOS, if you have [brew](https://brew.sh/) installed, it's easy to install uv:

```shell
brew update
brew install uv
```

For Ubuntu:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See [uv's docs](https://docs.astral.sh/uv/getting-started/installation/) for other
platforms and installation methods.

`uv` replaces traditional use of `pyenv`, `pipx`, `poetry`, `pip`, etc.

Now you can use uv to install a current Python environment:

```shell
uv python install 3.13 # Or pick another version.
```

## Development

For development workflows, see [development.md](development.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
