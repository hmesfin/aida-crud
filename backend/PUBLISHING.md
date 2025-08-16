# Publishing AIDA-CRUD to PyPI

## Prerequisites

1. **PyPI Account**: Create an account at <https://pypi.org/account/register/>
2. **API Token**: Generate an API token at <https://pypi.org/manage/account/token/>
3. **Install Tools**: Ensure you have `build` and `twine` installed:

   ```bash
   pip install build twine
   ```

## Publishing Steps

### Option 1: Using the Publish Script

```bash
./publish.sh
```

This script will:

- Clean previous builds
- Build the distribution packages
- Check package quality
- Optionally upload to Test PyPI first
- Upload to production PyPI

### Option 2: Manual Publishing

1. **Clean previous builds**:

   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

2. **Build the package**:

   ```bash
   python -m build
   ```

3. **Check the package**:

   ```bash
   twine check dist/*
   ```

4. **Upload to Test PyPI (optional)**:

   ```bash
   twine upload --repository testpypi dist/*
   ```

   Test installation:

   ```bash
   pip install -i https://test.pypi.org/simple/ aida-crud
   ```

5. **Upload to Production PyPI**:

   ```bash
   twine upload dist/*
   ```

## Authentication

### Using API Token (Recommended)

When prompted for credentials:

- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### Using .pypirc File

Create `~/.pypirc` with your credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

**Note**: Keep your `.pypirc` file secure and never commit it to version control!

## Version Management

Before publishing a new version:

1. Update version in `setup.py` and `pyproject.toml`
2. Update version in `aida_crud/__init__.py`
3. Update CHANGELOG.md (if exists)
4. Commit changes: `git commit -m "Bump version to X.Y.Z"`
5. Tag the release: `git tag vX.Y.Z`
6. Push tags: `git push origin --tags`

## Post-Publishing

After successful publishing:

1. **Verify Installation**:

   ```bash
   pip install aida-crud
   python -c "import aida_crud; print(aida_crud.__version__)"
   ```

2. **Update Documentation**: Update README with the latest version badge

3. **Create GitHub Release**: Go to <https://github.com/hmesfin/aida-crud/releases/new>

## Troubleshooting

### "Package already exists" Error

- You cannot overwrite an existing version on PyPI
- Bump the version number and try again

### Authentication Failed

- Ensure you're using `__token__` as username
- Check that your API token is correct
- Make sure the token has the correct scope (entire account or project-specific)

### Package Not Found After Upload

- PyPI may take a few minutes to index new packages
- Try again after 5-10 minutes

## Support

For issues, please create an issue at: <https://github.com/hmesfin/aida-crud/issues>
