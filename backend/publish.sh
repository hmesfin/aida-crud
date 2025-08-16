#!/bin/bash

# AIDA-CRUD PyPI Publishing Script
# =================================

set -e

echo "🚀 Publishing AIDA-CRUD to PyPI"
echo "================================"

# Clean previous builds
echo "📦 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "🔨 Building distribution packages..."
python -m build

# Check the package
echo "✅ Checking package quality..."
twine check dist/*

# Test upload (optional)
read -p "Do you want to upload to Test PyPI first? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "📤 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Test upload complete!"
    echo "Test your package with: pip install -i https://test.pypi.org/simple/ aida-crud"
    read -p "Press enter to continue with production upload..."
fi

# Production upload
echo "📤 Uploading to PyPI..."
echo "Note: You'll need your PyPI API token."
echo "Get one at: https://pypi.org/manage/account/token/"
twine upload dist/*

echo "✅ Package published successfully!"
echo "Install with: pip install aida-crud"