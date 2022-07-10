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
""""""
import numpy as np
from .memristor_errors import RandomErrorGen
from .control_cell import MemCell, ProtoVoterCell
from .mux import RoutingMux
from .plotter import plot_all_equal


def count_failure(failure_list, max):
    c = failure_list.count(True)
    return c / float(max)


def count_failure_old(failure_list, max):
    c = failure_list.count(True)
    return (max - c) / float(max)


def simulate_failure(failure_probabilities, cell_type, iterations):
    results = dict()

    for pSA0 in failure_probabilities:
        for pSA1 in failure_probabilities:
            for pUD in failure_probabilities:
                key = f"{pSA0},{pSA1},{pUD}"
                results[key] = list()
                for i in range(iterations):
                    reg = RandomErrorGen(pSA0, pSA1, pUD)
                    rm = RoutingMux(2, [4, 3], cell_type)
                    rm.set_errors(reg)
                    results[key].append(rm.getMuxUnusable())

    # Get % of unusable muxes
    results = dict((k, count_failure_old(v, iterations)) for k, v in results.items())
    return results


def simulate_failure_equal(failure_probabilities, cell_type, iterations):
    results = dict()

    for p in failure_probabilities:
        key = f"{p}"
        results[key] = list()
        for i in range(iterations):
            reg = RandomErrorGen(pSA0=0, pSA1=0, pUD=p)
            rm = RoutingMux(2, [4, 3], cell_type)
            rm.set_errors(reg)
            results[key].append(rm.getMuxUnusable())

    # Get % of unusable muxes
    results = dict((k, count_failure(v, iterations)) for k, v in results.items())
    return results


def main():
    failure_probabilities = np.arange(0, .155, .005)
    # print(failure_probabilities)
    # failure_probabilities = [0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.10, 0.25]

    res_base = simulate_failure_equal(failure_probabilities, MemCell, 10000)
    res_proto_voter = simulate_failure_equal(failure_probabilities, ProtoVoterCell, 10000)
    plot_all_equal(failure_probabilities, res_base, res_proto_voter)


if __name__ == "__main__":
    main()
