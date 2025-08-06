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

import os
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional
from typing_extensions import TypedDict


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions in Kinesis operations.

    Wraps the function in a try-catch block and returns any exceptions
    in a standardized error format.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function that handles exceptions
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return {'error': str(e)}

    return wrapper


def mutation_check(func):
    """Decorator to block mutations if KINESIS-MCP-READONLY is set to true."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        readonly = os.environ.get('KINESIS-MCP-READONLY', '').lower()
        if readonly in ('true', '1', 'yes'):  # treat these as true
            return {'error': 'Mutation not allowed: KINESIS-MCP-READONLY is set to true.'}
        return await func(*args, **kwargs)

    return wrapper


# Type definitions for Kinesis Data Streams
ShardIteratorType = Literal[
    'AT_SEQUENCE_NUMBER',
    'AFTER_SEQUENCE_NUMBER', 
    'TRIM_HORIZON',
    'LATEST',
    'AT_TIMESTAMP'
]

StreamStatus = Literal['CREATING', 'DELETING', 'ACTIVE', 'UPDATING']
StreamModeDetails = Literal['PROVISIONED', 'ON_DEMAND']
ScalingType = Literal['UNIFORM_SCALING']
EncryptionType = Literal['NONE', 'KMS']
MetricsName = Literal[
    'IncomingRecords',
    'IncomingBytes', 
    'OutgoingRecords',
    'OutgoingBytes',
    'WriteProvisionedThroughputExceeded',
    'ReadProvisionedThroughputExceeded',
    'IncomingPutRecords',
    'IteratorAgeMilliseconds',
    'ALL'
]
ConsumerStatus = Literal['CREATING', 'DELETING', 'ACTIVE']


class StreamModeDetailsType(TypedDict, total=False):
    StreamMode: StreamModeDetails


class ShardLevelMetrics(TypedDict):
    MetricsNames: List[MetricsName]


class Tag(TypedDict):
    Key: str
    Value: str


class CreateStreamInput(TypedDict, total=False):
    StreamName: str  # required
    ShardCount: Optional[int]
    StreamModeDetails: Optional[StreamModeDetailsType]


class DeleteStreamInput(TypedDict):
    StreamName: str  # required
    EnforceConsumerDeletion: Optional[bool]


class DescribeStreamInput(TypedDict, total=False):
    StreamName: str  # required
    Limit: Optional[int]
    ExclusiveStartShardId: Optional[str]
    StreamARN: Optional[str]


class ListStreamsInput(TypedDict, total=False):
    Limit: Optional[int]
    ExclusiveStartStreamName: Optional[str]
    NextToken: Optional[str]


class UpdateShardCountInput(TypedDict):
    StreamName: str  # required
    TargetShardCount: int  # required
    ScalingType: ScalingType  # required


class PutRecordInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    Data: bytes  # required - The data blob to put into the record
    PartitionKey: str  # required
    ExplicitHashKey: Optional[str]
    SequenceNumberForOrdering: Optional[str]


class PutRecordsRequestEntry(TypedDict, total=False):
    Data: bytes  # required
    ExplicitHashKey: Optional[str]
    PartitionKey: str  # required


class PutRecordsInput(TypedDict, total=False):
    Records: List[PutRecordsRequestEntry]  # required
    StreamName: Optional[str]
    StreamARN: Optional[str]


class GetShardIteratorInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ShardId: str  # required
    ShardIteratorType: ShardIteratorType  # required
    StartingSequenceNumber: Optional[str]
    Timestamp: Optional[float]


class GetRecordsInput(TypedDict, total=False):
    ShardIterator: str  # required
    Limit: Optional[int]
    StreamARN: Optional[str]


class ListShardsInput(TypedDict, total=False):
    StreamName: Optional[str]
    NextToken: Optional[str]
    ExclusiveStartShardId: Optional[str]
    MaxResults: Optional[int]
    StreamCreationTimestamp: Optional[float]
    ShardFilter: Optional[Dict[str, Any]]
    StreamARN: Optional[str]


class MergeShardsInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ShardToMerge: str  # required
    AdjacentShardToMerge: str  # required


class SplitShardInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ShardToSplit: str  # required
    NewStartingHashKey: str  # required


class EnableEnhancedMonitoringInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ShardLevelMetrics: List[MetricsName]  # required


class DisableEnhancedMonitoringInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ShardLevelMetrics: List[MetricsName]  # required


class StartStreamEncryptionInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    EncryptionType: EncryptionType  # required
    KeyId: str  # required


class StopStreamEncryptionInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    EncryptionType: EncryptionType  # required
    KeyId: str  # required


class AddTagsToStreamInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    Tags: Dict[str, str]  # required


class RemoveTagsFromStreamInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    TagKeys: List[str]  # required


class ListTagsForStreamInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    ExclusiveStartTagKey: Optional[str]
    Limit: Optional[int]


class IncreaseStreamRetentionPeriodInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    RetentionPeriodHours: int  # required


class DecreaseStreamRetentionPeriodInput(TypedDict, total=False):
    StreamName: Optional[str]
    StreamARN: Optional[str]
    RetentionPeriodHours: int  # required


class RegisterStreamConsumerInput(TypedDict, total=False):
    StreamARN: str  # required
    ConsumerName: str  # required


class DeregisterStreamConsumerInput(TypedDict, total=False):
    StreamARN: Optional[str]
    ConsumerName: Optional[str]
    ConsumerARN: Optional[str]


class DescribeStreamConsumerInput(TypedDict, total=False):
    StreamARN: Optional[str]
    ConsumerName: Optional[str]
    ConsumerARN: Optional[str]


class ListStreamConsumersInput(TypedDict, total=False):
    StreamARN: str  # required
    NextToken: Optional[str]
    MaxResults: Optional[int]
    StreamCreationTimestamp: Optional[float]


class SubscribeToShardInput(TypedDict):
    ConsumerARN: str  # required
    ShardId: str  # required
    StartingPosition: Dict[str, Any]  # required


class DescribeStreamSummaryInput(TypedDict, total=False):
    StreamName: str  # required
    StreamARN: Optional[str]


class UpdateStreamModeInput(TypedDict, total=False):
    StreamARN: str  # required
    StreamModeDetails: StreamModeDetailsType  # required