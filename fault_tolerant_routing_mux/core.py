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
import numpy as np

from .mux import RoutingMux
from .rr_graph_parser import RRGraphParser
from .memristor_errors import Errors, RandomErrorGen


class FaultSimulator():
    """Wrapper to simulate production defects in NV-based routing multiplexers.

    This class can be used as a standalone simulator for a single routing element
    or be integrated with Verilog to Routing toolchain to analyze the effects of
    faults in a FPGA-implemented design.
    A standalone simulation is a class method and returns the results directly.
    >>> res = FaultSimulator.standalone_sim(probabilities_array, num_iterations, cell_type)

    Utilities to plot the given results are provided in plot_fault_results.
    >>> ftrm.plot_fault_results(res)

    To use it with VTR, instantiate the class with a memory cell class, rr_graph file and fault probabilities.
    >>> fault_sim = FaultSimulator(ProtoVoterCell, rr_graph_file=file_pathname, p=0.003)
    >>> fault_sim.run_simulation()
    """

    def __init__(self, cell_type, rr_graph_file: str, p: float=None, pSA0: float=0., pSA1: float=0., pUD: float=0.):  # noqa: E501, E252
        """Wrap RRGraphParser and RandomErrorGen."""
        self.rrg = RRGraphParser(rr_graph_file)
        self.initial_edge_count = self.get_edge_count(self.rrg.get_mux_dict())
        self.muxes = self.gen_routing_muxes(self.rrg.get_mux_dict(), cell_type)
        self.defect_edges = dict()
        # [:-4] gets name up to extension (.xml)
        self.rr_graph_file = rr_graph_file[:-4]
        self.cell_type = cell_type
        if p is not None:  # Assume all equal probabilites
            self.reg = RandomErrorGen(pSA0=p, pSA1=p, pUD=p)
            self.faulty_rr_graph_file = f"{self.rr_graph_file}_{p*100:02.1f}.xml"
        else:
            self.reg = RandomErrorGen(pSA0=pSA0, pSA1=pSA1, pUD=pUD)
            self.faulty_rr_graph_file = f"{self.rr_graph_file}_{pSA0*100:05.2f}_{pSA1*100:05.2f}_{pSA1*100:05.2f}.xml"  # noqa E501

    def run_simulation(self):
        # Setup
        cell_errors = list()
        defect_edges = dict()
        unusable_muxes = list()
        sim_start = datetime.now()

        # Simulation itself
        for mux in self.muxes:
            mux.set_errors(self.reg)
            mux.compute_block_errors()
            cell_errors += mux.get_cell_errors()
            defect_edges.update(mux.get_defect_edges())
            unusable_muxes.append(mux.get_mux_unusable())

        # Teardown
        print("Simulation ended. Parsing results.", end="")
        sim_end = datetime.now()
        self.sim_time = (sim_end - sim_start).total_seconds()
        self.unusable_count = sum(unusable_muxes)
        self.defect_edges = defect_edges
        self.cell_errors_counter = Counter(cell_errors)
        self.defect_edge_count = self.get_edge_count(self.defect_edges)
        print(".", end="")

        self._write_defect_rr_graph_file()
        print(".")
        self.report_time = (datetime.now() - sim_end).total_seconds()
        self._write_report()

    def standalone_sim(p_array: np.array, num_iters: int, cell_type):
        results = dict()

        start = datetime.now()
        for p in p_array:
            defect_edges = list()
            cell_errors = list()
            reg = RandomErrorGen(pSA0=p, pSA1=p, pUD=p)
            # Simulation
            sim_muxes = [RoutingMux(
                            sink_node=i,
                            src_node_list=[src_node for src_node in range(i * 12, i * 12 + 12)],
                            cell_type=cell_type)
                         for i in range(num_iters)]
            for mux in sim_muxes:
                mux.set_errors(reg)
                mux.compute_block_errors()
                defect_edges += mux.get_defect_edges().values()
                cell_errors += mux.get_cell_errors()

            # Results
            res_unusable = sum([m.get_mux_unusable() for m in sim_muxes]) / num_iters
            res_cell_errors = Counter(cell_errors)
            res_defect_edges = sum([len(edges) for edges in defect_edges])
            res_defect_edges = res_defect_edges / (12 * num_iters)
            results[p] = (res_unusable,
                          res_defect_edges,
                          res_cell_errors[Errors.SA0],
                          res_cell_errors[Errors.SA1],
                          res_cell_errors[Errors.UD]
                          )

        sim_time = (datetime.now() - start).total_seconds()
        FaultSimulator._write_standalone_report(cell_type, num_iters, sim_time, results)
        return results

    def _write_standalone_report(cell_type, num_iters, sim_time, results):
        with open('fault_sim.rpt', 'w') as f:
            # Header
            f.write("Standalone simulation report\n")
            f.write(f"Number of iterations:\t{num_iters}\n")
            f.write(f"Cell type:\t\t\t\t{cell_type.__name__}\n")
            f.write(f"Simulation time:\t\t{sim_time:.2f} seconds\n")
            f.write("=" * 80)
            f.write("\n\n")

            # Table header
            f.write("Fault probability\t")
            f.write("% unusable\t")
            f.write("% defect edges\t")
            f.write("# SA0\t")
            f.write("# SA1\t")
            f.write("# UD\t")
            f.write("% SA0\t")
            f.write("% SA1\t")
            f.write("% UD\n")

            # Table
            for k, v in results.items():
                key = f"{100 * k:05.2f}"
                unusable = f"\t\t\t\t{v[0] * 100:6.2f}"
                defect = f"\t{v[1] * 100:6.2f}"
                errors = f"\t{v[2]:4d}\t{v[3]:4d}\t{v[4]:4d}"
                percentsa0 = f"{v[2] / (num_iters*7) * 100:5.2f}"
                percentsa1 = f"{v[3] / (num_iters*7) * 100:5.2f}"
                percentud = f"{v[4] / (num_iters*7) * 100:5.2f}"
                percents = f"{percentsa0}\t{percentsa1}\t{percentud}"
                table_entry = f"{key}\t{unusable}\t{defect}\t{errors}\t{percents}\n"
                f.write(table_entry)

        print("Report written to fault_sim.rpt")

    def _write_report(self):
        report_file = f'{self.faulty_rr_graph_file[:-4]}.rpt'
        with open(report_file, 'w') as f:
            # Header
            f.write("Fault simulation report\n")
            f.write(f"RR Graph File:\t{self.rr_graph_file}\n")
            f.write(f"Cell type:\t\t{self.cell_type.__name__}\n")
            f.write(f"Simulation time:\t{self.sim_time:.2f} seconds\n")
            f.write(f"Report time:\t\t{self.report_time:.2f} seconds\n")
            f.write("=" * 80)
            f.write("\n\n")

            # Table
            unusable = self.unusable_count / len(self.muxes) * 100
            defect = self.defect_edge_count / self.initial_edge_count * 100
            print(f"FF: {self.cell_errors_counter[Errors.FF]}")
            err_sa0 = self.cell_errors_counter[Errors.SA0] / sum(self.cell_errors_counter.values()) * 100
            err_sa1 = self.cell_errors_counter[Errors.SA1] / sum(self.cell_errors_counter.values()) * 100
            err_ud  = self.cell_errors_counter[Errors.UD]  / sum(self.cell_errors_counter.values()) * 100# noqa E221

            f.write(f"# SA0:\t\t\t\t{self.cell_errors_counter[Errors.SA0]:6d}\n")
            f.write(f"# SA1:\t\t\t\t{self.cell_errors_counter[Errors.SA1]:6d}\n")
            f.write(f"# UD:\t\t\t\t{self.cell_errors_counter[Errors.UD]:6d}\n")
            f.write(f"Total edges:\t\t\t{self.initial_edge_count:6d}\n")
            f.write(f"Defect edges:\t\t\t{self.defect_edge_count:6d}\n")
            f.write(f"% SA0:\t\t\t\t{err_sa0:6.2f}\n")
            f.write(f"% SA1:\t\t\t\t{err_sa1:6.2f}\n")
            f.write(f"% UD:\t\t\t\t{err_ud:6.2f}\n")
            f.write(f"% Defect edges:\t\t{defect:6.2f}\n")
            f.write(f"% Unusable muxes:\t\t{unusable:6.2f}\n")

        print(f"Report written to {report_file}")

    def _write_defect_rr_graph_file(self):
        self.rrg.update_rr_graph(self.faulty_rr_graph_file, self.defect_edges)

    def get_edge_count(self, mux_dict: Dict):
        """Return number of edges from a dictionary of {sink: [source nodes]}."""
        return sum([len(edges) for edges in mux_dict.values()])

    def gen_routing_muxes(self, mux_dict: Dict, cell_type):
        """Create list of RoutingMuxes from RRGraphParser output."""
        return [RoutingMux(sink, sources, cell_type) for sink, sources in mux_dict.items()]
