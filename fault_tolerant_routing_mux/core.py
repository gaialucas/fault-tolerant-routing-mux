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
"""Provides core simulation class to load and overwrite routing resource files."""
from collections import Counter
from datetime import datetime
from typing import Dict
from fault_tolerant_routing_mux.control_cell import MemCell, ProtoVoterCell  # noqa: F401
from mux import RoutingMux
from rr_graph_parser import RRGraphParser
from memristor_errors import RandomErrorGen


class FaultSimulator():
    """Load rr_graph file, run fault simulation and write results."""

    def __init__(self, rr_graph_file: str, cell_type, p: float=None, pSA0: float=0., pSA1: float=0., pUD: float=0.):  # noqa: E501, E252
        """Wrap RRGraphParser and RandomErrorGen."""
        self.rrg = RRGraphParser(rr_graph_file)
        self.initial_edge_count = self.get_edge_count(self.rrg.get_mux_dict(), cell_type)
        self.muxes = self.gen_routing_muxes(self.rrg.get_mux_dict())
        self.defect_edges = dict()
        if p is not None:  # Assume all equal probabilites
            self.reg = RandomErrorGen(pSA0=p, pSA1=p, pUD=p)
            self.faulty_rr_graph_file = f"{rr_graph_file}_{p*100:02.1f}"
        else:
            self.reg = RandomErrorGen(pSA0=pSA0, pSA1=pSA1, pUD=pUD)
            self.faulty_rr_graph_file = f"{rr_graph_file}_{pSA0*100:02.1f}_{pSA1*100:02.1f}_{pSA1*100:02.1f}"  # noqa E501

    def run_simulation(self):
        # Setup
        cell_errors = list()
        defect_edges = dict()
        start = datetime.now()

        # Simulation itself
        for mux in self.muxes:
            mux.set_errors(self.reg)
            mux.compute_block_errors()
            cell_errors += mux.get_cell_errors()
            defect_edges.update(mux.get_defect_edges())

        # Teardown
        self.sim_time = (datetime.now() - start).total_seconds()
        self.defect_edges = defect_edges
        self.cell_errors_counter = Counter(cell_errors)
        self.defect_edge_count = self.get_edge_count(self.defect_edges)

    def write_defect_rr_graph_file(self):
        self.rrg.update_rr_graph(self.faulty_rr_graph_file, self.defect_edges)

    def get_edge_count(self, mux_dict: Dict):
        """Return number of edges from a dictionary of {sink: [source nodes]}."""
        return sum([len(edges) for edges in mux_dict.values()])

    def gen_routing_muxes(self, mux_dict: Dict, cell_type):
        """Create list of RoutingMuxes from RRGraphParser output."""
        return [RoutingMux(sink, sources, cell_type) for sink, sources in mux_dict.items()]
