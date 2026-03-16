#!/usr/bin/env bash
set -e
echo "Running ruff check..."
ruff check app/ tests/
echo "Running ruff format check..."
ruff format --check app/ tests/
echo "All checks passed!"
