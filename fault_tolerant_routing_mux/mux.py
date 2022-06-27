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
from math import ceil
from .control_cell import ProtoVoterCell
from .memristor_errors import Errors, RandomErrorGen


class RoutingMuxBlock():
    """Representation of a mux block."""

    def __init__(self, src_node_list, sink_node, cell_list) -> None:
        """Initialize block as error-free and with all valid inputs."""
        self.src_node_list = src_node_list
        self.sink_node = sink_node
        self.ctrCellList = cell_list[:len(src_node_list)]
        self.blockUnusable = False

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
        elif memCellErrors.count(Errors.SA1) > 1:
            self.blockUnusable = True
            # print("Multiple SA1 in block")

    def getBlockUnusable(self):
        """Return global usability of block."""
        return self.blockUnusable

    def get_defect_edges(self):
        if self.blockUnusable:
            defect_edges = self.src_node_list
            return defect_edges

        memCellErrors = [m.getCellError() for m in self.ctrCellList]
        if Errors.SA1 in memCellErrors:
            active_source = memCellErrors.index(Errors.SA1)
            # all but SA1 are defect
            defect_edges = self.src_node_list.copy()
            defect_edges.pop(active_source)
            return defect_edges

        defect_edges = [self.src_node_list[i]
                        for i in range(len(self.src_node_list))
                        if self.ctrCellList[i].getCellError() == Errors.SA0]

        return defect_edges


class SecondStageMuxBlock(RoutingMuxBlock):
    def get_defect_edges(self):
        if self.blockUnusable:
            # Flatten inputs and return all
            defect_edges = [edge for block_edges in self.src_node_list for edge in block_edges]
            return defect_edges

        memCellErrors = [m.getCellError() for m in self.ctrCellList]
        if Errors.SA1 in memCellErrors:
            active_source = memCellErrors.index(Errors.SA1)
            # all but SA1 are defect
            defect_edges = self.src_node_list.copy()
            defect_edges.pop(active_source)
            defect_edges = [edge for block_edges in defect_edges for edge in block_edges]
            return defect_edges

        # Only SA0 present
        defect_edges = []
        for i in range(len(self.src_node_list)):
            if self.ctrCellList[i].getCellError() == Errors.SA0:
                defect_edges += self.src_node_list[i]

        return defect_edges


class RoutingMux():
    """Representation of a routing multiplexer with variable stage number and size."""

    def __init__(self, sink_node, src_node_list, cell_type) -> None:
        """Initialize error-free, all inputs valid mux with a given control cell architecture.

        The mux consists of n stages of a given cell controlling each input.

        :param sink_node: Sink node of the routing mux
        :param src_node_list: List of source nodes of the routing mux
        :param cell_type: Cell architecture to be used in simulation
        :param defect_sink_list: List of unusable sink nodes after defect simulation
        """
        self.sink_node = sink_node
        self.src_node_list = src_node_list
        self.optimal_block_size = self.compute_num_stages()
        self.first_stage_blocks = []
        self.build_mux(cell_type)

    def compute_num_stages(self):
        """Compute optimal block size for a 2-stage routing mux."""
        mux_size = len(self.src_node_list)
        block_size = mux_size
        n_mem_cells = mux_size
        partial_block = False

        for new_block_size in range(1, mux_size + 1):
            partial_block = (mux_size % new_block_size) != 0
            new_n_mem_cell = new_block_size + (mux_size // new_block_size) + partial_block

            if (new_n_mem_cell < n_mem_cells):
                n_mem_cells = new_n_mem_cell
                block_size = new_block_size

        return block_size

    def build_mux(self, cell_type):
        """Build a 2-stage routing mux."""
        n_blocks = ceil(len(self.src_node_list) / self.optimal_block_size)
        first_stage_cells = [cell_type() for i in range(self.optimal_block_size)]
        second_stage_cells = [cell_type() for i in range(n_blocks)]
        second_stage_inputs = []

        for n in range(n_blocks):
            start_input = n * self.optimal_block_size
            end_input = start_input + self.optimal_block_size
            block_inputs = self.src_node_list[start_input:end_input]
            rmb = RoutingMuxBlock(
                src_node_list=block_inputs,
                sink_node=None,
                cell_list=first_stage_cells
            )
            self.first_stage_blocks.append(rmb)
            second_stage_inputs.append(block_inputs)

        self.second_stage_block = SecondStageMuxBlock(
                                    src_node_list=second_stage_inputs,
                                    sink_node=self.sink_node,
                                    cell_list=second_stage_cells)
        self.cell_list = first_stage_cells + second_stage_cells

    def setErrors(self, reg):
        """Set error for all cells in a block of each stage."""
        self.first_stage_blocks[0].setErrors(reg)
        self.second_stage_block.setErrors(reg)

    def computeBlockErrors(self):
        for block in self.first_stage_blocks:
            block.computeBlockError()
        self.second_stage_block.computeBlockError()

    def get_defect_edges(self):
        """Return a dict of defect source nodes indexed by the sink node."""
        defect_edges = []
        for block in self.first_stage_blocks:
            defect_edges += block.get_defect_edges()
        defect_edges += self.second_stage_block.get_defect_edges()
        if not defect_edges:
            return {}

        return {self.sink_node: set(defect_edges)}

    def getMuxUnusable(self):
        """Return if mux is usable for routing or not."""
        return self.muxUnusable
