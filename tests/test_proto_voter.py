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
from fault_tolerant_routing_mux.control_cell import ProtoVoterCell

def test_base_arch_init():
    test_cell = ProtoVoterCell()
    assert test_cell.get_cell_error() == Errors.FF


def test_base_arch_ff():
    test_cell = ProtoVoterCell()
    # Main (mce) and Control Cell Errors (cce)
    mce = [Errors.FF, Errors.FF]
    cce = [Errors.FF, Errors.FF]

    # mc FF, cc FF
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.FF

    # mc FF, cc SA1
    cce = [Errors.SA1, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.FF

    # mc SA1, cc FF
    mce = [Errors.SA1, Errors.FF]
    cce = [Errors.FF, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.FF

def test_base_arch_sa0():
    test_cell = ProtoVoterCell()

    # mc FF, cc SA0
    mce = [Errors.FF, Errors.FF]
    cce = [Errors.SA0, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc FF, cc UD
    cce = [Errors.UD, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc SA0, cc UD
    mce = [Errors.SA0, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc SA0, cc SA1
    cce = [Errors.SA1, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc SA0, cc FF
    cce = [Errors.FF, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc SA0, cc SA0
    cce = [Errors.SA0, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc SA1, cc SA0
    mce = [Errors.SA1, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc UD, cc SA0
    mce = [Errors.UD, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0

    # mc UD, cc FF
    cce = [Errors.FF, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA0


def test_base_arch_sa1():
    test_cell = ProtoVoterCell()

    # mc SA1, cc SA1
    mce = [Errors.SA1, Errors.FF]
    cce = [Errors.SA1, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.SA1

def test_base_arch_ud():
    test_cell = ProtoVoterCell()

    # mc SA1, cc UD
    mce = [Errors.SA1, Errors.FF]
    cce = [Errors.UD, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.UD

    # mc UD, cc UD
    mce = [Errors.UD, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.UD

    # mc UD, cc SA1
    cce = [Errors.SA1, Errors.FF]
    test_cell.set_errors(mce, cce)
    assert test_cell.get_cell_error() == Errors.UD
