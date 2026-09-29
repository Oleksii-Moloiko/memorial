#!/usr/bin/env bash

set -Eeuo pipefail

cd "$(dirname "$0")"

BRANCH="develop"
PYTHON="./.venv/bin/python"
SETTINGS="config.settings.prod"

echo "==> Checking repository..."

CURRENT_BRANCH="$(git branch --show-current)"

if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "ERROR: Expected branch '$BRANCH', current branch is '$CURRENT_BRANCH'."
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "ERROR: Working tree is not clean."
    git status --short
    exit 1
fi

echo "==> Updating code..."
git pull --ff-only origin "$BRANCH"

echo "==> Installing dependencies..."
"$PYTHON" -m pip install -r requirements.txt

echo "==> Checking Django..."
"$PYTHON" manage.py check --settings="$SETTINGS"

echo "==> Checking for missing migrations..."
"$PYTHON" manage.py makemigrations \
    --check \
    --dry-run \
    --settings="$SETTINGS"

echo "==> Applying migrations..."
"$PYTHON" manage.py migrate \
    --noinput \
    --settings="$SETTINGS"

echo "==> Collecting static files..."
"$PYTHON" manage.py collectstatic \
    --noinput \
    --settings="$SETTINGS"

echo
echo "======================================"
echo "Deployment completed successfully."
echo "Restart Python application in ISPmanager."
echo "======================================"