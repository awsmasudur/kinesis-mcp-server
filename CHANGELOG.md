# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-08

### Added
- Initial release of AWS Kinesis Data Streams MCP Server
- Complete implementation of Kinesis Data Streams API
- Stream management tools (create, delete, describe, list, update)
- Shard management tools (list, merge, split, update count)
- Record operations (put_record, put_records, get_records, get_shard_iterator)
- Consumer management for enhanced fan-out
- Enhanced monitoring controls
- Encryption management (start/stop stream encryption)
- Tag management (add, remove, list tags)
- Retention period management
- Support for both PROVISIONED and ON_DEMAND stream modes
- Automatic data encoding/decoding for records
- Comprehensive error handling and mutation protection
- Read-only mode support via KINESIS-MCP-READONLY environment variable