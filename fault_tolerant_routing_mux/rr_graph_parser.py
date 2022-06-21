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
"""Module to parse rr_graph files into data structures."""
import re
from collections import defaultdict


class RRGraphParser():

    def __init__(self, rr_graph_file):
        self.file = rr_graph_file
        self.mux_dict = defaultdict(list)

    def add_sink_source_node(self, line):
        extracted_nodes = re.search(' (.+) ', line).group(1)
        for node in extracted_nodes.split():
            # print(node)
            if "sink" in node:
                sink_node = int(node.split('=')[1].strip('"'))
            if "src" in node:
                source_node = int(node.split('=')[1].strip('"'))

        self.mux_dict[source_node].append(sink_node)

    def parse_switches(self, rr_graph_file):
        for line in rr_graph_file:
            if line.startswith("<switch "):
                if "name=\"0\"" in line:
                    self.target_id = re.search('id="(.+?)"', line).group(1)
            elif line == "</switches>\n":
                return

    def parse_rr_edges(self, rr_graph_file):
        for line in rr_graph_file:
            if line.startswith("<edge "):
                if f"switch_id=\"{self.target_id}\"" in line:
                    self.add_sink_source_node(line)
            elif line == "</rr_edges>\n":
                return

    def parse(self):
        with open(self.file) as f:
            for line in f:
                if line == "<switches>\n":
                    # print(line)
                    self.parse_switches(f)
                elif line == "<rr_edges>\n":
                    # print(line)
                    self.parse_rr_edges(f)
                    break

        return self.mux_dict
