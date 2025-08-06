#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import boto3
import os
from awslabs.kinesis_mcp_server.common import (
    AddTagsToStreamInput,
    CreateStreamInput,
    DecreaseStreamRetentionPeriodInput,
    DeleteStreamInput,
    DeregisterStreamConsumerInput,
    DescribeStreamConsumerInput,
    DescribeStreamInput,
    DescribeStreamSummaryInput,
    DisableEnhancedMonitoringInput,
    EnableEnhancedMonitoringInput,
    GetRecordsInput,
    GetShardIteratorInput,
    IncreaseStreamRetentionPeriodInput,
    ListShardsInput,
    ListStreamConsumersInput,
    ListStreamsInput,
    ListTagsForStreamInput,
    MergeShardsInput,
    MetricsName,
    PutRecordInput,
    PutRecordsInput,
    PutRecordsRequestEntry,
    RegisterStreamConsumerInput,
    RemoveTagsFromStreamInput,
    ShardIteratorType,
    SplitShardInput,
    StartStreamEncryptionInput,
    StopStreamEncryptionInput,
    StreamModeDetailsType,
    SubscribeToShardInput,
    Tag,
    UpdateShardCountInput,
    UpdateStreamModeInput,
    handle_exceptions,
    mutation_check,
)
from botocore.config import Config
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Any, Dict, List, Literal, Optional, Union


# Define server instructions and dependencies
SERVER_INSTRUCTIONS = """The official MCP Server for interacting with AWS Kinesis Data Streams

This server provides comprehensive Kinesis Data Streams capabilities with 30+ operational tools for managing
streams, shards, records, consumers, and more.

IMPORTANT: Data Encoding for Records
-----------------------------------
When putting records into Kinesis streams, the Data field must be bytes. The server will automatically
handle base64 encoding/decoding when needed. You can provide data as:
- String (will be UTF-8 encoded to bytes)
- Base64-encoded string (will be decoded to bytes)
- Raw bytes

For partition keys, use strings that will help distribute your data evenly across shards.

Stream Management:
- Streams can be in PROVISIONED mode (specify shard count) or ON_DEMAND mode (auto-scaling)
- Shard operations like split/merge are only available for PROVISIONED streams
- Enhanced monitoring provides detailed CloudWatch metrics at shard level

Consumer Management:
- Register consumers for enhanced fan-out (dedicated throughput per consumer)
- Use SubscribeToShard for real-time processing with enhanced fan-out consumers
- Standard consumers use GetRecords with shard iterators

All tools support an optional `region_name` parameter to specify which AWS region to operate in.
If not provided, it will use the AWS_REGION environment variable or default to 'us-west-2'.
"""

SERVER_DEPENDENCIES = [
    'boto3',
    'botocore',
    'pydantic',
]


def create_server():
    """Create and configure the MCP server instance."""
    return FastMCP(
        'awslabs.kinesis-mcp-server',
        instructions=SERVER_INSTRUCTIONS,
        dependencies=SERVER_DEPENDENCIES,
    )


app = create_server()


def get_kinesis_client(region_name: str | None):
    """Create a boto3 Kinesis client using credentials from environment variables."""
    # Use provided region, or get from env, or fall back to us-west-2
    region = region_name or os.getenv('AWS_REGION') or 'us-west-2'

    # Configure custom user agent to identify requests from LLM/MCP
    config = Config(user_agent_extra='MCP/KinesisServer')

    # Create a new session to force credentials to reload
    session = boto3.Session()

    return session.client('kinesis', region_name=region, config=config)


# Common field definitions
stream_name = Field(description='The name of the Kinesis data stream')
stream_arn = Field(default=None, description='The ARN of the Kinesis data stream')
region_name = Field(default=None, description='The AWS region to run the tool')


@app.tool()
@handle_exceptions
@mutation_check
async def create_stream(
    stream_name: str = stream_name,
    shard_count: int = Field(default=None, description='Number of shards for PROVISIONED mode', ge=1),
    stream_mode_details: StreamModeDetailsType = Field(
        default=None, description='Stream mode configuration (PROVISIONED or ON_DEMAND)'
    ),
    region_name: str = region_name,
) -> dict:
    """Creates a Kinesis data stream. You can create streams in PROVISIONED mode (specify shard count) or ON_DEMAND mode (auto-scaling)."""
    client = get_kinesis_client(region_name)
    params: CreateStreamInput = {'StreamName': stream_name}
    
    if shard_count:
        params['ShardCount'] = shard_count
    if stream_mode_details:
        params['StreamModeDetails'] = stream_mode_details
    
    response = client.create_stream(**params)
    return {'StreamName': stream_name, 'Status': 'CREATING'}


@app.tool()
@handle_exceptions
@mutation_check
async def delete_stream(
    stream_name: str = stream_name,
    enforce_consumer_deletion: bool = Field(
        default=None, description='Delete stream even if it has registered consumers'
    ),
    region_name: str = region_name,
) -> dict:
    """Deletes a Kinesis data stream and all its shards and data. This operation is irreversible."""
    client = get_kinesis_client(region_name)
    params: DeleteStreamInput = {'StreamName': stream_name}
    
    if enforce_consumer_deletion is not None:
        params['EnforceConsumerDeletion'] = enforce_consumer_deletion
    
    response = client.delete_stream(**params)
    return {'StreamName': stream_name, 'Status': 'DELETING'}


@app.tool()
@handle_exceptions
async def describe_stream(
    stream_name: str = stream_name,
    limit: int = Field(default=None, description='Maximum number of shards to return', ge=1, le=10000),
    exclusive_start_shard_id: str = Field(
        default=None, description='Shard ID to start listing from (for pagination)'
    ),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Returns detailed information about a Kinesis data stream including its shards, status, and configuration."""
    client = get_kinesis_client(region_name)
    params: DescribeStreamInput = {'StreamName': stream_name}
    
    if limit:
        params['Limit'] = limit
    if exclusive_start_shard_id:
        params['ExclusiveStartShardId'] = exclusive_start_shard_id
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.describe_stream(**params)
    return response['StreamDescription']


@app.tool()
@handle_exceptions
async def describe_stream_summary(
    stream_name: str = stream_name,
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Returns a summary of stream information without shard details. Faster than describe_stream for basic info."""
    client = get_kinesis_client(region_name)
    params: DescribeStreamSummaryInput = {'StreamName': stream_name}
    
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.describe_stream_summary(**params)
    return response['StreamDescriptionSummary']


@app.tool()
@handle_exceptions
async def list_streams(
    limit: int = Field(default=None, description='Maximum number of streams to return', ge=1, le=10000),
    exclusive_start_stream_name: str = Field(
        default=None, description='Stream name to start listing from (for pagination)'
    ),
    next_token: str = Field(default=None, description='Token for pagination'),
    region_name: str = region_name,
) -> dict:
    """Returns a list of Kinesis data streams in your account."""
    client = get_kinesis_client(region_name)
    params: ListStreamsInput = {}
    
    if limit:
        params['Limit'] = limit
    if exclusive_start_stream_name:
        params['ExclusiveStartStreamName'] = exclusive_start_stream_name
    if next_token:
        params['NextToken'] = next_token
    
    response = client.list_streams(**params)
    return {
        'StreamNames': response.get('StreamNames', []),
        'HasMoreStreams': response.get('HasMoreStreams', False),
        'NextToken': response.get('NextToken'),
        'StreamSummaries': response.get('StreamSummaries', [])
    }


@app.tool()
@handle_exceptions
async def list_shards(
    stream_name: str = Field(default=None, description='The name of the data stream'),
    next_token: str = Field(default=None, description='Token for pagination'),
    exclusive_start_shard_id: str = Field(
        default=None, description='Shard ID to start listing from'
    ),
    max_results: int = Field(default=None, description='Maximum number of shards to return', ge=1, le=10000),
    stream_creation_timestamp: float = Field(
        default=None, description='Timestamp when the stream was created (Unix timestamp)'
    ),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Returns a list of shards in a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: ListShardsInput = {}
    
    if stream_name:
        params['StreamName'] = stream_name
    if next_token:
        params['NextToken'] = next_token
    if exclusive_start_shard_id:
        params['ExclusiveStartShardId'] = exclusive_start_shard_id
    if max_results:
        params['MaxResults'] = max_results
    if stream_creation_timestamp:
        params['StreamCreationTimestamp'] = stream_creation_timestamp
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.list_shards(**params)
    return {
        'Shards': response.get('Shards', []),
        'NextToken': response.get('NextToken')
    }

@app.tool()
@handle_exceptions
@mutation_check
async def update_shard_count(
    stream_name: str = stream_name,
    target_shard_count: int = Field(description='The new number of shards', ge=1),
    scaling_type: Literal['UNIFORM_SCALING'] = Field(
        default='UNIFORM_SCALING', description='The scaling type (currently only UNIFORM_SCALING is supported)'
    ),
    region_name: str = region_name,
) -> dict:
    """Updates the shard count of a stream in PROVISIONED mode. Cannot be used with ON_DEMAND streams."""
    client = get_kinesis_client(region_name)
    params: UpdateShardCountInput = {
        'StreamName': stream_name,
        'TargetShardCount': target_shard_count,
        'ScalingType': scaling_type
    }
    
    response = client.update_shard_count(**params)
    return {
        'StreamName': response.get('StreamName'),
        'CurrentShardCount': response.get('CurrentShardCount'),
        'TargetShardCount': response.get('TargetShardCount')
    }


@app.tool()
@handle_exceptions
@mutation_check
async def update_stream_mode(
    stream_arn: str = Field(description='The ARN of the data stream'),
    stream_mode_details: StreamModeDetailsType = Field(
        description='The mode you want to change the stream to (PROVISIONED or ON_DEMAND)'
    ),
    region_name: str = region_name,
) -> dict:
    """Updates the capacity mode of a data stream. Can switch between PROVISIONED and ON_DEMAND modes."""
    client = get_kinesis_client(region_name)
    params: UpdateStreamModeInput = {
        'StreamARN': stream_arn,
        'StreamModeDetails': stream_mode_details
    }
    
    response = client.update_stream_mode(**params)
    return {'StreamARN': stream_arn, 'StreamModeDetails': stream_mode_details}


@app.tool()
@handle_exceptions
@mutation_check
async def put_record(
    data: Union[str, bytes] = Field(description='The data blob to put into the record'),
    partition_key: str = Field(description='Determines which shard the record goes to'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    explicit_hash_key: str = Field(
        default=None, description='Hash value to explicitly determine the shard'
    ),
    sequence_number_for_ordering: str = Field(
        default=None, description='Sequence number for ordering records'
    ),
    region_name: str = region_name,
) -> dict:
    """Writes a single data record into a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    
    # Handle data encoding
    if isinstance(data, str):
        try:
            # Try to decode as base64 first
            data_bytes = base64.b64decode(data)
        except:
            # If not base64, encode as UTF-8
            data_bytes = data.encode('utf-8')
    else:
        data_bytes = data
    
    params: PutRecordInput = {
        'Data': data_bytes,
        'PartitionKey': partition_key
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    if explicit_hash_key:
        params['ExplicitHashKey'] = explicit_hash_key
    if sequence_number_for_ordering:
        params['SequenceNumberForOrdering'] = sequence_number_for_ordering
    
    response = client.put_record(**params)
    return {
        'ShardId': response.get('ShardId'),
        'SequenceNumber': response.get('SequenceNumber'),
        'EncryptionType': response.get('EncryptionType')
    }


@app.tool()
@handle_exceptions
@mutation_check
async def put_records(
    records: List[Dict[str, Any]] = Field(
        description='List of records to put. Each record should have Data and PartitionKey fields'
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Writes multiple data records into a Kinesis data stream in a single call."""
    client = get_kinesis_client(region_name)
    
    # Process records to handle data encoding
    processed_records = []
    for record in records:
        data = record.get('Data')
        if isinstance(data, str):
            try:
                # Try to decode as base64 first
                data_bytes = base64.b64decode(data)
            except:
                # If not base64, encode as UTF-8
                data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        processed_record: PutRecordsRequestEntry = {
            'Data': data_bytes,
            'PartitionKey': record['PartitionKey']
        }
        
        if 'ExplicitHashKey' in record:
            processed_record['ExplicitHashKey'] = record['ExplicitHashKey']
        
        processed_records.append(processed_record)
    
    params: PutRecordsInput = {'Records': processed_records}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.put_records(**params)
    return {
        'FailedRecordCount': response.get('FailedRecordCount', 0),
        'Records': response.get('Records', []),
        'EncryptionType': response.get('EncryptionType')
    }


@app.tool()
@handle_exceptions
async def get_shard_iterator(
    shard_id: str = Field(description='The shard ID of the shard to get the iterator for'),
    shard_iterator_type: ShardIteratorType = Field(
        description='Determines how the shard iterator is used to start reading records'
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    starting_sequence_number: str = Field(
        default=None, description='Sequence number to start reading from (required for AT_SEQUENCE_NUMBER and AFTER_SEQUENCE_NUMBER)'
    ),
    timestamp: float = Field(
        default=None, description='Timestamp to start reading from (required for AT_TIMESTAMP)'
    ),
    region_name: str = region_name,
) -> dict:
    """Gets a shard iterator for reading records from a specific shard."""
    client = get_kinesis_client(region_name)
    params: GetShardIteratorInput = {
        'ShardId': shard_id,
        'ShardIteratorType': shard_iterator_type
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    if starting_sequence_number:
        params['StartingSequenceNumber'] = starting_sequence_number
    if timestamp:
        params['Timestamp'] = timestamp
    
    response = client.get_shard_iterator(**params)
    return {'ShardIterator': response.get('ShardIterator')}


@app.tool()
@handle_exceptions
async def get_records(
    shard_iterator: str = Field(description='The shard iterator returned by get_shard_iterator'),
    limit: int = Field(default=None, description='Maximum number of records to return', ge=1, le=10000),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Retrieves records from a Kinesis data stream shard using a shard iterator."""
    client = get_kinesis_client(region_name)
    params: GetRecordsInput = {'ShardIterator': shard_iterator}
    
    if limit:
        params['Limit'] = limit
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.get_records(**params)
    
    # Decode record data for easier consumption
    records = response.get('Records', [])
    for record in records:
        if 'Data' in record:
            try:
                # Try to decode as UTF-8 string
                record['DataString'] = record['Data'].decode('utf-8')
            except UnicodeDecodeError:
                # If not UTF-8, provide base64 encoded version
                record['DataBase64'] = base64.b64encode(record['Data']).decode('utf-8')
    
    return {
        'Records': records,
        'NextShardIterator': response.get('NextShardIterator'),
        'MillisBehindLatest': response.get('MillisBehindLatest')
    }


@app.tool()
@handle_exceptions
@mutation_check
async def merge_shards(
    shard_to_merge: str = Field(description='The shard ID of the shard to merge'),
    adjacent_shard_to_merge: str = Field(description='The shard ID of the adjacent shard to merge'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Merges two adjacent shards in a Kinesis data stream. Only available for PROVISIONED streams."""
    client = get_kinesis_client(region_name)
    params: MergeShardsInput = {
        'ShardToMerge': shard_to_merge,
        'AdjacentShardToMerge': adjacent_shard_to_merge
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.merge_shards(**params)
    return {'Status': 'Merge initiated'}


@app.tool()
@handle_exceptions
@mutation_check
async def split_shard(
    shard_to_split: str = Field(description='The shard ID of the shard to split'),
    new_starting_hash_key: str = Field(description='Hash key value for the new shard'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Splits a shard into two new shards in a Kinesis data stream. Only available for PROVISIONED streams."""
    client = get_kinesis_client(region_name)
    params: SplitShardInput = {
        'ShardToSplit': shard_to_split,
        'NewStartingHashKey': new_starting_hash_key
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.split_shard(**params)
    return {'Status': 'Split initiated'}


@app.tool()
@handle_exceptions
@mutation_check
async def enable_enhanced_monitoring(
    shard_level_metrics: List[MetricsName] = Field(
        description='List of shard-level metrics to enable'
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Enables enhanced monitoring for a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: EnableEnhancedMonitoringInput = {'ShardLevelMetrics': shard_level_metrics}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.enable_enhanced_monitoring(**params)
    return {
        'StreamName': response.get('StreamName'),
        'CurrentShardLevelMetrics': response.get('CurrentShardLevelMetrics', []),
        'DesiredShardLevelMetrics': response.get('DesiredShardLevelMetrics', [])
    }


@app.tool()
@handle_exceptions
@mutation_check
async def disable_enhanced_monitoring(
    shard_level_metrics: List[MetricsName] = Field(
        description='List of shard-level metrics to disable'
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Disables enhanced monitoring for a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: DisableEnhancedMonitoringInput = {'ShardLevelMetrics': shard_level_metrics}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.disable_enhanced_monitoring(**params)
    return {
        'StreamName': response.get('StreamName'),
        'CurrentShardLevelMetrics': response.get('CurrentShardLevelMetrics', []),
        'DesiredShardLevelMetrics': response.get('DesiredShardLevelMetrics', [])
    }


@app.tool()
@handle_exceptions
@mutation_check
async def start_stream_encryption(
    encryption_type: Literal['KMS'] = Field(default='KMS', description='The encryption type to use'),
    key_id: str = Field(description='The GUID for the customer-managed AWS KMS key or alias'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Enables server-side encryption for a Kinesis data stream using AWS KMS."""
    client = get_kinesis_client(region_name)
    params: StartStreamEncryptionInput = {
        'EncryptionType': encryption_type,
        'KeyId': key_id
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.start_stream_encryption(**params)
    return {'Status': 'Encryption started'}


@app.tool()
@handle_exceptions
@mutation_check
async def stop_stream_encryption(
    encryption_type: Literal['KMS'] = Field(default='KMS', description='The encryption type to disable'),
    key_id: str = Field(description='The GUID for the customer-managed AWS KMS key or alias'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Disables server-side encryption for a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: StopStreamEncryptionInput = {
        'EncryptionType': encryption_type,
        'KeyId': key_id
    }
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.stop_stream_encryption(**params)
    return {'Status': 'Encryption stopped'}


@app.tool()
@handle_exceptions
@mutation_check
async def add_tags_to_stream(
    tags: Dict[str, str] = Field(description='A dictionary of tag key-value pairs to add'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Adds or updates tags for a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: AddTagsToStreamInput = {'Tags': tags}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.add_tags_to_stream(**params)
    return {'Status': 'Tags added successfully'}


@app.tool()
@handle_exceptions
@mutation_check
async def remove_tags_from_stream(
    tag_keys: List[str] = Field(description='List of tag keys to remove'),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Removes tags from a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: RemoveTagsFromStreamInput = {'TagKeys': tag_keys}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.remove_tags_from_stream(**params)
    return {'Status': 'Tags removed successfully'}


@app.tool()
@handle_exceptions
async def list_tags_for_stream(
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    exclusive_start_tag_key: str = Field(
        default=None, description='Tag key to start listing from (for pagination)'
    ),
    limit: int = Field(default=None, description='Maximum number of tags to return', ge=1, le=50),
    region_name: str = region_name,
) -> dict:
    """Lists the tags for a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: ListTagsForStreamInput = {}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    if exclusive_start_tag_key:
        params['ExclusiveStartTagKey'] = exclusive_start_tag_key
    if limit:
        params['Limit'] = limit
    
    response = client.list_tags_for_stream(**params)
    return {
        'Tags': response.get('Tags', []),
        'HasMoreTags': response.get('HasMoreTags', False)
    }


@app.tool()
@handle_exceptions
@mutation_check
async def increase_stream_retention_period(
    retention_period_hours: int = Field(
        description='New retention period in hours (24-8760)', ge=24, le=8760
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Increases the retention period of a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: IncreaseStreamRetentionPeriodInput = {'RetentionPeriodHours': retention_period_hours}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.increase_stream_retention_period(**params)
    return {'Status': 'Retention period increased'}


@app.tool()
@handle_exceptions
@mutation_check
async def decrease_stream_retention_period(
    retention_period_hours: int = Field(
        description='New retention period in hours (24-8760)', ge=24, le=8760
    ),
    stream_name: str = Field(default=None, description='The name of the stream'),
    stream_arn: str = stream_arn,
    region_name: str = region_name,
) -> dict:
    """Decreases the retention period of a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: DecreaseStreamRetentionPeriodInput = {'RetentionPeriodHours': retention_period_hours}
    
    if stream_name:
        params['StreamName'] = stream_name
    if stream_arn:
        params['StreamARN'] = stream_arn
    
    response = client.decrease_stream_retention_period(**params)
    return {'Status': 'Retention period decreased'}


@app.tool()
@handle_exceptions
@mutation_check
async def register_stream_consumer(
    stream_arn: str = Field(description='The ARN of the Kinesis data stream'),
    consumer_name: str = Field(description='Name for the consumer'),
    region_name: str = region_name,
) -> dict:
    """Registers a consumer with a Kinesis data stream for enhanced fan-out."""
    client = get_kinesis_client(region_name)
    params: RegisterStreamConsumerInput = {
        'StreamARN': stream_arn,
        'ConsumerName': consumer_name
    }
    
    response = client.register_stream_consumer(**params)
    return response.get('Consumer', {})


@app.tool()
@handle_exceptions
@mutation_check
async def deregister_stream_consumer(
    stream_arn: str = Field(default=None, description='The ARN of the Kinesis data stream'),
    consumer_name: str = Field(default=None, description='Name of the consumer to deregister'),
    consumer_arn: str = Field(default=None, description='ARN of the consumer to deregister'),
    region_name: str = region_name,
) -> dict:
    """Deregisters a consumer from a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: DeregisterStreamConsumerInput = {}
    
    if stream_arn:
        params['StreamARN'] = stream_arn
    if consumer_name:
        params['ConsumerName'] = consumer_name
    if consumer_arn:
        params['ConsumerARN'] = consumer_arn
    
    response = client.deregister_stream_consumer(**params)
    return {'Status': 'Consumer deregistered'}


@app.tool()
@handle_exceptions
async def describe_stream_consumer(
    stream_arn: str = Field(default=None, description='The ARN of the Kinesis data stream'),
    consumer_name: str = Field(default=None, description='Name of the consumer'),
    consumer_arn: str = Field(default=None, description='ARN of the consumer'),
    region_name: str = region_name,
) -> dict:
    """Returns information about a registered consumer."""
    client = get_kinesis_client(region_name)
    params: DescribeStreamConsumerInput = {}
    
    if stream_arn:
        params['StreamARN'] = stream_arn
    if consumer_name:
        params['ConsumerName'] = consumer_name
    if consumer_arn:
        params['ConsumerARN'] = consumer_arn
    
    response = client.describe_stream_consumer(**params)
    return response.get('ConsumerDescription', {})


@app.tool()
@handle_exceptions
async def list_stream_consumers(
    stream_arn: str = Field(description='The ARN of the Kinesis data stream'),
    next_token: str = Field(default=None, description='Token for pagination'),
    max_results: int = Field(default=None, description='Maximum number of consumers to return', ge=1, le=10000),
    stream_creation_timestamp: float = Field(
        default=None, description='Timestamp when the stream was created (Unix timestamp)'
    ),
    region_name: str = region_name,
) -> dict:
    """Lists the consumers registered with a Kinesis data stream."""
    client = get_kinesis_client(region_name)
    params: ListStreamConsumersInput = {'StreamARN': stream_arn}
    
    if next_token:
        params['NextToken'] = next_token
    if max_results:
        params['MaxResults'] = max_results
    if stream_creation_timestamp:
        params['StreamCreationTimestamp'] = stream_creation_timestamp
    
    response = client.list_stream_consumers(**params)
    return {
        'Consumers': response.get('Consumers', []),
        'NextToken': response.get('NextToken')
    }


def main():
    """Main entry point for the server."""
    app.run()


if __name__ == '__main__':
    main()