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
"""Test suite for a routing mux block."""

from fault_tolerant_routing_mux.mux import RoutingMuxBlock
from fault_tolerant_routing_mux.control_cell import MemCell
from fault_tolerant_routing_mux.memristor_errors import Errors


TEST_SINK_NODE = 10
TEST_SRC_NODE_LIST = [0, 1, 2, 3, 4, 5, 6]

def test_no_failure():
    ctr_cell_list = [MemCell() for i in range(7)]
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    assert not rmb.get_defect_edges()  # empty list

def test_ud_in_block():
    ctr_cell_list = [MemCell() for i in range(7)]
    ctr_cell_list[0].setErrors(Errors.UD, Errors.UD)
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    rmb.computeBlockError()
    assert rmb.get_defect_edges()  == TEST_SRC_NODE_LIST  # all source nodes

def test_multiple_sa1():
    ctr_cell_list = [MemCell() for i in range(7)]
    ctr_cell_list[1].setErrors(Errors.FF, Errors.SA0)
    ctr_cell_list[2].setErrors(Errors.FF, Errors.SA0)
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    rmb.computeBlockError()
    assert rmb.get_defect_edges()  == TEST_SRC_NODE_LIST  # all source nodes

def test_single_sa1():
    ctr_cell_list = [MemCell() for i in range(7)]
    ctr_cell_list[3].setErrors(Errors.FF, Errors.SA0)
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    rmb.computeBlockError()
    assert rmb.get_defect_edges()  == [0, 1, 2, 4, 5, 6]  # all source nodes

def test_single_sa0():
    ctr_cell_list = [MemCell() for i in range(7)]
    ctr_cell_list[4].setErrors(Errors.FF, Errors.SA1)
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    rmb.computeBlockError()
    assert rmb.get_defect_edges()  == [4]  # all source nodes

def test_single_sa0():
    ctr_cell_list = [MemCell() for i in range(7)]
    ctr_cell_list[5].setErrors(Errors.FF, Errors.SA1)
    ctr_cell_list[6].setErrors(Errors.FF, Errors.SA1)
    rmb = RoutingMuxBlock(TEST_SRC_NODE_LIST, TEST_SINK_NODE, ctr_cell_list)
    rmb.computeBlockError()
    assert rmb.get_defect_edges()  == [5, 6]  # all source nodes