.PHONY: install update test run clean

# Define variables
SRC_DIR=src
TEST_DIR=tests
LINT_TARGETS=$(SRC_DIR) $(TEST_DIR)

# Run install job by default
default: install

# Install dependencies using Poetry
install:
	poetry install

# Update dependencies using Poetry
update:
	poetry update

# Run linters
lint:
	poetry run black $(LINT_TARGETS)
	poetry run isort $(LINT_TARGETS)

# Run tests
test:
	poetry run pytest $(TEST_DIR)

# Run the main script
run:
	poetry run python3 $(SRC_DIR)/main.py $(ARGS)

# Clean up the project
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
