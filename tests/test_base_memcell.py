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
"""Test suite for each control cell architecture."""
import pytest
from fault_tolerant_routing_mux.memristor_errors import Errors
from fault_tolerant_routing_mux.control_cell import MemCell

def test_base_arch_init():
    test_cell = MemCell()
    assert test_cell.getCellError() == Errors.FF

def test_base_arch_sa0():
    test_cell = MemCell()

    # Pull-Down SA1, Pull-Up ok
    test_cell.setErrors(Errors.FF, Errors.SA1)
    assert test_cell.getCellError() == Errors.SA0

    # Pull-Up SA0, Pull-Up ok or SA1
    test_cell.setErrors(Errors.SA0, Errors.FF)
    assert test_cell.getCellError() == Errors.SA0
    test_cell.setErrors(Errors.SA0, Errors.SA1)
    assert test_cell.getCellError() == Errors.SA0

def test_base_arch_sa1():
    test_cell = MemCell()

    # Pull-Down SA0, Pull-Up ok
    test_cell.setErrors(Errors.FF, Errors.SA0)
    assert test_cell.getCellError() == Errors.SA1

    # Pull-Up SA1, Pull-Up ok or SA0
    test_cell.setErrors(Errors.SA1, Errors.FF)
    assert test_cell.getCellError() == Errors.SA1
    test_cell.setErrors(Errors.SA1, Errors.SA0)
    assert test_cell.getCellError() == Errors.SA1

def test_base_arch_ud():
    test_cell = MemCell()

    # Pull-Down UD, Pull-Up any
    test_cell.setErrors(Errors.FF, Errors.UD)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.SA0, Errors.UD)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.SA1, Errors.UD)
    assert test_cell.getCellError() == Errors.UD

    # Pull-Up UD, Pull-down any
    test_cell.setErrors(Errors.UD, Errors.FF)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.UD, Errors.SA0)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.UD, Errors.SA1)
    assert test_cell.getCellError() == Errors.UD

    # Same error Pull-Down and Pull-Up
    test_cell.setErrors(Errors.SA1, Errors.SA1)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.SA0, Errors.SA0)
    assert test_cell.getCellError() == Errors.UD
    test_cell.setErrors(Errors.UD, Errors.UD)
    assert test_cell.getCellError() == Errors.UD
