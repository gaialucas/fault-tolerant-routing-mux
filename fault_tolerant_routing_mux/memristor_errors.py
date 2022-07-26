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
"""Error simulator for memristor components used in NV configuration memory."""
import random
random.seed(42)


# Possible errors regarding a Memristor
class Errors():
    """Error codes for possible defects in a memristor.

    FF: Free of Failure
    SA0: Stuck At 0
    SA0: Stuck At 1
    UD: UnDefined behaviour
    """

    FF, SA0, SA1, UD = range(4)


class RandomErrorGen():
    """Error generator for memristor components.

    Receives absolute probabilities for each error and stores them as
    cumulative. The gen() function takes no argument and returns a single
    error following the instance probabilities.

    reg = RandomErrorGen(pSA0=0, pSA1=0, pUD=0)
    """

    def __init__(self, pSA0: float = 0., pSA1: float = 0., pUD: float = 0.):
        """Init the error distribution."""
        self.pUD = pUD
        self.pSA0 = pUD + pSA0
        self.pSA1 = pUD + pSA0 + pSA1

    def gen(self):
        """Return a single Error following the instance distribution."""
        return random.choices(
            [Errors.UD, Errors.SA0, Errors.SA1, Errors.FF],
            cum_weights=[self.pUD, self.pSA0, self.pSA1, 1],
            k=2
        )

    def get_probabilities(self):
        # Convert cumulative back to absolute before returning
        return self.pSA0 - self.pUD, self.pSA1 - self.pSA0, self.pUD
