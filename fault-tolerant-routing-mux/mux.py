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
"""Mux representations."""
from .control_cell import ProtoVoterCell
from .memristor_errors import Errors, RandomErrorGen


class RoutingMuxBlock():
    """Representation of a mux block."""

    def __init__(self, ctrCellList) -> None:
        """Initialize block as error-free and with all valid inputs."""
        self.ctrCellList = ctrCellList
        # self.dependencyDict = dependencyDict
        self.blockUnusable = False
        self.invalidInputs = None

    def setInvalidInputs(self, invalidInputs) -> None:
        """Set invalid inputs of the block."""
        self.invalidInputs = invalidInputs

    def setErrors(self, reg: RandomErrorGen) -> None:
        """Set error for every cell in block.

        @ToDo: generalize memcell setErrors to receive reg
        """
        self.blockUnusable = False
        if type(self.ctrCellList[0]) == ProtoVoterCell:
            [c.setErrors(reg.gen(), reg.gen()) for c in self.ctrCellList]
        else:
            [c.setErrors(*reg.gen()) for c in self.ctrCellList]
        self.computeBlockError()

    def computeBlockError(self):
        """Compute global block error."""
        memCellErrors = [m.getCellError() for m in self.ctrCellList]
        # print(memCellErrors)

        if Errors.UD in memCellErrors:
            self.blockUnusable = True
            # print("UD in block")
            return
        elif memCellErrors.count(Errors.SA1) > 1:
            self.blockUnusable = True
            # print("Multiple SA1 in block")
            return

        if self.invalidInputs:
            for i in range(len(memCellErrors)):
                memCellErrors[i] = Errors.SA0 if self.invalidInputs[i] else memCellErrors[i]
        if memCellErrors.count(Errors.SA0) == len(self.ctrCellList):
            self.blockUnusable = True
            # print("No path available")

    def getBlockUnusable(self):
        """Return global usability of block."""
        return self.blockUnusable

    def debugBlock(self):
        """Debug utility - deprecated after tests implemented."""
        for c in self.ctrCellList:
            print("Test Cell")
            print(c.pullUpMemristor)
            print(c.pullDownMemristor)
            print(c.cellError)
        print("Get Block Error")
        print(self.getBlockUnusable())


class RoutingMux():
    """Representation of a routing multiplexer with variable stage number and size."""

    def __init__(self, n_stages, stage_inputs, cell_type) -> None:
        """Initialize error-free, all inputs valid mux with a given control cell architecture.

        The mux consists of n stages of a given cell controlling each input.
        """
        stage_inputs.append(1)  # add output node
        self.muxUnusable = False
        self.stages = []
        for n in range(n_stages):
            cell_list = [cell_type() for i in range(stage_inputs[n])]
            curr_stage = [RoutingMuxBlock(cell_list) for i in range(stage_inputs[n+1])]
            self.stages.append(curr_stage)

    def setErrors(self, reg):
        """Set error for all cells in a block of each stage."""
        self.muxUnusable = False
        for n in range(len(self.stages)):
            self.stages[n][0].setErrors(reg)
            if self.stages[n][0].getBlockUnusable():
                self.muxUnusable = True
                break

    def getMuxUnusable(self):
        """Return if mux is usable for routing or not."""
        return self.muxUnusable
