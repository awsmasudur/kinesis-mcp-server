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

import pytest
from unittest.mock import Mock, patch
from awslabs.kinesis_mcp_server.server import get_kinesis_client, create_server


def test_create_server():
    """Test that the server can be created successfully."""
    server = create_server()
    assert server is not None
    assert server.name == 'awslabs.kinesis-mcp-server'


@patch('boto3.Session')
def test_get_kinesis_client_default_region(mock_session):
    """Test that get_kinesis_client uses default region when none provided."""
    mock_client = Mock()
    mock_session_instance = Mock()
    mock_session_instance.client.return_value = mock_client
    mock_session.return_value = mock_session_instance
    
    client = get_kinesis_client(None)
    
    mock_session_instance.client.assert_called_once()
    call_args = mock_session_instance.client.call_args
    assert call_args[0][0] == 'kinesis'
    assert 'region_name' in call_args[1]


@patch('boto3.Session')
def test_get_kinesis_client_custom_region(mock_session):
    """Test that get_kinesis_client uses provided region."""
    mock_client = Mock()
    mock_session_instance = Mock()
    mock_session_instance.client.return_value = mock_client
    mock_session.return_value = mock_session_instance
    
    client = get_kinesis_client('us-east-1')
    
    mock_session_instance.client.assert_called_once()
    call_args = mock_session_instance.client.call_args
    assert call_args[1]['region_name'] == 'us-east-1'


@patch.dict('os.environ', {'AWS_REGION': 'eu-west-1'})
@patch('boto3.Session')
def test_get_kinesis_client_env_region(mock_session):
    """Test that get_kinesis_client uses AWS_REGION environment variable."""
    mock_client = Mock()
    mock_session_instance = Mock()
    mock_session_instance.client.return_value = mock_client
    mock_session.return_value = mock_session_instance
    
    client = get_kinesis_client(None)
    
    mock_session_instance.client.assert_called_once()
    call_args = mock_session_instance.client.call_args
    assert call_args[1]['region_name'] == 'eu-west-1'