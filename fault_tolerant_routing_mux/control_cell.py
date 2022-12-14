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
"""Control Cell representations for NV configuration memory.

Control Cell are defined as the logic that result in a signal enabling or
disabling an input of the mux stage. It could be as simple as a single
memory cell such as the base architecture proposed by Xilinx or more robust
logic as explored in this work.
"""

from .memristor_errors import Errors


class MemCell():
    """Standard representation of a single 2T2R memory cell."""

    error_LUT = ((Errors.FF,  Errors.SA0, Errors.SA1, Errors.UD),
                 (Errors.SA1, Errors.UD,  Errors.SA1, Errors.UD),
                 (Errors.SA0, Errors.SA0, Errors.UD,  Errors.UD),
                 (Errors.UD,  Errors.UD,  Errors.UD,  Errors.UD))

    def __init__(self) -> None:
        """Initialize cell as error-free."""
        self.pullUpMemristor = Errors.FF
        self.pullDownMemristor = Errors.FF

    def set_errors(self, pullUpError, pullDownError) -> None:
        """Set error for memristors in cell and compute global cell error."""
        self.pullUpMemristor = pullUpError
        self.pullDownMemristor = pullDownError

    def get_cell_error(self):
        """Return the cell error."""
        return MemCell.error_LUT[self.pullDownMemristor][self.pullUpMemristor]


class ProtoVoterCell():
    """Representation of a simple selector control cell.

    The cell consists of a single memory cell selecting between another
    memory cell or ground, in case of failure of the former.
    """
    error_LUT = ((Errors.FF,  Errors.SA0, Errors.FF,  Errors.SA0),
                 (Errors.SA0, Errors.SA0, Errors.SA0, Errors.SA0),
                 (Errors.FF,  Errors.SA0, Errors.SA1, Errors.UD),
                 (Errors.SA0, Errors.SA0, Errors.UD,  Errors.UD))

    def __init__(self) -> None:
        """Initialize control cell as error-free."""
        self.mainCell = MemCell()
        self.ctrCell = MemCell()

    def set_errors(self, mainCellErrors, crtCellErrors):
        """Set error for each memory cell and compute global error."""
        self.mainCell.set_errors(*mainCellErrors)
        self.ctrCell.set_errors(*crtCellErrors)

    def get_cell_error(self):
        """Return cell error."""
        mainCellError = self.mainCell.get_cell_error()
        ctrCellError = self.ctrCell.get_cell_error()
        return ProtoVoterCell.error_LUT[mainCellError][ctrCellError]
