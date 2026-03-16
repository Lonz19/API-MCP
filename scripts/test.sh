#!/usr/bin/env bash
set -e
echo "Running tests with coverage..."
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
