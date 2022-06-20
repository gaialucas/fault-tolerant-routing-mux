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
"""Test suite for the routing resource graph parser."""
import pytest
import rr_graph_parser


EMPTY_FILE = """"""

MIN_FILE = """<switches>
<switch id="0" name="0" type="mux"><timing Tdel="1.10200002e-10"/>
<sizing buf_size="11.9105997" mux_trans_size="1.21493995"/>
</switch>
</switches>
<rr_edges>
<edge sink_node="24678" src_node="10" switch_id="0"></edge>
<edge sink_node="24680" src_node="10" switch_id="0"></edge>
<edge sink_node="24681" src_node="10" switch_id="0"></edge>
<edge sink_node="24682" src_node="10" switch_id="0"></edge>
<edge sink_node="24684" src_node="10" switch_id="0"></edge>
</rr_edges>
"""

SAMPLE_FILE = """<switches>
<switch id="0" name="__vpr_delayless_switch__" type="mux"><timing/>
<sizing buf_size="0" mux_trans_size="0"/>
</switch>
<switch id="1" name="ipin_cblock" type="mux"><timing R="700.077515" Tdel="8.60699984e-11"/>
<sizing buf_size="7.11716986" mux_trans_size="1.22125995"/>
</switch>
<switch id="2" name="0" type="mux"><timing Tdel="1.10200002e-10"/>
<sizing buf_size="11.9105997" mux_trans_size="1.21493995"/>
</switch>
</switches>
<rr_edges>
<edge sink_node="10" src_node="1" switch_id="0"></edge>
<edge sink_node="13" src_node="4" switch_id="0"></edge>
<edge sink_node="16" src_node="7" switch_id="0"></edge>
<edge sink_node="0" src_node="9" switch_id="0"></edge>
<edge sink_node="24670" src_node="10" switch_id="2"></edge>
<edge sink_node="24672" src_node="10" switch_id="2"></edge>
<edge sink_node="24673" src_node="10" switch_id="2"></edge>
<edge sink_node="24674" src_node="10" switch_id="2"></edge>
<edge sink_node="24676" src_node="10" switch_id="2"></edge>
<edge sink_node="24678" src_node="10" switch_id="2"></edge>
<edge sink_node="24680" src_node="10" switch_id="2"></edge>
<edge sink_node="24681" src_node="10" switch_id="2"></edge>
<edge sink_node="24682" src_node="10" switch_id="2"></edge>
<edge sink_node="24684" src_node="10" switch_id="2"></edge>
<edge sink_node="2" src_node="11" switch_id="0"></edge>
<edge sink_node="3" src_node="12" switch_id="0"></edge>
<edge sink_node="24673" src_node="13" switch_id="2"></edge>
<edge sink_node="24681" src_node="13" switch_id="2"></edge>
<edge sink_node="24689" src_node="13" switch_id="2"></edge>
<edge sink_node="24696" src_node="13" switch_id="2"></edge>
<edge sink_node="24697" src_node="13" switch_id="2"></edge>
<edge sink_node="24698" src_node="13" switch_id="2"></edge>
<edge sink_node="24700" src_node="13" switch_id="2"></edge>
<edge sink_node="24702" src_node="13" switch_id="2"></edge>
<edge sink_node="24704" src_node="13" switch_id="2"></edge>
</rr_edges>
"""

def test_no_file():
    with pytest.raises(TypeError):
        # rr_graph_parser.parse()
        raise TypeError

def empty_file():
    mux_list = rr_graph_parser.parse(EMPTY_FILE)
    assert mux_list is None

def test_minimal_file():
    expected_mux_list = {"10": [24678, 24680, 24681, 24682, 24684]}
    mux_list = rr_graph_parser.parse(MIN_FILE)
    assert mux_list == expected_mux_list

def test_minimal_file():
    expected_mux_list = {
        "10": [24670, 24672, 24673, 24674, 24676, 24678, 24680, 24681, 24682, 24684],
        "13": [24673, 24681, 24689, 24696, 24697, 24698, 24700, 24702, 24704]
    }
    mux_list = rr_graph_parser.parse(MIN_FILE)
    assert mux_list == expected_mux_list