# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-16

### Added
- Support for Django 5.0 and 5.1
- CHANGELOG.md for tracking version history

### Changed
- Updated Django dependency constraint from `<5.0` to `<6.0`
- Added Django 5.0 and 5.1 to framework classifiers

### Fixed
- Import errors when Django is not yet configured

## [1.0.0] - 2025-01-16

### Initial Release
- Generic CRUD viewsets with automatic configuration
- Dynamic serializers with context-aware field selection
- Advanced filtering, searching, and ordering
- Bulk operations (create, update, delete)
- Soft delete functionality with restore capabilities
- Comprehensive audit trail system
- Multi-format data export (CSV, JSON, Excel)
- API metadata endpoints for frontend auto-configuration
- Full test suite with pytest
- Vue.js frontend components (separate package)
- Complete documentation and examples