#!/usr/bin/env python3
"""Render a compact dbt lineage graph from target/graph_summary.json.

This produces a presentation-ready PNG that highlights the core pipeline:
raw source -> staging -> cleaning -> marts.
"""

import argparse
import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx


def load_summary(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def short_name(name):
    suffix = name.split(".")[-1]
    mapping = {
        "bird_features": "raw",
        "stg_bird_features": "staging",
        "clean_bird_features": "cleaned",
        "bird_distribution": "distribution",
        "bird_stats": "stats",
        "high_pitch_birds": "high pitch",
        "long_duration_birds": "long duration",
        "top_birds": "top birds",
    }
    return mapping.get(suffix, suffix.replace("_", " "))


def build_graph(summary, include_tests=False, include_seeds=False):
    linked = summary.get("linked", {})
    graph = nx.DiGraph()

    allowed_types = {"source", "model"}
    if include_tests:
        allowed_types.add("test")
    if include_seeds:
        allowed_types.add("seed")

    for node in linked.values():
        node_type = node.get("type", "")
        if node_type not in allowed_types:
            continue
        graph.add_node(node["name"], node_type=node_type)

    for index, node in linked.items():
        node_type = node.get("type", "")
        if node_type not in allowed_types:
            continue
        for succ_index in node.get("succ", []):
            succ = linked[str(succ_index)]
            succ_type = succ.get("type", "")
            if succ_type not in allowed_types:
                continue
            graph.add_edge(node["name"], succ["name"])

    return graph


def layer_positions(graph):
    if not graph.nodes:
        return {}

    depth = {node: 0 for node in graph.nodes}
    for node in nx.topological_sort(graph):
        parents = list(graph.predecessors(node))
        if parents:
            depth[node] = max(depth[parent] + 1 for parent in parents)

    grouped = defaultdict(list)
    for node, level in depth.items():
        grouped[level].append(node)

    positions = {}
    for level in sorted(grouped):
        nodes = sorted(grouped[level])
        for offset, node in enumerate(nodes):
            positions[node] = (level * 2.6, -offset * 1.8)

    return positions


def node_colors(graph):
    palette = {
        "source": "#1f77b4",
        "model": "#2ca02c",
        "test": "#ff7f0e",
        "seed": "#9467bd",
    }
    return [palette.get(graph.nodes[node].get("node_type", "model"), "#7f7f7f") for node in graph.nodes]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="target/graph_summary.json", help="Path to dbt graph_summary.json")
    parser.add_argument("--output", default="docs/assets/dbt_lineage.png", help="Output PNG path")
    parser.add_argument("--include-tests", action="store_true", help="Include test nodes in the graph")
    parser.add_argument("--include-seeds", action="store_true", help="Include seed nodes in the graph")
    args = parser.parse_args()

    summary = load_summary(args.input)
    graph = build_graph(summary, include_tests=args.include_tests, include_seeds=args.include_seeds)
    positions = layer_positions(graph)

    if not graph.nodes:
        raise SystemExit("No nodes found in dbt graph summary.")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    plt.figure(figsize=(18, 9))
    nx.draw_networkx_edges(
        graph,
        positions,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=16,
        width=1.5,
        edge_color="#8f9bb3",
        alpha=0.75,
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=3400,
        node_color=node_colors(graph),
        linewidths=1.5,
        edgecolors="#1a1a1a",
    )
    labels = {node: short_name(node) for node in graph.nodes}
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=8, font_weight="bold", font_color="white")

    plt.title("BirdNET dbt Lineage Graph", fontsize=16, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close()

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()