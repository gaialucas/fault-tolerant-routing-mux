# Copyright 2022 Lucas Gaia de Castro
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
# =============================================================================
"""Test suite for the routing resource graph parser."""
import pytest
import os
from fault_tolerant_routing_mux.rr_graph_parser import RRGraphParser

BASE_DIR = "tests/sample_files"
def test_no_file():
    with pytest.raises(TypeError):
        rrgp = RRGraphParser()

def test_empty_file():
    rrgp = RRGraphParser(os.path.join(BASE_DIR, "empty.xml"))
    mux_dict = rrgp.parse()
    assert not mux_dict

def test_minimal_file():
    rrgp = RRGraphParser(os.path.join(BASE_DIR, "minimal.xml"))
    expected_mux_dict = {10: [24678, 24680, 24681, 24682, 24684]}
    mux_dict = rrgp.parse()
    for k in mux_dict:
        assert mux_dict[k] == expected_mux_dict[k]
    # assert mux_dict.values() == expected_mux_dict.values()

def test_sample_file():
    rrgp = RRGraphParser(os.path.join(BASE_DIR, "simple.xml"))
    expected_mux_dict = {
        10: [24670, 24672, 24673, 24674, 24676, 24678, 24680, 24681, 24682, 24684],
        13: [24673, 24681, 24689, 24696, 24697, 24698, 24700, 24702, 24704]
    }
    mux_dict = rrgp.parse()
    for k in mux_dict:
        assert mux_dict[k] == expected_mux_dict[k]