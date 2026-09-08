"""Graph traversal, shortest paths and structural properties.

Graphs are 1-indexed with `n` nodes and an explicit edge list.
"""

from __future__ import annotations

import heapq
import random
from collections import deque

from app.content.codequest.framework import (
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    PAIR_LIST,
    Param,
    TRIPLE_LIST,
    connected_edges,
    dag_edges,
    p_int,
)

T = ["Graphs"]
BFS = ["Graph BFS / DFS"]
CC = ["BFS / Connected Components"]
TOPO = ["Topological Sort"]

GRAPH_NOTE = "Nodes are numbered 1 to n. The graph may be disconnected unless stated otherwise."


def p_edges(name="edges", desc="each pair is an edge u v"):
    return Param(name, PAIR_LIST, desc)


def p_weighted(name="edges", desc="each entry is u v w"):
    return Param(name, TRIPLE_LIST, desc)


def g_undirected(sizes=(1, 2, 3, 5, 9, 18, 45, 100)):
    def gen(rng: random.Random):
        cases = []
        for n in sizes:
            if n == 1:
                cases.append((1, []))
                continue
            # Mix connected graphs with sparse, possibly disconnected ones.
            if rng.random() < 0.5:
                cases.append((n, connected_edges(rng, n, extra=rng.randint(0, n // 2))))
            else:
                edges = set()
                for _ in range(rng.randint(0, n)):
                    u, v = rng.randint(1, n), rng.randint(1, n)
                    if u != v:
                        edges.add((min(u, v), max(u, v)))
                cases.append((n, sorted(edges)))
        return cases

    return gen


def g_weighted(sizes=(1, 2, 3, 5, 9, 18, 40, 90)):
    def gen(rng: random.Random):
        cases = []
        for n in sizes:
            if n == 1:
                cases.append((1, []))
                continue
            base = connected_edges(rng, n, extra=rng.randint(0, n // 2))
            cases.append((n, [(u, v, rng.randint(1, 30)) for u, v in base]))
        return cases

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "count-connected-components", "Count Connected Components", "medium", T, CC,
        "Given an undirected graph with `n` nodes and the given edges, print the number of connected "
        "components.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _count_components(n, edges),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "1 <= u, v <= n", "u != v"],
        ["Build an adjacency list from the edge list.",
         "Start a BFS or DFS from every node you have not visited yet.",
         "Each traversal you launch marks exactly one component.",
         "Isolated nodes are components of size 1."],
        notes=[GRAPH_NOTE],
        explanations=["{1,2,3} and {4,5}.", "Three isolated nodes."],
    ))

    add(P(
        "largest-component-size", "Largest Component Size", "medium", T, CC,
        "Print the number of nodes in the largest connected component of the undirected graph.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _largest_component(n, edges),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Traverse each component and count the nodes you reach.",
         "Track the maximum count across all traversals.",
         "With no edges, every component has size 1."],
        notes=[GRAPH_NOTE],
        explanations=["{1,2,3} has 3 nodes.", "Every component is a single node."],
    ))

    add(P(
        "bfs-order-from-node", "BFS Traversal Order", "medium", T, BFS,
        "Print the BFS order starting from node `1`, visiting each node's neighbours in increasing order. "
        "Only nodes reachable from `1` appear.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT_LIST,
        lambda n, edges: _bfs_order(n, edges),
        [(5, [(1, 2), (1, 3), (2, 4)]), (2, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Sort each adjacency list so the order is deterministic.",
         "Use a queue and mark nodes visited when you enqueue them, not when you dequeue.",
         "Marking on dequeue lets a node enter the queue twice."],
        notes=[GRAPH_NOTE],
        explanations=["1,2,3,4 — node 5 is unreachable.", "Only node 1 is reachable."],
    ))

    add(P(
        "dfs-order-from-node", "DFS Traversal Order", "medium", T, BFS,
        "Print the DFS order starting from node `1`, always descending into the smallest unvisited "
        "neighbour first. Only nodes reachable from `1` appear.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT_LIST,
        lambda n, edges: _dfs_order(n, edges),
        [(5, [(1, 2), (1, 3), (2, 4)]), (2, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Sort the adjacency lists to make the traversal deterministic.",
         "Recursion is natural, but a stack avoids deep-recursion limits.",
         "With a stack, push neighbours in descending order so the smallest pops first."],
        notes=[GRAPH_NOTE],
        explanations=["1,2,4,3.", "Only node 1 is reachable."],
    ))

    add(P(
        "shortest-path-unweighted", "Shortest Path In Unweighted Graph", "medium", T, BFS,
        "Print the fewest edges on a path from node `1` to node `n` in the undirected graph, or `-1` if "
        "`n` is unreachable.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _shortest_unweighted(n, edges),
        [(5, [(1, 2), (2, 5), (1, 3)]), (4, [(1, 2)])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["BFS explores nodes in order of increasing distance, so the first time you reach n is optimal.",
         "Store distances in an array initialised to -1 to double as the visited marker.",
         "Dijkstra is unnecessary when every edge costs the same.",
         "n = 1 means the answer is 0."],
        notes=[GRAPH_NOTE],
        explanations=["1-2-5 uses 2 edges.", "Node 4 is unreachable."],
    ))

    add(P(
        "all-shortest-distances", "Distances From Source", "medium", T, BFS,
        "Print the fewest edges from node `1` to every node `1..n`, space separated, using `-1` for "
        "unreachable nodes.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT_LIST,
        lambda n, edges: _bfs_distances(n, edges),
        [(4, [(1, 2), (2, 3)]), (2, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["One BFS from the source fills every distance.",
         "The distance to the source itself is 0.",
         "Nodes never dequeued stay at -1."],
        notes=[GRAPH_NOTE],
        explanations=["0,1,2,-1.", "0,-1."],
    ))

    add(P(
        "detect-cycle-undirected", "Cycle In Undirected Graph", "medium", T, CC,
        "Print `YES` if the undirected graph contains a cycle, else `NO`.",
        [p_int("n", "number of nodes"), p_edges()], OUT_BOOL,
        lambda n, edges: _has_cycle_undirected(n, edges),
        [(3, [(1, 2), (2, 3), (1, 3)]), (3, [(1, 2), (2, 3)])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "no repeated edges"],
        ["During DFS, an edge to an already visited node that is not the parent closes a cycle.",
         "Remember to skip only the immediate parent, not every visited neighbour.",
         "Union-Find is an alternative: an edge joining two nodes already in the same set forms a cycle.",
         "Check every component, since the cycle may not be reachable from node 1."],
        notes=[GRAPH_NOTE],
        explanations=["The triangle is a cycle.", "The graph is a path."],
    ))

    add(P(
        "detect-cycle-directed", "Cycle In Directed Graph", "medium", T, TOPO,
        "The edges are directed from `u` to `v`. Print `YES` if the graph contains a directed cycle, else "
        "`NO`.",
        [p_int("n", "number of nodes"), p_edges("edges", "each pair is a directed edge u -> v")],
        OUT_BOOL, lambda n, edges: _has_cycle_directed(n, edges),
        [(3, [(1, 2), (2, 3), (3, 1)]), (3, [(1, 2), (2, 3)])],
        lambda rng: [(lambda n: (n, dag_edges(rng, n, 0.3) if rng.random() < 0.5
                                 else [(rng.randint(1, n), rng.randint(1, n)) for _ in range(n)]))(n)
                     for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["DFS with three colours: unvisited, in progress and finished.",
         "An edge back to an in-progress node is a cycle; an edge to a finished node is not.",
         "Kahn's algorithm is the alternative — leftover nodes after the topological sort form cycles.",
         "Self-loops count as cycles."],
        notes=[GRAPH_NOTE],
        explanations=["1->2->3->1 is a cycle.", "The graph is a chain."],
    ))

    add(P(
        "topological-sort-order", "Topological Sort", "medium", T, TOPO,
        "The edges are directed and the graph is acyclic. Print a topological order of the nodes, always "
        "choosing the smallest available node next.",
        [p_int("n", "number of nodes"), p_edges("edges", "each pair is a directed edge u -> v")],
        OUT_INT_LIST, lambda n, edges: _topological(n, edges),
        [(4, [(1, 2), (1, 3), (3, 4)]), (2, [])],
        lambda rng: [(n, dag_edges(rng, n, 0.3)) for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "the graph is acyclic"],
        ["Kahn's algorithm repeatedly removes a node with in-degree 0.",
         "Use a min-heap instead of a plain queue to always take the smallest such node.",
         "Decrement each neighbour's in-degree as you remove a node, pushing it when it hits 0.",
         "The tie-break rule is what makes the answer unique."],
        notes=[GRAPH_NOTE],
        explanations=["1,2,3,4.", "1,2."],
    ))

    add(P(
        "is-bipartite-graph", "Bipartite Check", "medium", T, CC,
        "Print `YES` if the undirected graph can be 2-coloured so no edge joins same-coloured nodes, else "
        "`NO`.",
        [p_int("n", "number of nodes"), p_edges()], OUT_BOOL,
        lambda n, edges: _is_bipartite(n, edges),
        [(4, [(1, 2), (2, 3), (3, 4)]), (3, [(1, 2), (2, 3), (1, 3)])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["BFS from each unvisited node, colouring neighbours the opposite colour.",
         "A conflict means an odd-length cycle exists and the graph is not bipartite.",
         "Every component must be checked separately.",
         "A graph with no edges is trivially bipartite."],
        notes=[GRAPH_NOTE],
        explanations=["A path is always bipartite.", "The triangle has an odd cycle."],
    ))

    add(P(
        "dijkstra-shortest-path", "Dijkstra Shortest Path", "hard", T, BFS,
        "Each edge `u v w` is undirected with positive weight `w`. Print the minimum total weight of a "
        "path from node `1` to node `n`, or `-1` if unreachable.",
        [p_int("n", "number of nodes"), p_weighted()], OUT_INT,
        lambda n, edges: _dijkstra(n, edges),
        [(4, [(1, 2, 1), (2, 4, 2), (1, 3, 5), (3, 4, 1)]), (2, [])],
        g_weighted(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "1 <= w <= 10^4"],
        ["Use a min-heap keyed by the tentative distance.",
         "Pop the closest unfinished node and relax its outgoing edges.",
         "Skip a popped entry whose distance is stale — that replaces a decrease-key operation.",
         "Positive weights are what make the greedy choice safe; negatives need Bellman-Ford."],
        notes=[GRAPH_NOTE],
        explanations=["1-2-4 costs 3.", "Node 2 is unreachable."],
        brute=lambda n, edges: _bellman_ford(n, edges),
    ))

    add(P(
        "all-pairs-shortest-total", "Sum Of All Pairs Distances", "hard", T, BFS,
        "Each edge `u v w` is undirected with positive weight. Print the sum of the shortest distances "
        "over every unordered pair of distinct nodes, ignoring pairs that are unreachable.",
        [p_int("n", "number of nodes"), p_weighted()], OUT_INT,
        lambda n, edges: _all_pairs_sum(n, edges),
        [(3, [(1, 2, 1), (2, 3, 2)]), (2, [])],
        g_weighted((1, 2, 3, 5, 9, 18, 40, 70)),
        ["1 <= n <= 200", "0 <= number of edges <= 5000", "1 <= w <= 10^4",
         "the answer fits in a 64-bit signed integer"],
        ["Floyd-Warshall computes all pairs in O(n^3) with a triple loop.",
         "Initialise the diagonal to 0 and each edge to its weight, keeping the smallest parallel edge.",
         "Then relax through every intermediate node k.",
         "Running Dijkstra from each node is O(n * m log n) and also fine here."],
        notes=[GRAPH_NOTE],
        explanations=["1-2 is 1, 2-3 is 2 and 1-3 is 3, totalling 6.", "No pair is connected."],
    ))

    add(P(
        "minimum-spanning-tree-weight", "Minimum Spanning Tree Weight", "hard", T + ["Union-Find"],
        ["Union-Find"],
        "Each edge `u v w` is undirected with positive weight. Print the total weight of a minimum "
        "spanning tree, or `-1` if the graph is not connected.",
        [p_int("n", "number of nodes"), p_weighted()], OUT_INT,
        lambda n, edges: _mst_weight(n, edges),
        [(4, [(1, 2, 1), (2, 3, 2), (3, 4, 3), (1, 4, 10)]), (3, [(1, 2, 5)])],
        g_weighted(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "1 <= w <= 10^4"],
        ["Kruskal's algorithm sorts the edges and adds each one that joins two different components.",
         "Union-Find with path compression makes the component test near-constant.",
         "Stop once n-1 edges are chosen; fewer means the graph is disconnected.",
         "Prim's algorithm with a heap is the alternative."],
        notes=[GRAPH_NOTE],
        explanations=["Edges of weight 1, 2 and 3 total 6.", "Node 3 is isolated."],
    ))

    add(P(
        "count-paths-in-dag", "Count Paths In DAG", "medium", T + ["Dynamic Programming"], TOPO,
        "The edges are directed and acyclic. Print the number of distinct directed paths from node `1` to "
        "node `n`.",
        [p_int("n", "number of nodes"), p_edges("edges", "each pair is a directed edge u -> v")],
        OUT_INT, lambda n, edges: _count_dag_paths(n, edges),
        [(4, [(1, 2), (1, 3), (2, 4), (3, 4)]), (3, [(1, 2)])],
        lambda rng: [(n, dag_edges(rng, n, 0.35)) for n in (1, 2, 3, 5, 9, 16, 30, 60)],
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "the graph is acyclic",
         "the answer fits in a 64-bit signed integer"],
        ["Process nodes in topological order so every predecessor is finalised first.",
         "paths[v] is the sum of paths[u] over all edges u -> v, with paths[1] = 1.",
         "Memoised DFS achieves the same thing without an explicit sort.",
         "The answer is 0 when node n is unreachable; n = 1 gives 1."],
        notes=[GRAPH_NOTE],
        explanations=["1-2-4 and 1-3-4.", "Node 3 is unreachable."],
    ))

    add(P(
        "node-with-max-degree", "Node With Highest Degree", "easy", T, CC,
        "Print the node with the most incident edges in the undirected graph, breaking ties by the "
        "smallest node number.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _max_degree_node(n, edges),
        [(4, [(1, 2), (1, 3), (2, 3)]), (2, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Count incidences per node while reading the edges.",
         "Each undirected edge adds 1 to both endpoints.",
         "Scan nodes in increasing order so ties resolve to the smallest."],
        notes=[GRAPH_NOTE],
        explanations=["Nodes 1, 2 and 3 all have degree 2, so 1 wins.", "All degrees are 0."],
    ))

    add(P(
        "count-islands-in-graph-rows", "Count Reachable From Source", "easy", T, BFS,
        "Print how many nodes are reachable from node `1` in the undirected graph, including node `1` "
        "itself.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: len(_bfs_order(n, edges)),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Run one BFS or DFS from node 1 and count the visited nodes.",
         "The source always counts, so the answer is at least 1.",
         "Nodes in other components are not reachable."],
        notes=[GRAPH_NOTE],
        explanations=["Nodes 1, 2 and 3.", "Only node 1."],
    ))

    add(P(
        "shortest-cycle-length-undirected", "Shortest Cycle Length", "hard", T, BFS,
        "Print the number of edges in the shortest cycle of the undirected graph, or `-1` if it is acyclic.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _girth(n, edges),
        [(4, [(1, 2), (2, 3), (3, 1), (3, 4)]), (3, [(1, 2), (2, 3)])],
        g_undirected((1, 2, 3, 5, 9, 16, 30, 60)),
        ["1 <= n <= 200", "0 <= number of edges <= 2000", "no repeated edges", "u != v"],
        ["Run a BFS from every node, tracking each node's parent.",
         "Meeting a visited node that is not the parent closes a cycle of length dist[u] + dist[v] + 1.",
         "Take the minimum over all starting nodes.",
         "This finds the girth in O(n * m)."],
        notes=[GRAPH_NOTE],
        explanations=["The triangle 1-2-3 has 3 edges.", "The graph is a path."],
    ))

    add(P(
        "count-edges-to-make-connected", "Edges To Connect Graph", "medium", T + ["Union-Find"], CC,
        "Print the minimum number of edges to add so the undirected graph becomes connected.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _count_components(n, edges) - 1,
        [(4, [(1, 2), (3, 4)]), (1, [])],
        g_undirected(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Count the connected components first.",
         "Joining c components into one always takes exactly c-1 edges.",
         "A single node needs no edges."],
        notes=[GRAPH_NOTE],
        explanations=["Two components need one edge.", "Already connected."],
    ))

    add(P(
        "bipartite-color-counts", "Two Colouring Sizes", "medium", T, CC,
        "The undirected graph is bipartite. 2-colour it so that in every component the node with the "
        "smallest number gets colour 0. Print the total count of colour-0 nodes followed by the count of "
        "colour-1 nodes.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT_LIST,
        lambda n, edges: _bipartite_counts(n, edges),
        [(4, [(1, 2), (3, 4)]), (2, [])],
        lambda rng: [(lambda n: (n, _bipartite_edges(rng, n)))(n) for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= n <= 2000", "0 <= number of edges <= 5000", "the graph is bipartite"],
        ["BFS each component from its smallest node, alternating colours by BFS level.",
         "Isolated nodes all receive colour 0.",
         "Sum the two colour counts across every component."],
        notes=[GRAPH_NOTE],
        out_desc="Print `colour0Count colour1Count`.",
        explanations=["Nodes 1 and 3 get colour 0; 2 and 4 get colour 1.", "Both nodes are isolated."],
    ))

    add(P(
        "eventual-safe-nodes-count", "Count Nodes Not In Cycles", "hard", T, TOPO,
        "The edges are directed. A node is safe when every path from it eventually terminates. Print how "
        "many nodes are safe.",
        [p_int("n", "number of nodes"), p_edges("edges", "each pair is a directed edge u -> v")],
        OUT_INT, lambda n, edges: _count_safe_nodes(n, edges),
        [(4, [(1, 2), (2, 3), (3, 2), (4, 1)]), (2, [])],
        lambda rng: [(lambda n: (n, [(rng.randint(1, n), rng.randint(1, n)) for _ in range(rng.randint(0, n))]))(n)
                     for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Reverse the graph and run Kahn's algorithm from nodes with out-degree 0.",
         "A node becomes safe once all of its successors are safe.",
         "Nodes that never get processed lie on or lead into a cycle.",
         "Three-colour DFS is the direct alternative."],
        notes=[GRAPH_NOTE],
        explanations=["Nodes 2 and 3 form a cycle, and both 1 and 4 lead into it, so no node is safe.",
                      "Neither node has an outgoing edge, so both are safe."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _adjacency(n, edges, directed=False):
    graph: list[list[int]] = [[] for _ in range(n + 1)]
    for u, v in edges:
        graph[u].append(v)
        if not directed:
            graph[v].append(u)
    for node in range(1, n + 1):
        graph[node].sort()
    return graph


def _count_components(n, edges):
    graph = _adjacency(n, edges)
    seen = [False] * (n + 1)
    components = 0
    for start in range(1, n + 1):
        if seen[start]:
            continue
        components += 1
        stack = [start]
        seen[start] = True
        while stack:
            node = stack.pop()
            for neighbour in graph[node]:
                if not seen[neighbour]:
                    seen[neighbour] = True
                    stack.append(neighbour)
    return components


def _largest_component(n, edges):
    graph = _adjacency(n, edges)
    seen = [False] * (n + 1)
    best = 0
    for start in range(1, n + 1):
        if seen[start]:
            continue
        size = 0
        stack = [start]
        seen[start] = True
        while stack:
            node = stack.pop()
            size += 1
            for neighbour in graph[node]:
                if not seen[neighbour]:
                    seen[neighbour] = True
                    stack.append(neighbour)
        best = max(best, size)
    return best


def _bfs_order(n, edges):
    graph = _adjacency(n, edges)
    seen = [False] * (n + 1)
    order = []
    queue = deque([1])
    seen[1] = True
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbour in graph[node]:
            if not seen[neighbour]:
                seen[neighbour] = True
                queue.append(neighbour)
    return order


def _dfs_order(n, edges):
    graph = _adjacency(n, edges)
    seen = [False] * (n + 1)
    order = []
    stack = [1]
    while stack:
        node = stack.pop()
        if seen[node]:
            continue
        seen[node] = True
        order.append(node)
        for neighbour in reversed(graph[node]):
            if not seen[neighbour]:
                stack.append(neighbour)
    return order


def _bfs_distances(n, edges):
    graph = _adjacency(n, edges)
    distance = [-1] * (n + 1)
    distance[1] = 0
    queue = deque([1])
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if distance[neighbour] == -1:
                distance[neighbour] = distance[node] + 1
                queue.append(neighbour)
    return distance[1:]


def _shortest_unweighted(n, edges):
    return _bfs_distances(n, edges)[n - 1]


def _has_cycle_undirected(n, edges):
    graph = _adjacency(n, edges)
    seen = [False] * (n + 1)
    for start in range(1, n + 1):
        if seen[start]:
            continue
        stack = [(start, 0)]
        seen[start] = True
        while stack:
            node, parent = stack.pop()
            for neighbour in graph[node]:
                if neighbour == parent:
                    continue
                if seen[neighbour]:
                    return True
                seen[neighbour] = True
                stack.append((neighbour, node))
    return False


def _has_cycle_directed(n, edges):
    graph = _adjacency(n, edges, directed=True)
    state = [0] * (n + 1)

    for start in range(1, n + 1):
        if state[start] != 0:
            continue
        stack = [(start, iter(graph[start]))]
        state[start] = 1
        while stack:
            node, iterator = stack[-1]
            advanced = False
            for neighbour in iterator:
                if state[neighbour] == 1:
                    return True
                if state[neighbour] == 0:
                    state[neighbour] = 1
                    stack.append((neighbour, iter(graph[neighbour])))
                    advanced = True
                    break
            if not advanced:
                state[node] = 2
                stack.pop()
    return False


def _topological(n, edges):
    graph = _adjacency(n, edges, directed=True)
    indegree = [0] * (n + 1)
    for _, v in edges:
        indegree[v] += 1
    heap = [node for node in range(1, n + 1) if indegree[node] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                heapq.heappush(heap, neighbour)
    return order


def _is_bipartite(n, edges):
    graph = _adjacency(n, edges)
    colour = [-1] * (n + 1)
    for start in range(1, n + 1):
        if colour[start] != -1:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbour in graph[node]:
                if colour[neighbour] == -1:
                    colour[neighbour] = 1 - colour[node]
                    queue.append(neighbour)
                elif colour[neighbour] == colour[node]:
                    return False
    return True


def _bipartite_edges(rng, n):
    """Random bipartite graph: split the nodes, only join across the split."""
    if n == 1:
        return []
    left = [node for node in range(1, n + 1) if rng.random() < 0.5]
    right = [node for node in range(1, n + 1) if node not in set(left)]
    if not left or not right:
        return []
    edges = set()
    for _ in range(rng.randint(0, n)):
        u = rng.choice(left)
        v = rng.choice(right)
        edges.add((min(u, v), max(u, v)))
    return sorted(edges)


def _bipartite_counts(n, edges):
    graph = _adjacency(n, edges)
    colour = [-1] * (n + 1)
    counts = [0, 0]
    for start in range(1, n + 1):
        if colour[start] != -1:
            continue
        colour[start] = 0
        counts[0] += 1
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbour in graph[node]:
                if colour[neighbour] == -1:
                    colour[neighbour] = 1 - colour[node]
                    counts[colour[neighbour]] += 1
                    queue.append(neighbour)
    return counts


def _weighted_adjacency(n, edges):
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n + 1)]
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    return graph


def _dijkstra(n, edges):
    graph = _weighted_adjacency(n, edges)
    INF = float("inf")
    distance = [INF] * (n + 1)
    distance[1] = 0
    heap = [(0, 1)]
    while heap:
        cost, node = heapq.heappop(heap)
        if cost > distance[node]:
            continue
        for neighbour, weight in graph[node]:
            candidate = cost + weight
            if candidate < distance[neighbour]:
                distance[neighbour] = candidate
                heapq.heappush(heap, (candidate, neighbour))
    return -1 if distance[n] == INF else int(distance[n])


def _bellman_ford(n, edges):
    INF = float("inf")
    distance = [INF] * (n + 1)
    distance[1] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if distance[u] + w < distance[v]:
                distance[v] = distance[u] + w
                changed = True
            if distance[v] + w < distance[u]:
                distance[u] = distance[v] + w
                changed = True
        if not changed:
            break
    return -1 if distance[n] == INF else int(distance[n])


def _all_pairs_sum(n, edges):
    INF = float("inf")
    dist = [[INF] * (n + 1) for _ in range(n + 1)]
    for node in range(1, n + 1):
        dist[node][node] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)
    for k in range(1, n + 1):
        row_k = dist[k]
        for i in range(1, n + 1):
            via = dist[i][k]
            if via == INF:
                continue
            row_i = dist[i]
            for j in range(1, n + 1):
                candidate = via + row_k[j]
                if candidate < row_i[j]:
                    row_i[j] = candidate
    total = 0
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if dist[i][j] != INF:
                total += dist[i][j]
    return int(total)


def _mst_weight(n, edges):
    parent = list(range(n + 1))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    total = 0
    used = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            used += 1
    return total if used == n - 1 else -1


def _count_dag_paths(n, edges):
    graph = _adjacency(n, edges, directed=True)
    order = _topological(n, edges)
    paths = [0] * (n + 1)
    paths[1] = 1
    for node in order:
        if paths[node] == 0:
            continue
        for neighbour in graph[node]:
            paths[neighbour] += paths[node]
    return paths[n]


def _max_degree_node(n, edges):
    degree = [0] * (n + 1)
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    best_node = 1
    for node in range(1, n + 1):
        if degree[node] > degree[best_node]:
            best_node = node
    return best_node


def _girth(n, edges):
    graph = _adjacency(n, edges)
    best = None
    for start in range(1, n + 1):
        distance = [-1] * (n + 1)
        parent = [0] * (n + 1)
        distance[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbour in graph[node]:
                if distance[neighbour] == -1:
                    distance[neighbour] = distance[node] + 1
                    parent[neighbour] = node
                    queue.append(neighbour)
                elif neighbour != parent[node]:
                    length = distance[node] + distance[neighbour] + 1
                    best = length if best is None else min(best, length)
    return best if best is not None else -1


def _count_safe_nodes(n, edges):
    reverse: list[list[int]] = [[] for _ in range(n + 1)]
    outdegree = [0] * (n + 1)
    for u, v in edges:
        reverse[v].append(u)
        outdegree[u] += 1
    queue = deque(node for node in range(1, n + 1) if outdegree[node] == 0)
    safe = [False] * (n + 1)
    for node in queue:
        safe[node] = True
    while queue:
        node = queue.popleft()
        for predecessor in reverse[node]:
            outdegree[predecessor] -= 1
            if outdegree[predecessor] == 0:
                safe[predecessor] = True
                queue.append(predecessor)
    return sum(1 for node in range(1, n + 1) if safe[node])
