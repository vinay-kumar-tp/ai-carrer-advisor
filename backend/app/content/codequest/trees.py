"""Binary tree and binary search tree problems.

Trees arrive as level-order tokens where `null` marks a missing child, which is
the same encoding LeetCode uses.
"""

from __future__ import annotations

import random
from collections import deque

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    Param,
    TOKEN_LIST,
    TreeNode,
    bst_tokens,
    build_tree,
    ints,
    p_int,
    tree_tokens,
)

T = ["Trees"]
TT = ["Tree Traversal"]
TB = ["Tree BFS / DFS"]
SIZES = (1, 2, 3, 5, 9, 18, 45, 120)

TREE_NOTE = ("The tree is given in level order: read `n` tokens where each is either an integer or the "
             "word `null` for a missing child. `null` never has children of its own.")


def p_tree(name="tree", desc="level-order tokens, `null` for a missing child"):
    return Param(name, TOKEN_LIST, desc)


def g_tree(sizes=SIZES):
    def gen(rng: random.Random):
        return [(tree_tokens(rng, n),) for n in sizes]

    return gen


def g_bst(sizes=SIZES):
    def gen(rng: random.Random):
        return [(bst_tokens(rng.sample(range(1, 400), n)),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "tree-inorder-traversal", "Inorder Traversal", "easy", T, TT,
        "Print the values of the tree in inorder (left subtree, node, right subtree), space separated.",
        [p_tree()], OUT_INT_LIST, lambda tree: _inorder(build_tree(tree)),
        [(["1", "null", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Recurse left, visit the node, then recurse right.",
         "Iteratively, push left children onto a stack, then pop and go right.",
         "An empty tree produces an empty line."],
        notes=[TREE_NOTE],
        explanations=["1,3,2.", "The tree is empty."],
    ))

    add(P(
        "tree-preorder-traversal", "Preorder Traversal", "easy", T, TT,
        "Print the values of the tree in preorder (node, left subtree, right subtree), space separated.",
        [p_tree()], OUT_INT_LIST, lambda tree: _preorder(build_tree(tree)),
        [(["1", "null", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Visit the node before its children.",
         "With a stack, push the right child before the left so the left pops first.",
         "Preorder is the traversal used to serialise a tree."],
        notes=[TREE_NOTE],
        explanations=["1,2,3.", "The tree is empty."],
    ))

    add(P(
        "tree-postorder-traversal", "Postorder Traversal", "easy", T, TT,
        "Print the values of the tree in postorder (left subtree, right subtree, node), space separated.",
        [p_tree()], OUT_INT_LIST, lambda tree: _postorder(build_tree(tree)),
        [(["1", "null", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Visit both children before the node itself.",
         "A neat trick: do a modified preorder (node, right, left) and reverse the result.",
         "Postorder is what you need when freeing or aggregating from the leaves up."],
        notes=[TREE_NOTE],
        explanations=["3,2,1.", "The tree is empty."],
    ))

    add(P(
        "tree-level-order-traversal", "Level Order Traversal", "easy", T, TB,
        "Print the values of the tree level by level, left to right within each level, space separated.",
        [p_tree()], OUT_INT_LIST, lambda tree: _level_order(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Use a queue seeded with the root.",
         "Pop a node, print it, then push its children.",
         "Skip null children so they never enter the queue."],
        notes=[TREE_NOTE],
        explanations=["3,9,20,15,7.", "The tree is empty."],
    ))

    add(P(
        "tree-height", "Tree Height", "easy", T, TB,
        "Print the height of the tree, counted as the number of nodes on the longest root-to-leaf path. "
        "An empty tree has height `0`.",
        [p_tree()], OUT_INT, lambda tree: _height(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["The height is 1 plus the taller of the two subtree heights.",
         "The base case is an empty subtree with height 0.",
         "A BFS counting levels gives the same answer iteratively."],
        notes=[TREE_NOTE],
        explanations=["The longest path has 3 nodes.", "An empty tree."],
    ))

    add(P(
        "count-tree-nodes", "Count Nodes", "easy", T, TB,
        "Print how many nodes the binary tree contains. An empty tree has `0` nodes.",
        [p_tree()], OUT_INT, lambda tree: _count(build_tree(tree)),
        [(["1", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["The count is 1 plus the counts of both subtrees.",
         "Any traversal order works since every node is visited exactly once.",
         "An empty tree has 0 nodes."],
        notes=[TREE_NOTE],
    ))

    add(P(
        "count-tree-leaves", "Count Leaves", "easy", T, TB,
        "Print the number of leaf nodes (nodes with no children) in the tree.",
        [p_tree()], OUT_INT, lambda tree: _count_leaves(build_tree(tree)),
        [(["1", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["A node is a leaf when both children are absent.",
         "Recurse and sum the leaf counts of both subtrees.",
         "An empty tree has 0 leaves; a single node is one leaf."],
        notes=[TREE_NOTE],
        explanations=["2 and 3 are leaves.", "An empty tree."],
    ))

    add(P(
        "sum-of-tree-nodes", "Sum Of Tree", "easy", T, TB,
        "Print the sum of every node value in the tree. An empty tree sums to `0`.",
        [p_tree()], OUT_INT, lambda tree: _sum(build_tree(tree)),
        [(["1", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Add the node's value to the sums of both subtrees.",
         "The base case contributes 0.",
         "Any traversal order gives the same total."],
        notes=[TREE_NOTE],
    ))

    add(P(
        "max-value-in-tree", "Maximum Value In Tree", "easy", T, TB,
        "Print the largest node value in the tree. Print `-1000000000` if the tree is empty.",
        [p_tree()], OUT_INT, lambda tree: _max_value(build_tree(tree)),
        [(["1", "5", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Take the maximum of the node and both subtree maxima.",
         "Use a sentinel far below the value range for the empty case.",
         "This works for any binary tree, sorted or not."],
        notes=[TREE_NOTE],
    ))

    add(P(
        "tree-diameter", "Tree Diameter", "medium", T, TB,
        "Print the diameter of the tree, measured as the number of edges on the longest path between any "
        "two nodes.",
        [p_tree()], OUT_INT, lambda tree: _diameter(build_tree(tree)),
        [(["1", "2", "3", "4", "5"],), (["1"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["For each node, the longest path through it is leftHeight + rightHeight.",
         "Compute heights bottom-up and track the best sum seen.",
         "The path need not pass through the root, which is why every node must be considered.",
         "A single node has diameter 0."],
        notes=[TREE_NOTE],
        explanations=["The path 4-2-1-3 uses 3 edges.", "A single node."],
    ))

    add(P(
        "is-balanced-tree", "Balanced Binary Tree", "easy", T, TB,
        "Print `YES` if every node's two subtree heights differ by at most 1, else `NO`.",
        [p_tree()], OUT_BOOL, lambda tree: _is_balanced(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["1", "2", "null", "3"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Compute heights bottom-up and check the difference at every node.",
         "Returning a sentinel for 'already unbalanced' avoids recomputing heights.",
         "The naive version that calls height() inside the recursion is O(n^2)."],
        notes=[TREE_NOTE],
        explanations=["Both subtrees are close enough in height.", "The left side is two levels deeper."],
    ))

    add(P(
        "is-symmetric-tree", "Symmetric Tree", "easy", T, TB,
        "Print `YES` if the tree is a mirror image of itself around its centre, else `NO`.",
        [p_tree()], OUT_BOOL, lambda tree: _is_symmetric(build_tree(tree)),
        [(["1", "2", "2", "3", "4", "4", "3"],), (["1", "2", "2", "null", "3", "null", "3"],)],
        g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Compare the left subtree against the right subtree in mirrored order.",
         "Two nodes match when their values agree and left-vs-right pairs mirror each other.",
         "An empty tree is symmetric."],
        notes=[TREE_NOTE],
        explanations=["The two halves mirror each other.", "The 3s sit on the same side."],
    ))

    add(P(
        "invert-binary-tree", "Invert Binary Tree", "easy", T, TB,
        "Swap the two children of every node, then print the resulting tree in level order (values only, "
        "nulls omitted).",
        [p_tree()], OUT_INT_LIST, lambda tree: _level_order(_invert(build_tree(tree))),
        [(["4", "2", "7", "1", "3", "6", "9"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Swap the children at each node, then recurse into both.",
         "Doing the swap before or after the recursion both work.",
         "A BFS with a queue performs the same swaps iteratively."],
        notes=[TREE_NOTE],
        explanations=["4,7,2,9,6,3,1.", "An empty tree."],
    ))

    add(P(
        "left-view-of-tree", "Left View Of Tree", "medium", T, TB,
        "Print the first node encountered at each depth when scanning left to right, top to bottom.",
        [p_tree()], OUT_INT_LIST, lambda tree: _side_view(build_tree(tree), left=True),
        [(["1", "2", "3", "4", "5", "null", "6"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Do a level-order traversal and take the first node of each level.",
         "Alternatively use DFS, recording a node when its depth is seen for the first time.",
         "With DFS, visit the left child before the right."],
        notes=[TREE_NOTE],
        explanations=["1,2,4.", "An empty tree."],
    ))

    add(P(
        "right-view-of-tree", "Right View Of Tree", "medium", T, TB,
        "Print the last node encountered at each depth when scanning left to right, top to bottom.",
        [p_tree()], OUT_INT_LIST, lambda tree: _side_view(build_tree(tree), left=False),
        [(["1", "2", "3", "4", "5", "null", "6"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Take the last node of each level in a BFS.",
         "Or run DFS visiting the right child first and record each depth's first hit.",
         "The root is always part of the answer for a non-empty tree."],
        notes=[TREE_NOTE],
        explanations=["1,3,6.", "An empty tree."],
    ))

    add(P(
        "zigzag-level-order", "Zigzag Level Order", "medium", T, TB,
        "Print the tree level by level, alternating direction: the first level left to right, the second "
        "right to left, and so on.",
        [p_tree()], OUT_INT_LIST, lambda tree: _zigzag(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["Run a normal BFS but reverse the values of alternate levels before emitting them.",
         "Track the level index to decide the direction.",
         "Reversing after collecting a level is simpler than pushing children in a different order."],
        notes=[TREE_NOTE],
        explanations=["3,20,9,15,7.", "An empty tree."],
    ))

    add(P(
        "root-to-leaf-path-sum-exists", "Path Sum Exists", "easy", T, TB,
        "Print `YES` if some root-to-leaf path has values summing to `target`, else `NO`.",
        [p_tree(), p_int("target", "the required path sum")], OUT_BOOL,
        lambda tree, target: _has_path_sum(build_tree(tree), target),
        [(["5", "4", "8", "11", "null", "13", "4", "7", "2"], 22), (["1", "2"], 5)],
        lambda rng: [(tree_tokens(rng, n), rng.randint(1, 200)) for n in SIZES],
        ["0 <= number of nodes <= 2000", "-10^6 <= node value, target <= 10^6"],
        ["Carry the remaining target down the recursion.",
         "At a leaf, check whether the remaining amount equals the leaf's value.",
         "An empty tree has no root-to-leaf path, so the answer is NO.",
         "Do not stop at an internal node that happens to hit the target."],
        notes=[TREE_NOTE],
        explanations=["5+4+11+2 = 22.", "No leaf path sums to 5."],
    ))

    add(P(
        "max-root-to-leaf-sum", "Maximum Root To Leaf Sum", "medium", T, TB,
        "Print the largest sum along any root-to-leaf path. Print `0` for an empty tree.",
        [p_tree()], OUT_INT, lambda tree: _max_root_leaf(build_tree(tree)),
        [(["1", "2", "3"],), (["null"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["The answer at a node is its value plus the better of the two subtree answers.",
         "A leaf's answer is just its own value.",
         "Handle a missing child so it never contributes a spurious 0 path."],
        notes=[TREE_NOTE],
        explanations=["1+3 = 4.", "An empty tree."],
    ))

    add(P(
        "count-nodes-at-level", "Count Nodes At Depth", "easy", T, TB,
        "Print how many nodes sit at depth `d`, where the root is at depth `0`.",
        [p_tree(), p_int("d", "the depth to count")], OUT_INT,
        lambda tree, d: _count_at_depth(build_tree(tree), d),
        [(["1", "2", "3", "4"], 1), (["1"], 3)],
        lambda rng: [(tree_tokens(rng, n), rng.randint(0, 5)) for n in SIZES],
        ["0 <= number of nodes <= 2000", "0 <= d <= 2000"],
        ["Recurse while decreasing the remaining depth.",
         "When the remaining depth reaches 0, count the node and stop descending.",
         "A BFS counting the size of each level works too."],
        notes=[TREE_NOTE],
        explanations=["Depth 1 holds 2 and 3.", "The tree is not that deep."],
    ))

    add(P(
        "lowest-common-ancestor-bst", "Lowest Common Ancestor In BST", "medium", T, TB,
        "The tree is a binary search tree. Print the value of the lowest node that has both `p` and `q` "
        "as descendants (a node may be its own descendant). Both values are present in the tree.",
        [p_tree("bst", "level-order tokens of a BST"), p_int("p"), p_int("q")], OUT_INT,
        lambda bst, p, q: _lca_bst(build_tree(bst), p, q),
        [(["6", "2", "8", "0", "4", "7", "9"], 2, 8), (["2", "1"], 1, 2)],
        lambda rng: [(lambda values: (bst_tokens(values), rng.choice(values), rng.choice(values)))(
            rng.sample(range(1, 400), n)) for n in (1, 2, 3, 5, 9, 18, 45, 120)],
        ["1 <= number of nodes <= 2000", "the tree is a valid BST", "p and q are present in the tree"],
        ["Walk down from the root comparing both targets with the current value.",
         "If both are smaller go left; if both are larger go right.",
         "The first node that splits them (or equals one of them) is the answer.",
         "The BST ordering is what makes this O(height) without any recursion."],
        notes=[TREE_NOTE],
        explanations=["The root 6 splits 2 and 8.", "1 is below 2, so 2 is the ancestor."],
    ))

    add(P(
        "lowest-common-ancestor-binary-tree", "Lowest Common Ancestor", "medium", T, TB,
        "Print the value of the lowest node in the tree having both `p` and `q` as descendants (a node "
        "may be its own descendant). Both values are present and all values are distinct.",
        [p_tree(), p_int("p"), p_int("q")], OUT_INT,
        lambda tree, p, q: _lca(build_tree(tree), p, q),
        [(["3", "5", "1", "6", "2", "0", "8"], 5, 1), (["1", "2"], 2, 2)],
        lambda rng: [(lambda tokens: (lambda vals: (tokens, rng.choice(vals), rng.choice(vals)))(
            [int(t) for t in tokens if t != "null"]))(_distinct_tree(rng, n)) for n in SIZES],
        ["1 <= number of nodes <= 2000", "all values are distinct", "p and q are present"],
        ["Recurse into both subtrees looking for either target.",
         "If the two targets are found in different subtrees, the current node is the answer.",
         "If only one side returns something, propagate it upwards.",
         "Finding a target at the current node means that node is an ancestor of itself."],
        notes=[TREE_NOTE],
        explanations=["3 splits 5 and 1.", "A node is its own ancestor."],
    ))

    add(P(
        "validate-bst", "Validate Binary Search Tree", "medium", T, TB,
        "Print `YES` if the tree is a valid binary search tree (every left descendant is strictly smaller "
        "and every right descendant strictly larger), else `NO`.",
        [p_tree()], OUT_BOOL, lambda tree: _is_bst(build_tree(tree)),
        [(["2", "1", "3"],), (["5", "1", "4", "null", "null", "3", "6"],)],
        lambda rng: [(bst_tokens(rng.sample(range(1, 400), n)) if rng.random() < 0.5
                      else tree_tokens(rng, n),) for n in SIZES],
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Comparing a node only with its immediate children is not enough.",
         "Pass down an allowed (low, high) range and tighten it as you descend.",
         "Equivalently, an inorder traversal of a valid BST is strictly increasing.",
         "An empty tree is a valid BST."],
        notes=[TREE_NOTE],
        explanations=["Inorder gives 1,2,3.", "The 3 sits in the right subtree of 5 but is smaller."],
    ))

    add(P(
        "search-in-bst", "Search In BST", "easy", T, TB,
        "The tree is a binary search tree. Print `YES` if `target` appears in it, else `NO`.",
        [p_tree("bst", "level-order tokens of a BST"), p_int("target")], OUT_BOOL,
        lambda bst, target: _bst_contains(build_tree(bst), target),
        [(["4", "2", "7", "1", "3"], 2), (["4", "2", "7"], 5)],
        lambda rng: [(lambda values: (bst_tokens(values),
                                      rng.choice(values) if rng.random() < 0.6 else rng.randint(1, 400)))(
            rng.sample(range(1, 400), n)) for n in SIZES],
        ["1 <= number of nodes <= 2000", "the tree is a valid BST"],
        ["Compare the target with the current node and descend accordingly.",
         "Each comparison discards half the remaining tree.",
         "This costs O(height), which is O(log n) for a balanced BST."],
        notes=[TREE_NOTE],
    ))

    add(P(
        "kth-smallest-in-bst", "Kth Smallest In BST", "medium", T, TT,
        "The tree is a binary search tree. Print its `k`-th smallest value (1-based).",
        [p_tree("bst", "level-order tokens of a BST"), p_int("k", "1-based rank")], OUT_INT,
        lambda bst, k: _inorder(build_tree(bst))[k - 1],
        [(["3", "1", "4", "null", "2"], 1), (["2", "1"], 2)],
        lambda rng: [(lambda values: (bst_tokens(values), rng.randint(1, len(values))))(
            rng.sample(range(1, 400), n)) for n in SIZES],
        ["1 <= k <= number of nodes <= 2000", "the tree is a valid BST"],
        ["An inorder traversal of a BST yields sorted values.",
         "Stop as soon as you have visited k nodes.",
         "An iterative inorder with a stack lets you break out early."],
        notes=[TREE_NOTE],
        explanations=["The smallest value is 1.", "The 2nd smallest is 2."],
    ))

    add(P(
        "insert-into-bst-inorder", "Insert Into BST", "medium", T, TB,
        "Insert `value` into the binary search tree (the value is not already present) and print the "
        "resulting tree's inorder traversal.",
        [p_tree("bst", "level-order tokens of a BST"), p_int("value", "the value to insert")],
        OUT_INT_LIST, lambda bst, value: sorted(_inorder(build_tree(bst)) + [value]),
        [(["4", "2", "7", "1", "3"], 5), (["1"], 0)],
        lambda rng: [(lambda values: (bst_tokens(values),
                                      next(v for v in range(1, 500) if v not in set(values))))(
            rng.sample(range(1, 400), n)) for n in SIZES],
        ["1 <= number of nodes <= 2000", "the tree is a valid BST", "value is not already present"],
        ["Descend as if searching for the value.",
         "Attach a new leaf where the search falls off the tree.",
         "The inorder traversal afterwards is the sorted set of all values."],
        notes=[TREE_NOTE],
    ))

    add(P(
        "bst-floor-value", "BST Floor", "medium", T, TB,
        "The tree is a binary search tree. Print the largest value that is less than or equal to "
        "`target`, or `-1` if none exists.",
        [p_tree("bst", "level-order tokens of a BST"), p_int("target")], OUT_INT,
        lambda bst, target: _bst_floor(build_tree(bst), target),
        [(["8", "4", "12", "2", "6", "10", "14"], 11), (["5"], 3)],
        lambda rng: [(lambda values: (bst_tokens(values), rng.randint(0, 420)))(
            rng.sample(range(1, 400), n)) for n in SIZES],
        ["1 <= number of nodes <= 2000", "the tree is a valid BST", "node values are positive"],
        ["Descend the tree; when the node's value is at most the target, record it and go right.",
         "Otherwise go left.",
         "The last recorded value is the floor.",
         "Print -1 when nothing was ever recorded."],
        notes=[TREE_NOTE],
        explanations=["10 is the largest value at or below 11.", "Nothing is at or below 3."],
    ))

    add(P(
        "bst-ceil-value", "BST Ceiling", "medium", T, TB,
        "The tree is a binary search tree. Print the smallest value that is greater than or equal to "
        "`target`, or `-1` if none exists.",
        [p_tree("bst", "level-order tokens of a BST"), p_int("target")], OUT_INT,
        lambda bst, target: _bst_ceil(build_tree(bst), target),
        [(["8", "4", "12", "2", "6", "10", "14"], 11), (["5"], 7)],
        lambda rng: [(lambda values: (bst_tokens(values), rng.randint(0, 420)))(
            rng.sample(range(1, 400), n)) for n in SIZES],
        ["1 <= number of nodes <= 2000", "the tree is a valid BST", "node values are positive"],
        ["Mirror the floor logic: record the value when it is at least the target, then go left.",
         "Otherwise go right.",
         "Print -1 when no value qualifies."],
        notes=[TREE_NOTE],
        explanations=["12 is the smallest value at or above 11.", "Nothing is at or above 7."],
    ))

    add(P(
        "same-tree-check", "Same Tree", "easy", T, TB,
        "Print `YES` if the two trees have identical structure and values, else `NO`.",
        [p_tree("a", "level-order tokens of the first tree"),
         p_tree("b", "level-order tokens of the second tree")], OUT_BOOL,
        lambda a, b: _same_tree(build_tree(a), build_tree(b)),
        [(["1", "2", "3"], ["1", "2", "3"]), (["1", "2"], ["1", "null", "2"])],
        lambda rng: [(lambda tokens: (tokens, tokens if rng.random() < 0.5 else tree_tokens(rng, n)))(
            tree_tokens(rng, n)) for n in SIZES],
        ["0 <= number of nodes <= 2000"],
        ["Compare the two roots, then recurse on matching child pairs.",
         "Two empty subtrees match; one empty and one not does not.",
         "Structure matters as much as the values."],
        notes=[TREE_NOTE],
        explanations=["Identical trees.", "The 2 hangs on opposite sides."],
    ))

    add(P(
        "sum-of-left-leaves", "Sum Of Left Leaves", "easy", T, TB,
        "Print the sum of every leaf that is the left child of its parent. Print `0` if there are none.",
        [p_tree()], OUT_INT, lambda tree: _sum_left_leaves(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["1"],)], g_tree(),
        ["0 <= number of nodes <= 2000", "-10^6 <= node value <= 10^6"],
        ["Pass down whether the current node is a left child.",
         "Add the value only when the node is both a leaf and a left child.",
         "The root is never a left child."],
        notes=[TREE_NOTE],
        explanations=["9 and 15 are left leaves, summing to 24.", "The root is not a left child."],
    ))

    add(P(
        "min-depth-of-tree", "Minimum Depth Of Tree", "easy", T, TB,
        "Print the number of nodes on the shortest root-to-leaf path. Print `0` for an empty tree.",
        [p_tree()], OUT_INT, lambda tree: _min_depth(build_tree(tree)),
        [(["3", "9", "20", "null", "null", "15", "7"],), (["1", "2"],)], g_tree(),
        ["0 <= number of nodes <= 2000"],
        ["A node with only one child cannot use the missing side as a path.",
         "So take the minimum only over children that exist.",
         "BFS finds the shallowest leaf without exploring the whole tree."],
        notes=[TREE_NOTE],
        explanations=["The path 3-9 has 2 nodes.", "The only leaf is 2, at depth 2."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _inorder(node):
    result = []
    stack: list = []
    current = node
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result


def _preorder(node):
    if node is None:
        return []
    result = []
    stack = [node]
    while stack:
        current = stack.pop()
        result.append(current.val)
        if current.right:
            stack.append(current.right)
        if current.left:
            stack.append(current.left)
    return result


def _postorder(node):
    if node is None:
        return []
    result = []
    stack = [node]
    while stack:
        current = stack.pop()
        result.append(current.val)
        if current.left:
            stack.append(current.left)
        if current.right:
            stack.append(current.right)
    return list(reversed(result))


def _level_order(node):
    if node is None:
        return []
    result = []
    queue = deque([node])
    while queue:
        current = queue.popleft()
        result.append(current.val)
        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)
    return result


def _height(node):
    if node is None:
        return 0
    return 1 + max(_height(node.left), _height(node.right))


def _count(node):
    if node is None:
        return 0
    return 1 + _count(node.left) + _count(node.right)


def _count_leaves(node):
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    return _count_leaves(node.left) + _count_leaves(node.right)


def _sum(node):
    if node is None:
        return 0
    return node.val + _sum(node.left) + _sum(node.right)


def _max_value(node):
    if node is None:
        return -1_000_000_000
    return max(node.val, _max_value(node.left), _max_value(node.right))


def _diameter(node):
    best = 0

    def depth(current):
        nonlocal best
        if current is None:
            return 0
        left = depth(current.left)
        right = depth(current.right)
        best = max(best, left + right)
        return 1 + max(left, right)

    depth(node)
    return best


def _is_balanced(node):
    def check(current):
        if current is None:
            return 0
        left = check(current.left)
        if left < 0:
            return -1
        right = check(current.right)
        if right < 0:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return check(node) >= 0


def _is_symmetric(node):
    def mirror(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return node is None or mirror(node.left, node.right)


def _invert(node):
    if node is None:
        return None
    node.left, node.right = _invert(node.right), _invert(node.left)
    return node


def _side_view(node, left=True):
    if node is None:
        return []
    result = []
    queue = deque([node])
    while queue:
        size = len(queue)
        level = []
        for _ in range(size):
            current = queue.popleft()
            level.append(current.val)
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)
        result.append(level[0] if left else level[-1])
    return result


def _zigzag(node):
    if node is None:
        return []
    result = []
    queue = deque([node])
    reverse = False
    while queue:
        size = len(queue)
        level = []
        for _ in range(size):
            current = queue.popleft()
            level.append(current.val)
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)
        result.extend(reversed(level) if reverse else level)
        reverse = not reverse
    return result


def _has_path_sum(node, target):
    if node is None:
        return False
    if node.left is None and node.right is None:
        return node.val == target
    remaining = target - node.val
    return _has_path_sum(node.left, remaining) or _has_path_sum(node.right, remaining)


def _max_root_leaf(node):
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return node.val
    if node.left is None:
        return node.val + _max_root_leaf(node.right)
    if node.right is None:
        return node.val + _max_root_leaf(node.left)
    return node.val + max(_max_root_leaf(node.left), _max_root_leaf(node.right))


def _count_at_depth(node, depth):
    if node is None:
        return 0
    if depth == 0:
        return 1
    return _count_at_depth(node.left, depth - 1) + _count_at_depth(node.right, depth - 1)


def _lca_bst(node, p, q):
    low, high = min(p, q), max(p, q)
    current = node
    while current:
        if current.val > high:
            current = current.left
        elif current.val < low:
            current = current.right
        else:
            return current.val
    return -1


def _lca(node, p, q):
    def helper(current):
        if current is None:
            return None
        if current.val in (p, q):
            return current
        left = helper(current.left)
        right = helper(current.right)
        if left and right:
            return current
        return left or right

    found = helper(node)
    return found.val if found else -1


def _distinct_tree(rng, n):
    values = rng.sample(range(1, 500), n)
    tokens = tree_tokens(rng, n)
    slot = 0
    output = []
    for token in tokens:
        if token == "null":
            output.append("null")
        else:
            output.append(str(values[slot % len(values)]))
            slot += 1
    return output


def _is_bst(node):
    def check(current, low, high):
        if current is None:
            return True
        if not (low < current.val < high):
            return False
        return check(current.left, low, current.val) and check(current.right, current.val, high)

    return check(node, float("-inf"), float("inf"))


def _bst_contains(node, target):
    current = node
    while current:
        if current.val == target:
            return True
        current = current.left if target < current.val else current.right
    return False


def _bst_floor(node, target):
    best = -1
    current = node
    while current:
        if current.val <= target:
            best = current.val
            current = current.right
        else:
            current = current.left
    return best


def _bst_ceil(node, target):
    best = -1
    current = node
    while current:
        if current.val >= target:
            best = current.val
            current = current.left
        else:
            current = current.right
    return best


def _same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and _same_tree(a.left, b.left) and _same_tree(a.right, b.right)


def _sum_left_leaves(node):
    def helper(current, is_left):
        if current is None:
            return 0
        if current.left is None and current.right is None:
            return current.val if is_left else 0
        return helper(current.left, True) + helper(current.right, False)

    return helper(node, False)


def _min_depth(node):
    if node is None:
        return 0
    if node.left is None:
        return 1 + _min_depth(node.right)
    if node.right is None:
        return 1 + _min_depth(node.left)
    return 1 + min(_min_depth(node.left), _min_depth(node.right))
