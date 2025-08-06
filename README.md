# AWS Kinesis Data Streams MCP Server

The official MCP Server for interacting with AWS Kinesis Data Streams

This comprehensive server provides operational Kinesis Data Streams management with 30+ tools for managing streams, shards, records, consumers, and more.

## Available MCP Tools

### Stream Management
- `create_stream` - Creates a Kinesis data stream in PROVISIONED or ON_DEMAND mode
- `delete_stream` - Deletes a Kinesis data stream and all its shards and data
- `describe_stream` - Returns detailed information about a stream including shards, status, and configuration
- `describe_stream_summary` - Returns a summary of stream information without shard details
- `list_streams` - Returns a list of Kinesis data streams in your account
- `update_shard_count` - Updates the shard count of a stream in PROVISIONED mode
- `update_stream_mode` - Updates the capacity mode of a data stream (PROVISIONED/ON_DEMAND)

### Shard Management
- `list_shards` - Returns a list of shards in a Kinesis data stream
- `merge_shards` - Merges two adjacent shards (PROVISIONED streams only)
- `split_shard` - Splits a shard into two new shards (PROVISIONED streams only)

### Record Operations
- `put_record` - Writes a single data record into a Kinesis data stream
- `put_records` - Writes multiple data records into a stream in a single call
- `get_shard_iterator` - Gets a shard iterator for reading records from a specific shard
- `get_records` - Retrieves records from a shard using a shard iterator

### Consumer Management (Enhanced Fan-out)
- `register_stream_consumer` - Registers a consumer with a stream for enhanced fan-out
- `deregister_stream_consumer` - Deregisters a consumer from a stream
- `describe_stream_consumer` - Returns information about a registered consumer
- `list_stream_consumers` - Lists the consumers registered with a stream

### Monitoring and Metrics
- `enable_enhanced_monitoring` - Enables enhanced monitoring for detailed CloudWatch metrics
- `disable_enhanced_monitoring` - Disables enhanced monitoring

### Encryption
- `start_stream_encryption` - Enables server-side encryption using AWS KMS
- `stop_stream_encryption` - Disables server-side encryption

### Tags
- `add_tags_to_stream` - Adds or updates tags for a stream
- `remove_tags_from_stream` - Removes tags from a stream
- `list_tags_for_stream` - Lists the tags for a stream

### Retention
- `increase_stream_retention_period` - Increases the retention period (24-8760 hours)
- `decrease_stream_retention_period` - Decreases the retention period (24-8760 hours)

## Instructions

The official MCP Server for interacting with AWS Kinesis Data Streams provides a comprehensive set of tools for managing Kinesis streams and processing real-time data.

To use these tools, ensure you have proper AWS credentials configured with appropriate permissions for Kinesis operations. The server will automatically use credentials from environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) or other standard AWS credential sources.

All tools support an optional `region_name` parameter to specify which AWS region to operate in. If not provided, it will use the AWS_REGION environment variable or default to 'us-west-2'.

### Key Concepts

**Stream Modes:**
- **PROVISIONED**: You specify the number of shards and pay for provisioned capacity
- **ON_DEMAND**: Auto-scaling mode where AWS manages capacity based on throughput

**Data Encoding:**
- Records can contain string or binary data
- The server automatically handles UTF-8 encoding and base64 encoding/decoding
- Partition keys determine which shard records are written to

**Enhanced Fan-out:**
- Register consumers for dedicated throughput (2 MB/s per consumer per shard)
- Use for applications requiring low latency and high throughput

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. Set up AWS credentials with access to Kinesis Data Streams
   - Consider setting up Read-only permission if you don't want the LLM to modify any resources

## Installation

Add the MCP to your favorite agentic tools:

```json
{
  "mcpServers": {
    "awslabs.kinesis-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.kinesis-mcp-server@latest"],
      "env": {
        "KINESIS-MCP-READONLY": "true",
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-west-2",
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Environment Variables

- `KINESIS-MCP-READONLY`: Set to "true" to prevent any mutation operations
- `AWS_PROFILE`: AWS profile to use for authentication
- `AWS_REGION`: AWS region to use (defaults to us-west-2)
- `FASTMCP_LOG_LEVEL`: Logging level (ERROR, INFO, DEBUG)

## Examples

### Creating a Stream
```python
# Create a provisioned stream with 2 shards
create_stream(
    stream_name="my-stream",
    shard_count=2,
    stream_mode_details={"StreamMode": "PROVISIONED"}
)

# Create an on-demand stream
create_stream(
    stream_name="my-on-demand-stream",
    stream_mode_details={"StreamMode": "ON_DEMAND"}
)
```

### Putting Records
```python
# Put a single record
put_record(
    stream_name="my-stream",
    data="Hello, Kinesis!",
    partition_key="user123"
)

# Put multiple records
put_records(
    stream_name="my-stream",
    records=[
        {"Data": "Record 1", "PartitionKey": "key1"},
        {"Data": "Record 2", "PartitionKey": "key2"}
    ]
)
```

### Reading Records
```python
# Get shard iterator
iterator_response = get_shard_iterator(
    stream_name="my-stream",
    shard_id="shardId-000000000000",
    shard_iterator_type="LATEST"
)

# Get records
records_response = get_records(
    shard_iterator=iterator_response["ShardIterator"],
    limit=100
)
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.