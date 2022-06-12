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

    def __init__(self) -> None:
        """Initialize cell as error-free."""
        self.pullUpMemristor = Errors.FF
        self.pullDownMemristor = Errors.FF
        self.cellError = Errors.FF

    def computeCellError(self) -> None:
        """Compute global cel error from each memristor error."""
        if (self.pullUpMemristor == Errors.UD) or (self.pullDownMemristor == Errors.UD):
            self.cellError = Errors.UD
        elif (self.pullDownMemristor == Errors.SA0):
            if (self.pullUpMemristor == Errors.SA0):
                self.cellError = Errors.UD
            else:
                self.cellError = Errors.SA1
        elif (self.pullDownMemristor == Errors.SA1):
            if (self.pullUpMemristor == Errors.SA1):
                self.cellError = Errors.UD
            else:
                self.cellError = Errors.SA0
        else:  # Pull-Down is FF, cell error is the same as Pull-Up
            self.cellError = self.pullUpMemristor

    def setErrors(self, pullUpError, pullDownError) -> None:
        """Set error for memristors in cell and compute global cell error."""
        self.pullUpMemristor = pullUpError
        self.pullDownMemristor = pullDownError
        self.computeCellError()

    def getCellError(self):
        """Return the cell error."""
        return self.cellError


class ProtoVoterCell():
    """Representation of a simple selector control cell.

    The cell consists of a single memory cell selecting between another
    memory cell or ground, in case of failure of the former.
    """

    def __init__(self) -> None:
        """Initialize control cell as error-free."""
        self.mainCell = MemCell()
        self.ctrCell = MemCell()
        self.cellError = Errors.FF

    def setErrors(self, mainCellErrors, crtCellErrors):
        """Set error for each memory cell and compute global error."""
        self.mainCell.setErrors(*mainCellErrors)
        self.ctrCell.setErrors(*crtCellErrors)
        self.computeCellError()

    def computeCellError(self):
        """Compute global control cell error."""
        mainCellError = self.mainCell.getCellError()
        ctrCellError = self.ctrCell.getCellError()
        if (ctrCellError == Errors.UD):
            if (mainCellError == Errors.SA1 or mainCellError == Errors.UD):
                self.cellError = Errors.UD
            else:
                self.cellError = Errors.SA0
        elif (ctrCellError == Errors.SA1):
            self.cellError = mainCellError
        elif (ctrCellError == Errors.SA0):
            self.cellError = Errors.SA0
        # crlCellError == FF
        elif (mainCellError == Errors.SA0) or (mainCellError == Errors.UD):
            self.cellError = Errors.SA0

    def getCellError(self):
        """Return cell error."""
        return self.cellError
