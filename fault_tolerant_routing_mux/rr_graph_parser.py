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
import xml.etree.ElementTree as ET
from collections import defaultdict


class RRGraphParser():
    """Class to parse Routing Resource Graph files.

    This class implements a VERY naive approach. It does not validate the full
    structure of the RR Graph file. It searches for the tags we need and parse
    every subtag within. It is more memory efficient than loading the whole
    XML file into memory as we process line by line.

    :param file: The rr_graph file to be parsed
    :param mux_dict: Dictionary of routing multiplexer output (source) and input (sink) node.
    """

    def __init__(self, rr_graph_file):
        """Load a given rr_graph file and parse switches and edges.

        :param tree: RR Graph XML tree
        :self.switchbox_id: id of structure corresponding to the routing muxes in the XML
        :self.cblock_id: id of structure corresponding to the connection block in the XML
        :param mux_dict: Dictionary of routing multiplexers indexed by mux sink_node
        """
        self.tree = ET.parse(rr_graph_file)
        self.mux_dict = defaultdict(list)
        self.parse_switches()
        self.parse_rr_edges()

    def parse_switches(self):
        """Store the respective id of connection blocks and routing muxes based on switch name."""
        for s in self.tree.find('switches'):
            if (s.attrib['name'] == '0'):
                self.switchbox_id = s.attrib['id']
            elif (s.attrib['name'] == 'ipin_cblock'):
                self.cblock_id = s.attrib['id']

    def parse_rr_edges(self):
        """Iterate over edge tags and parse routing muxes.

        An edge is only parsed if mux id matches self.target_id.
        """
        for edge in self.tree.find('rr_edges'):
            if edge.attrib['switch_id'] == self.switchbox_id:
                sink_node = edge.attrib['sink_node']
                src_node = edge.attrib['src_node']
                self.mux_dict[int(sink_node)].append(int(src_node))

    def get_mux_dict(self):
        """Return dictionary of mux nodes."""
        return self.mux_dict

    def update_rr_graph(self, defect_filename, defect_edges_dict):
        # Since src-sink are unique we can use a set for efficiency
        defect_edges = {(str(source), str(sink))
                        for sink, sources in defect_edges_dict.items()
                        for source in sources}

        rr_edges = self.tree.find('rr_edges')
        all_rr_edges = set(rr_edges.findall('edge'))
        print('finding edges')
        mux_defect_edges = set(edge for edge in all_rr_edges if (edge.attrib['src_node'], edge.attrib['sink_node']) in defect_edges)
        print('found')
        print('creating new')
        good_edges = all_rr_edges - mux_defect_edges
        # print(f"Good edges len: {len(good_edges)}")
        new_rr_edges = ET.Element('rr_edges')
        new_rr_edges.extend(good_edges)
        print('deleting')
        self.tree.getroot().remove(rr_edges)
        print('readding')
        self.tree.getroot().append(new_rr_edges)

        # print(f"Writing new file")
        self.tree.write(defect_filename)
        # print(f"Saved {defect_filename}")
