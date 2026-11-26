# Development

This section explains how to work on Adyn: the development tools, the checks
to run before calling something done, and the tests.


## Environment

Adyn runs from its folder with `python main.py`, inside `.venv`. It is not
installed as a package: `pyproject.toml` only holds the settings of the tools.

Install the development tools in the virtual environment:

```bash
pip install pytest ruff mypy types-requests
```


## Checks

Run these before calling a change done.

Compile every file, to catch syntax errors:

```bash
python -m compileall -q -x '\.venv' .
```

Run the tests:

```bash
pytest
```

Check the style and the imports:

```bash
ruff check .
```

Check the types:

```bash
mypy
```

| Tool | Settings |
| --- | --- |
| ruff | Lines of up to 80 columns, import groups, common bugs |
| mypy | Strict mode, over `cli`, `config`, `core`, `main.py` and `tests` |
| pytest | No cache folder, tests found from the project root |

Only use `ruff check`. The code is formatted by hand, so do not run
`ruff format` or `black` over it.


## Tests

The tests live in `tests/`, mirroring the packages:

```text
tests/
    cli/
        test_parser.py            Commands and arguments
    core/
        orchestrator/
            test_loader.py        Reading adyn.toml
            test_models.py        Validation of adyn.toml
        tools/
            burp/
                test_certificate.py   Android file name of the CA
```

They test pure logic and never touch a device, an emulator, Burp, Docker or
the network. Files go to `tmp_path`.


## Conventions

| Topic | Rule |
| --- | --- |
| Layout | One package per tool in `core/tools/`, each with its own `models.py` |
| Constants | In `config/`, split by area, never in the code |
| User settings | In `adyn.toml`, validated when it is loaded |
| Errors | Subclasses of `AdynError`, with lowercase messages |
| Functions | Public ones first, reading as a list of steps; private helpers below |
| Files | Downloads, logs and state go to `.adyn/`, never to the home folder |
| Formatting | Lines of up to 80 columns, formatted by hand |


## Related Pages

- [Architecture](../architecture/README.md)
