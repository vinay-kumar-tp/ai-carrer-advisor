"""Disjoint set union problems."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    PAIR_LIST,
    Param,
    connected_edges,
    p_int,
)

T = ["Union-Find"]
UF = ["Union-Find"]


def p_edges(name="edges", desc="each pair is an edge u v"):
    return Param(name, PAIR_LIST, desc)


def g_graphs(sizes=(1, 2, 3, 5, 9, 18, 45, 120)):
    def gen(rng: random.Random):
        cases = []
        for n in sizes:
            if n == 1:
                cases.append((1, []))
                continue
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


def specs():
    out: list = []
    add = out.append

    add(P(
        "dsu-count-sets", "Count Disjoint Sets", "medium", T + ["Graphs"], UF,
        "Start with `n` singleton sets numbered 1 to `n`. Each pair unions the two sets containing those "
        "elements. Print how many sets remain.",
        [p_int("n", "number of elements"), p_edges("unions", "each pair unions u and v")], OUT_INT,
        lambda n, unions: _count_sets(n, unions),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of unions <= 5000", "1 <= u, v <= n"],
        ["Keep a parent array where each element initially points at itself.",
         "Find follows parents to the representative; union links one representative under the other.",
         "Every successful union reduces the set count by one.",
         "Path compression and union by rank make the operations near-constant."],
        explanations=["{1,2,3} and {4,5}.", "Three singletons."],
    ))

    add(P(
        "dsu-are-connected", "Are Elements Connected", "medium", T + ["Graphs"], UF,
        "After applying every union, print `YES` if elements `a` and `b` are in the same set, else `NO`.",
        [p_int("n", "number of elements"), p_edges("unions", "each pair unions u and v"),
         p_int("a"), p_int("b")], OUT_BOOL,
        lambda n, unions, a, b: _find_root(n, unions, a) == _find_root(n, unions, b),
        [(5, [(1, 2), (2, 3)], 1, 3), (5, [(1, 2)], 1, 5)],
        lambda rng: [(lambda pair: (pair[0], pair[1], rng.randint(1, pair[0]), rng.randint(1, pair[0])))(case)
                     for case in g_graphs()(rng)],
        ["1 <= n <= 2000", "0 <= number of unions <= 5000", "1 <= a, b <= n"],
        ["Apply all unions first, then compare the two representatives.",
         "Two elements are connected exactly when they share a representative.",
         "Comparing parents directly is wrong — you must follow the chain to the root."],
        explanations=["1 and 3 joined through 2.", "5 was never unioned."],
    ))

    add(P(
        "dsu-largest-set-size", "Largest Set Size", "medium", T + ["Graphs"], UF,
        "After applying every union, print the size of the largest set.",
        [p_int("n", "number of elements"), p_edges("unions", "each pair unions u and v")], OUT_INT,
        lambda n, unions: _largest_set(n, unions),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of unions <= 5000"],
        ["Maintain a size array alongside the parent array.",
         "On union, add the smaller set's size into the larger representative.",
         "Track the running maximum, or scan the sizes at the end.",
         "With no unions every set has size 1."],
        explanations=["{1,2,3} has 3 elements.", "All sets are singletons."],
    ))

    add(P(
        "dsu-redundant-connection", "First Redundant Edge", "medium", T + ["Graphs"], UF,
        "Process the edges in order. Print the two endpoints of the first edge that joins two already "
        "connected nodes, or `-1` if no edge is redundant.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT_LIST,
        lambda n, edges: _redundant_edge(n, edges),
        [(3, [(1, 2), (1, 3), (2, 3)]), (3, [(1, 2)])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Union each edge in order.",
         "When both endpoints already share a representative, that edge closes a cycle.",
         "Report the first such edge and stop.",
         "Print -1 on a single line when the graph stays a forest."],
        explanations=["The third edge closes the triangle.", "No cycle forms."],
        out_desc="Print `u v` for the redundant edge, or -1.",
    ))

    add(P(
        "dsu-count-cycles-formed", "Count Cycle Forming Edges", "medium", T + ["Graphs"], UF,
        "Process the edges in order and print how many of them join two nodes that were already connected.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _count_cycle_edges(n, edges),
        [(3, [(1, 2), (1, 3), (2, 3)]), (3, [(1, 2)])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Union each edge and count the failures.",
         "A failed union means both endpoints already shared a component.",
         "The successful unions form a spanning forest."],
        explanations=["Only the last edge is redundant.", "No redundant edge."],
    ))

    add(P(
        "dsu-min-edges-to-connect", "Edges Needed To Connect", "medium", T + ["Graphs"], UF,
        "Print the minimum number of extra edges needed to make every node connected, or `-1` if the "
        "existing edges cannot be rearranged to do it. You may only reuse edges that are currently "
        "redundant.",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: _edges_to_connect(n, edges),
        [(4, [(1, 2), (1, 3), (2, 3)]), (4, [(1, 2)])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Count components and count redundant edges with Union-Find.",
         "Joining c components needs c-1 edges, which must come from the redundant pool.",
         "If there are fewer redundant edges than c-1, print -1.",
         "Otherwise the answer is c-1."],
        explanations=["One redundant edge covers the single missing link.",
                      "Two links are missing but only zero spare edges exist."],
    ))

    add(P(
        "dsu-accounts-merge-count", "Merge Groups By Shared Items", "medium", T + ["Hashing"], UF,
        "Each pair `(a, b)` says items `a` and `b` belong to the same owner. Print how many distinct owners "
        "there are among items 1 to `n`.",
        [p_int("n", "number of items"), p_edges("links", "each pair links two items")], OUT_INT,
        lambda n, links: _count_sets(n, links),
        [(6, [(1, 2), (3, 4), (4, 5)]), (2, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of links <= 5000"],
        ["This is component counting in disguise.",
         "Union every linked pair, then count distinct representatives.",
         "Unlinked items are their own owner."],
        explanations=["{1,2}, {3,4,5} and {6} give 3.", "Two separate owners."],
    ))

    add(P(
        "dsu-number-of-provinces", "Number Of Provinces", "medium", T + ["Matrix", "Graphs"], UF,
        "The `n x n` matrix `isConnected` uses 1 to mark a direct connection. Print the number of "
        "provinces, where a province is a maximal set of directly or indirectly connected cities.",
        [Param("isConnected", "int[][]", "symmetric adjacency matrix of 0/1")], OUT_INT,
        lambda isConnected: _count_provinces(isConnected),
        [([[1, 1, 0], [1, 1, 0], [0, 0, 1]],), ([[1]],)],
        lambda rng: [(_symmetric_matrix(rng, n),) for n in (1, 2, 3, 4, 6, 9, 14, 20)],
        ["1 <= n <= 200", "isConnected[i][j] is 0 or 1", "the matrix is symmetric",
         "isConnected[i][i] is 1"],
        ["Union i and j whenever the matrix marks them connected.",
         "Only the upper triangle needs scanning since the matrix is symmetric.",
         "The answer is the number of distinct representatives.",
         "A DFS over the matrix works equally well."],
        explanations=["Cities 0 and 1 form one province, city 2 another.", "A single city."],
    ))

    add(P(
        "dsu-equations-satisfiable", "Equality Constraints Satisfiable", "medium", T, UF,
        "The first `equalCount` pairs assert `a == b`; the remaining pairs assert `a != b`. Print `YES` if "
        "all the constraints can hold simultaneously, else `NO`.",
        [p_int("n", "number of variables"), p_edges("constraints", "equality pairs then inequality pairs"),
         p_int("equalCount", "how many leading pairs are equalities")], OUT_BOOL,
        lambda n, constraints, equalCount: _equations_satisfiable(n, constraints, equalCount),
        [(3, [(1, 2), (2, 3), (1, 3)], 2), (3, [(1, 2), (1, 2)], 1)],
        lambda rng: [(lambda pair: (pair[0], pair[1], rng.randint(0, len(pair[1]))))(case)
                     for case in g_graphs()(rng)],
        ["1 <= n <= 2000", "0 <= number of constraints <= 5000",
         "0 <= equalCount <= number of constraints"],
        ["Union all the equalities first so every equal group collapses to one representative.",
         "Then check each inequality: it fails if both sides share a representative.",
         "Processing inequalities before equalities would give wrong answers.",
         "A variable is always equal to itself, so `a != a` is unsatisfiable."],
        explanations=["1==2 and 2==3 force 1==3, contradicting 1!=3.",
                      "1==2 then 1!=2 contradict each other."],
    ))

    add(P(
        "dsu-count-islands-pairs", "Count Connected Pairs", "medium", T + ["Graphs"], UF,
        "After applying every union, count the pairs of distinct elements that belong to the same set.",
        [p_int("n", "number of elements"), p_edges("unions", "each pair unions u and v")], OUT_INT,
        lambda n, unions: _count_connected_pairs(n, unions),
        [(5, [(1, 2), (2, 3), (4, 5)]), (3, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of unions <= 5000",
         "the answer fits in a 64-bit signed integer"],
        ["Compute each set's size after all unions.",
         "A set of size s contributes s*(s-1)/2 pairs.",
         "Sum that formula over the distinct representatives.",
         "Singletons contribute nothing."],
        explanations=["3 pairs inside {1,2,3} plus 1 inside {4,5} gives 4.", "No pairs."],
    ))

    add(P(
        "dsu-smallest-representative", "Smallest Element Per Set", "medium", T, UF,
        "After applying every union, print for each element 1 to `n` the smallest element in its set, space "
        "separated.",
        [p_int("n", "number of elements"), p_edges("unions", "each pair unions u and v")], OUT_INT_LIST,
        lambda n, unions: _smallest_per_set(n, unions),
        [(5, [(1, 3), (3, 5)]), (2, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of unions <= 5000"],
        ["Track the minimum element alongside each representative.",
         "On union, the merged set's minimum is the smaller of the two.",
         "Alternatively group elements by representative and take each group's minimum."],
        explanations=["1,2,1,4,1.", "1,2."],
    ))

    add(P(
        "dsu-kruskal-tree-edges", "Spanning Forest Edge Count", "medium", T + ["Graphs"], UF,
        "Print how many of the given edges a Union-Find sweep would accept when building a spanning forest "
        "(that is, the number of successful unions).",
        [p_int("n", "number of nodes"), p_edges()], OUT_INT,
        lambda n, edges: n - _count_sets(n, edges),
        [(4, [(1, 2), (2, 3), (1, 3)]), (3, [])],
        g_graphs(),
        ["1 <= n <= 2000", "0 <= number of edges <= 5000"],
        ["Each successful union reduces the component count by exactly one.",
         "Starting from n components and ending at c, exactly n - c unions succeeded.",
         "A connected graph accepts n-1 edges."],
        explanations=["Two edges are accepted, the third closes a cycle.", "No edges to accept."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

class _DSU:
    def __init__(self, n: int):
        self.parent = list(range(n + 1))
        self.size = [1] * (n + 1)
        self.smallest = list(range(n + 1))

    def find(self, node: int) -> int:
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.smallest[ra] = min(self.smallest[ra], self.smallest[rb])
        return True


def _build(n, unions):
    dsu = _DSU(n)
    for a, b in unions:
        dsu.union(a, b)
    return dsu


def _count_sets(n, unions):
    dsu = _build(n, unions)
    return len({dsu.find(node) for node in range(1, n + 1)})


def _find_root(n, unions, element):
    return _build(n, unions).find(element)


def _largest_set(n, unions):
    dsu = _build(n, unions)
    counts: dict[int, int] = {}
    for node in range(1, n + 1):
        root = dsu.find(node)
        counts[root] = counts.get(root, 0) + 1
    return max(counts.values())


def _redundant_edge(n, edges):
    dsu = _DSU(n)
    for a, b in edges:
        if not dsu.union(a, b):
            return [a, b]
    return [-1]


def _count_cycle_edges(n, edges):
    dsu = _DSU(n)
    return sum(1 for a, b in edges if not dsu.union(a, b))


def _edges_to_connect(n, edges):
    dsu = _DSU(n)
    spare = 0
    for a, b in edges:
        if not dsu.union(a, b):
            spare += 1
    components = len({dsu.find(node) for node in range(1, n + 1)})
    needed = components - 1
    return needed if spare >= needed else -1


def _symmetric_matrix(rng, n):
    mat = [[0] * n for _ in range(n)]
    for i in range(n):
        mat[i][i] = 1
    for i in range(n):
        for j in range(i + 1, n):
            value = 1 if rng.random() < 0.3 else 0
            mat[i][j] = value
            mat[j][i] = value
    return mat


def _count_provinces(isConnected):
    n = len(isConnected)
    dsu = _DSU(n)
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                dsu.union(i + 1, j + 1)
    return len({dsu.find(node) for node in range(1, n + 1)})


def _equations_satisfiable(n, constraints, equalCount):
    dsu = _DSU(n)
    for a, b in constraints[:equalCount]:
        dsu.union(a, b)
    for a, b in constraints[equalCount:]:
        if dsu.find(a) == dsu.find(b):
            return False
    return True


def _count_connected_pairs(n, unions):
    dsu = _build(n, unions)
    counts: dict[int, int] = {}
    for node in range(1, n + 1):
        root = dsu.find(node)
        counts[root] = counts.get(root, 0) + 1
    return sum(size * (size - 1) // 2 for size in counts.values())


def _smallest_per_set(n, unions):
    dsu = _build(n, unions)
    return [dsu.smallest[dsu.find(node)] for node in range(1, n + 1)]
