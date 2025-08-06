# AWS Kinesis MCP Server

The official MCP Server for interacting with AWS Kinesis Data Streams

This comprehensive server provides both operational Kinesis management and expert streaming architecture guidance, featuring 30+ operational tools for managing Kinesis streams, shards, records, consumers, and more, plus expert streaming design guidance.

## Available MCP Tools

### Design & Architecture
- `kinesis_streaming_architecture` - Retrieves the complete Kinesis Streaming Architecture Expert prompt

### Stream Operations
- `create_stream` - Creates a Kinesis data stream in PROVISIONED or ON_DEMAND mode
- `delete_stream` - Deletes a Kinesis data stream and all its shards and data
- `describe_stream` - Returns detailed information about a stream including shards, status, and configuration
- `describe_stream_summary` - Returns stream summary without shard details for basic info
- `list_streams` - Returns a list of Kinesis data streams in your account
- `update_stream_mode` - Updates the capacity mode between PROVISIONED and ON_DEMAND
- `update_shard_count` - Updates the shard count for PROVISIONED streams

### Shard Operations
- `list_shards` - Returns a list of shards in a Kinesis data stream
- `merge_shards` - Merges two adjacent shards in a PROVISIONED stream
- `split_shard` - Splits a shard into two new shards in a PROVISIONED stream

### Record Operations
- `put_record` - Writes a single data record into a Kinesis data stream
- `put_records` - Writes multiple data records into a Kinesis data stream in a single call
- `get_shard_iterator` - Gets a shard iterator for reading records from a specific shard
- `get_records` - Retrieves records from a Kinesis data stream shard using a shard iterator

### Consumer Operations
- `register_stream_consumer` - Registers a consumer with a stream for enhanced fan-out
- `deregister_stream_consumer` - Deregisters a consumer from a stream
- `describe_stream_consumer` - Returns information about a registered consumer
- `list_stream_consumers` - Lists the consumers registered with a stream

### Monitoring & Metrics
- `enable_enhanced_monitoring` - Enables enhanced monitoring for shard-level metrics
- `disable_enhanced_monitoring` - Disables enhanced monitoring for a stream

### Security & Encryption
- `start_stream_encryption` - Enables server-side encryption using AWS KMS
- `stop_stream_encryption` - Disables server-side encryption for a stream

### Retention & Lifecycle
- `increase_stream_retention_period` - Increases the retention period (24-8760 hours)
- `decrease_stream_retention_period` - Decreases the retention period (24-8760 hours)

### Tags
- `add_tags_to_stream` - Adds or updates tags for a Kinesis data stream
- `remove_tags_from_stream` - Removes tags from a stream
- `list_tags_for_stream` - Lists the tags for a stream

## Instructions

The official MCP Server for interacting with AWS Kinesis Data Streams provides a comprehensive set of tools for both designing and managing Kinesis streaming resources.

To use these tools, ensure you have proper AWS credentials configured with appropriate permissions for Kinesis operations. The server will automatically use credentials from environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) or other standard AWS credential sources.

All tools support an optional `region_name` parameter to specify which AWS region to operate in. If not provided, it will use the AWS_REGION environment variable or default to 'us-west-2'.

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. Set up AWS credentials with access to AWS services
   - Consider setting up Read-only permission if you don't want the LLM to modify any resources

## Installation

| Cursor | VS Code |
|:------:|:-------:|
| [![Install MCP Server](https://cursor.com/deeplink/mcp-install-light.svg)](https://cursor.com/install-mcp?name=awslabs.kinesis-mcp-server&config=eyJjb21tYW5kIjoidXZ4IGF3c2xhYnMua2luZXNpcy1tY3Atc2VydmVyQGxhdGVzdCIsImVudiI6eyJLSU5FU0lTLU1DUC1SRUFET05MWSI6InRydWUiLCJBV1NfUFJPRklMRSI6ImRlZmF1bHQiLCJBV1NfUkVHSU9OIjoidXMtd2VzdC0yIiwiRkFTVE1DUF9MT0dfTEVWRUwiOiJFUlJPUiJ9LCJkaXNhYmxlZCI6ZmFsc2UsImF1dG9BcHByb3ZlIjpbXX0%3D) | [![Install on VS Code](https://img.shields.io/badge/Install_on-VS_Code-FF9900?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=Kinesis%20MCP%20Server&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22awslabs.kinesis-mcp-server%40latest%22%5D%2C%22env%22%3A%7B%22KINESIS-MCP-READONLY%22%3A%22true%22%2C%22AWS_PROFILE%22%3A%22default%22%2C%22AWS_REGION%22%3A%22us-west-2%22%2C%22FASTMCP_LOG_LEVEL%22%3A%22ERROR%22%7D%2C%22disabled%22%3Afalse%2C%22autoApprove%22%3A%5B%5D%7D) |

Add the MCP to your favorite agentic tools. (e.g. for Amazon Q Developer CLI MCP, `~/.aws/amazonq/mcp.json`):

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

or docker after a successful `docker build -t awslabs/kinesis-mcp-server .`:

```json
  {
    "mcpServers": {
      "awslabs.kinesis-mcp-server": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "--interactive",
          "--env",
          "FASTMCP_LOG_LEVEL=ERROR",
          "awslabs/kinesis-mcp-server:latest"
        ],
        "env": {},
        "disabled": false,
        "autoApprove": []
      }
    }
  }
```