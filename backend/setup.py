import os

from setuptools import find_packages, setup

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aida-crud",
    version="1.0.0",
    author="Gojjo Tech",
    author_email="admin@gojjotech.com",
    description="Advanced Intelligent Django API CRUD Framework - A comprehensive, DRY solution for building feature-rich CRUD operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hmesfin/aida-crud",
    project_urls={
        "Bug Tracker": "https://github.com/hmesfin/aida-crud/issues",
        "Documentation": "https://github.com/hmesfin/aida-crud#readme",
        "Source Code": "https://github.com/hmesfin/aida-crud",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2,<5.0",
        "djangorestframework>=3.12.0",
        "django-filter>=2.4.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-django>=4.5",
            "pytest-cov>=4.0",
            "black>=22.0",
            "ruff>=0.1.0",
            "isort>=5.10",
            "mypy>=1.0",
        ],
    },
    keywords="django rest api crud framework drf restful soft-delete audit bulk-operations",
    include_package_data=True,
    zip_safe=False,
)
