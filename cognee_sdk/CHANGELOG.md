# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-07

### Added

- Initial release of Cognee Python SDK
- Core API methods:
  - `add()` - Add data to datasets
  - `delete()` - Delete data
  - `cognify()` - Process data into knowledge graphs
  - `search()` - Search knowledge graphs with 19 search types
  - `list_datasets()` - List all datasets
  - `create_dataset()` - Create new datasets
- Dataset management API:
  - `update()` - Update existing data
  - `delete_dataset()` - Delete datasets
  - `get_dataset_data()` - Get data items in dataset
  - `get_dataset_graph()` - Get knowledge graph data
  - `get_dataset_status()` - Get processing status
  - `download_raw_data()` - Download raw data files
- Authentication API:
  - `login()` - User login
  - `register()` - User registration
  - `get_current_user()` - Get current user info
- Memify API:
  - `memify()` - Enrich knowledge graphs
  - `get_search_history()` - Get search history
- Visualization API:
  - `visualize()` - Generate HTML visualization
- Sync API:
  - `sync_to_cloud()` - Sync to Cognee Cloud
  - `get_sync_status()` - Get sync status
- WebSocket support:
  - `subscribe_cognify_progress()` - Real-time progress updates
- Advanced features:
  - `add_batch()` - Batch data operations
  - Automatic retry with exponential backoff
  - Connection pooling
  - Comprehensive error handling
- Type safety:
  - Full type hints
  - Pydantic data models
  - PEP 561 support
- Testing:
  - Comprehensive unit tests
  - Example code
- Documentation:
  - README with examples
  - API documentation
  - Code examples

### Features

- Lightweight SDK (~5-10MB vs 500MB-2GB for full library)
- Fully asynchronous API
- Support for multiple file formats
- Automatic MIME type detection
- Request retry mechanism
- Connection pooling for performance

