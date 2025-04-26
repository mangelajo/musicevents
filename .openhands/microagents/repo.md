# Python package

This repository uses uv, when adding packages to the repository, please
make sure to add it with `uv add <package>`. Then right after use
`uv pip compile --output-file requirements.txt` to update the requirements.txt.

# When modifying or extending templates
Use internationalization (i18n) for any text that will be displayed to the user, and update the files in the `locale` folder, for all the supported languages.

# Running python scripts
When running python scripts, use the `uv run` command.


# Testing
When changes are made, please make sure to run the tests with `make test`.

# Linting
Always run `make lint` before committing your changes to ensure that the code is properly formatted, fix any issues. `make lint-fix` can help with that.

