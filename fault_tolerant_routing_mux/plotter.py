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
"""Plot utilities for visualization."""

import numpy as np
import matplotlib.pyplot as plt


def plot_3d_scatter(x_axis, y_axis, z_axis, z_axis_robust, pUD):
    """Plot a 3D scatter plot."""
    fig = plt.figure(figsize=(12, 12))
    # fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(x_axis, y_axis, z_axis, label="Base arch")
    ax.scatter(x_axis, y_axis, z_axis_robust, label="Proto Voter (ground)")

    ax.set_xlabel('SA0 probability')
    ax.set_ylabel('SA1 probability')
    ax.set_zlabel('Ratio of usable units')
    # ax.xlim()
    # ax.ylim()
    ax.set_zlim3d(0, 1.0)

    plt.title(f"Robustness analysis at p(UD) = {100 * pUD:.2f}%")
    plt.legend()
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'{pUD:.2f}-UD.png')


def plot_scatter(x_axis, y_axis, y_axis_robust):
    """Plot a scatter plot."""
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot()

    ax.scatter(x_axis, y_axis, c='b', label="Base arch")
    ax.scatter(x_axis, y_axis_robust, c='r', marker='s', label="Proto Voter (ground)")

    ax.set_xlabel('Failure probability')
    ax.set_ylabel('% unusable units')
    ax.set_xticks(np.arange(0, .155, .015))
    ax.set_yticks(np.arange(0, 1.01, 0.1))
    plt.grid()

    plt.title("% Unusable units by UD failure probability")
    plt.legend()
    plt.tight_layout()
    # plt.show()
    plt.savefig('failure-percent.png')


def plot_all(probs, res_base, res_proto_voter):
    for p in probs:
        # print(str(p))
        k_filter = [k for k in list(res_base.keys()) if k.split(",")[-1] == str(p)]
        # print(k_filter)

        x_axis = [float(k.split(",")[0]) for k in k_filter]
        y_axis = [float(k.split(",")[1]) for k in k_filter]
        z_axis = [res_base[k] for k in k_filter]
        z_axis_robust = [res_proto_voter[k] for k in k_filter]

        plot_3d_scatter(x_axis, y_axis, z_axis, z_axis_robust, p)


def plot_all_equal(probs, res_base, res_proto_voter):
    # for p in probs:
    #     print(str(p))
    #     k_filter = [k for k in list(res_base.keys()) if k == str(p)]
    #     print(k_filter)

    x_axis = [float(k) for k in res_base.keys()]
    y_axis = [v for v in res_base.values()]
    y_axis_robust = [v for v in res_proto_voter.values()]

    plot_scatter(x_axis, y_axis, y_axis_robust)
