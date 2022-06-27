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
"""Test suite for a routing mux."""

from fault_tolerant_routing_mux.control_cell import MemCell
from fault_tolerant_routing_mux.memristor_errors import Errors
from fault_tolerant_routing_mux.mux import RoutingMux


TEST_SINK_NODE = 20
TEST_SRC_NODE_LIST = [i for i in range(16)]

def test_init_optimal_size():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    assert rm.optimal_block_size == 4

def test_build_mux():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    assert len(rm.first_stage_blocks) == 4
    assert len(rm.cell_list) == 8
    assert rm.first_stage_blocks[0].src_node_list == [i for i in range(4)]
    assert rm.first_stage_blocks[1].src_node_list == [i for i in range(4, 8)]
    assert rm.first_stage_blocks[2].src_node_list == [i for i in range(8, 12)]
    assert rm.first_stage_blocks[3].src_node_list == [i for i in range(12, 16)]
    assert rm.second_stage_block.sink_node == 20

def test_no_defect():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {}

def test_first_stage_sa0():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[0].setErrors(Errors.FF, Errors.SA1)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {0, 4, 8, 12}}

def test_second_stage_sa0():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[4].setErrors(Errors.FF, Errors.SA1)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {0, 1, 2, 3}}

def test_first_stage_sa1():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[2].setErrors(Errors.FF, Errors.SA0)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {0, 1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15}}

def test_second_stage_sa1():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[6].setErrors(Errors.FF, Errors.SA0)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {0, 1, 2, 3, 4, 5, 6, 7, 12, 13, 14, 15}}

def test_first_stage_multiple_sa1():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[1].setErrors(Errors.FF, Errors.SA0)
    rm.cell_list[3].setErrors(Errors.FF, Errors.SA0)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {i for i in range(16)}}

def test_second_stage_multiple_sa1():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[5].setErrors(Errors.FF, Errors.SA0)
    rm.cell_list[7].setErrors(Errors.FF, Errors.SA0)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {i for i in range(16)}}

def test_first_stage_ud():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[1].setErrors(Errors.FF, Errors.UD)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {i for i in range(16)}}

def test_second_stage_ud():
    rm = RoutingMux(TEST_SINK_NODE, TEST_SRC_NODE_LIST, MemCell)
    rm.cell_list[5].setErrors(Errors.FF, Errors.UD)
    rm.computeBlockErrors()
    assert rm.get_defect_edges() == {20: {i for i in range(16)}}
