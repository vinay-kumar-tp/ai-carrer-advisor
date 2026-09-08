"""Linked list problems.

A list is given as its values in order, so you can solve these with an array or
by building real nodes — the logic being tested is identical.
"""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    Param,
    ints,
    p_int,
    sorted_ints,
)

T = ["Linked List"]
LL = ["Linked List"]
REV = ["Linked List / Reversal"]
FS = ["Fast & Slow Pointers"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)

NODE_NOTE = ("The list is supplied as its values from head to tail. Build real nodes if you prefer — the "
             "traversal logic is the same.")


def p_list(name="values", desc="the node values from head to tail"):
    return Param(name, INT_LIST, desc)


def g_list(lo=-50, hi=50, sizes=SIZES):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "reverse-linked-list", "Reverse Linked List", "easy", T, REV,
        "Print the values of the list after reversing it.",
        [p_list()], OUT_INT_LIST, lambda values: list(reversed(values)),
        [([1, 2, 3, 4],), ([7],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Walk the list keeping previous, current and next pointers.",
         "Point current at previous, then advance both by one node.",
         "The new head is the last node you visited.",
         "Losing the next pointer before you reassign it is the classic bug."],
        notes=[NODE_NOTE],
        explanations=["4,3,2,1.", "A single node is unchanged."],
    ))

    add(P(
        "middle-of-linked-list", "Middle Of Linked List", "easy", T, FS,
        "Print the value of the middle node. For an even length, print the second of the two middle nodes.",
        [p_list()], OUT_INT, lambda values: values[len(values) // 2],
        [([1, 2, 3, 4, 5],), ([1, 2],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Advance a slow pointer one node and a fast pointer two nodes per step.",
         "When fast reaches the end, slow is at the middle.",
         "This convention lands on the second middle node for even lengths."],
        notes=[NODE_NOTE],
        explanations=["3 is the middle of five nodes.", "2 is the second of the two middle nodes."],
    ))

    add(P(
        "nth-node-from-end", "Nth Node From End", "easy", T, FS,
        "Print the value of the `k`-th node counting from the end, where `k = 1` is the last node.",
        [p_list(), p_int("k", "position from the end")], OUT_INT,
        lambda values, k: values[len(values) - k],
        [([1, 2, 3, 4, 5], 2), ([9], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, -50, 50)) for n in SIZES],
        ["1 <= k <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Advance a lead pointer k nodes ahead, then move both until the lead falls off the end.",
         "The trailing pointer then sits on the answer.",
         "This needs only one pass and no length computation."],
        notes=[NODE_NOTE],
        explanations=["The 2nd from the end is 4.", "The only node."],
    ))

    add(P(
        "delete-nth-from-end", "Delete Nth Node From End", "medium", T, FS,
        "Delete the `k`-th node from the end and print the remaining values. Print an empty line if the "
        "list becomes empty.",
        [p_list(), p_int("k", "position from the end")], OUT_INT_LIST,
        lambda values, k: values[:len(values) - k] + values[len(values) - k + 1:],
        [([1, 2, 3, 4, 5], 2), ([1], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, -50, 50)) for n in SIZES],
        ["1 <= k <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Use the two-pointer gap trick to reach the node before the target.",
         "A dummy node in front of the head removes the special case of deleting the head.",
         "Relink the predecessor to skip the target node."],
        notes=[NODE_NOTE],
        explanations=["Removing 4 leaves 1,2,3,5.", "The list becomes empty."],
    ))

    add(P(
        "detect-cycle-in-list", "Detect Cycle", "medium", T, FS,
        "The list has `n` nodes; `pos` is the 0-based index the tail links back to, or `-1` if the list "
        "ends normally. Print `YES` if the list contains a cycle, else `NO`.",
        [p_int("n", "number of nodes"), p_int("pos", "index the tail points to, or -1")], OUT_BOOL,
        lambda n, pos: 0 <= pos < n,
        [(4, 1), (3, -1)],
        lambda rng: [(lambda n: (n, rng.choice([-1, rng.randrange(n)])))(rng.randint(1, 40)) for _ in range(8)],
        ["1 <= n <= 2000", "-1 <= pos < n"],
        ["Floyd's tortoise and hare moves one pointer by 1 and the other by 2.",
         "They meet inside the cycle if one exists; the fast pointer reaches the end otherwise.",
         "This uses O(1) extra space, unlike a visited set.",
         "Here the structure is described directly, so the answer follows from whether pos is a valid index."],
        explanations=["The tail links back to index 1.", "The list terminates."],
    ))

    add(P(
        "cycle-length", "Cycle Length", "medium", T, FS,
        "The list has `n` nodes; the tail links back to index `pos`, or `-1` for no cycle. Print the "
        "number of nodes in the cycle, or `0` if there is none.",
        [p_int("n", "number of nodes"), p_int("pos", "index the tail points to, or -1")], OUT_INT,
        lambda n, pos: n - pos if 0 <= pos < n else 0,
        [(5, 2), (3, -1)],
        lambda rng: [(lambda n: (n, rng.choice([-1, rng.randrange(n)])))(rng.randint(1, 40)) for _ in range(8)],
        ["1 <= n <= 2000", "-1 <= pos < n"],
        ["After the tortoise and hare meet, keep one pointer fixed and walk the other until it returns.",
         "The number of steps taken is the cycle length.",
         "With the structure given directly, the cycle spans indices pos..n-1."],
        explanations=["Nodes 2,3,4 form the cycle.", "There is no cycle."],
    ))

    add(P(
        "merge-two-sorted-lists", "Merge Two Sorted Lists", "easy", T, LL,
        "Both lists are sorted ascending. Print the values of the merged sorted list.",
        [Param("a", INT_LIST, "first list, sorted"), Param("b", INT_LIST, "second list, sorted")],
        OUT_INT_LIST, lambda a, b: _merge(a, b),
        [([1, 3, 5], [2, 4]), ([1], [1])],
        lambda rng: [(sorted_ints(rng, n, -40, 40), sorted_ints(rng, m, -40, 40))
                     for n, m in ((1, 1), (1, 3), (3, 1), (4, 4), (9, 6), (25, 30), (90, 70))],
        ["1 <= n, m <= 2000", "both lists are sorted in non-decreasing order"],
        ["Walk both lists, always taking the smaller head.",
         "A dummy head node keeps the linking code uniform.",
         "Append the remaining nodes once one list is exhausted."],
        notes=[NODE_NOTE],
    ))

    add(P(
        "remove-duplicates-sorted-list", "Remove Duplicates From Sorted List", "easy", T, LL,
        "The list is sorted. Remove duplicate values so each appears once and print the remaining values.",
        [Param("values", INT_LIST, "sorted node values")], OUT_INT_LIST,
        lambda values: sorted(set(values)),
        [([1, 1, 2, 3, 3],), ([2],)],
        lambda rng: [(sorted(ints(rng, n, 1, max(2, n // 2))),) for n in SIZES],
        ["1 <= n <= 2000", "the values are sorted in non-decreasing order"],
        ["Because the list is sorted, duplicates are adjacent.",
         "Skip a node whose value matches the previous kept node.",
         "Relink the previous node past every skipped node."],
        notes=[NODE_NOTE],
    ))

    add(P(
        "remove-all-duplicates-list", "Remove All Duplicate Values", "medium", T, LL,
        "The list is sorted. Delete every value that appears more than once and print what remains. Print "
        "an empty line if nothing survives.",
        [Param("values", INT_LIST, "sorted node values")], OUT_INT_LIST,
        lambda values: [v for v in sorted(set(values)) if values.count(v) == 1],
        [([1, 2, 3, 3, 4],), ([1, 1],)],
        lambda rng: [(sorted(ints(rng, n, 1, max(2, n // 2))),) for n in SIZES],
        ["1 <= n <= 2000", "the values are sorted in non-decreasing order"],
        ["Look ahead to detect a run of equal values.",
         "Skip the whole run, not just the extra copies.",
         "A dummy head simplifies deleting from the front."],
        notes=[NODE_NOTE],
        explanations=["3 appears twice so it goes entirely.", "Every value is duplicated."],
    ))

    add(P(
        "is-list-palindrome", "Palindrome Linked List", "easy", T, FS,
        "Print `YES` if the list's values read the same forwards and backwards, else `NO`.",
        [p_list()], OUT_BOOL, lambda values: values == values[::-1],
        [([1, 2, 2, 1],), ([1, 2],)],
        lambda rng: [(_maybe_palindrome(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Find the middle with fast and slow pointers.",
         "Reverse the second half, then compare it against the first half.",
         "That achieves O(1) extra space; copying to an array is the simpler O(n) approach."],
        notes=[NODE_NOTE],
    ))

    add(P(
        "reverse-list-in-k-groups", "Reverse Nodes In K Groups", "hard", T, REV,
        "Reverse every consecutive group of `k` nodes. A trailing group with fewer than `k` nodes is left "
        "as is. Print the resulting values.",
        [p_list(), p_int("k", "group size")], OUT_INT_LIST,
        lambda values, k: _reverse_k_groups(values, k),
        [([1, 2, 3, 4, 5], 2), ([1, 2, 3], 5)],
        lambda rng: [(ints(rng, n, -40, 40), rng.randint(1, max(1, n + 2))) for n in SIZES],
        ["1 <= n <= 2000", "1 <= k <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Count k nodes ahead before reversing so you know a full group exists.",
         "Reverse the group, then connect it to the previously reversed part.",
         "Leave the final partial group untouched.",
         "A dummy head keeps the first group's relinking simple."],
        notes=[NODE_NOTE],
        explanations=["2,1,4,3,5 — the last node has no partner.",
                      "Fewer than k nodes, so nothing is reversed."],
    ))

    add(P(
        "reverse-list-between-positions", "Reverse Sublist", "medium", T, REV,
        "Reverse the nodes from position `left` to position `right` inclusive (1-based) and print the "
        "resulting values.",
        [p_list(), p_int("left", "start position, 1-based"), p_int("right", "end position, 1-based")],
        OUT_INT_LIST, lambda values, left, right: _reverse_between(values, left, right),
        [([1, 2, 3, 4, 5], 2, 4), ([1], 1, 1)],
        lambda rng: [(lambda arr: (lambda l: (arr, l, rng.randint(l, len(arr))))(rng.randint(1, len(arr))))(
            ints(rng, n, -40, 40)) for n in SIZES],
        ["1 <= left <= right <= n <= 2000"],
        ["Walk to the node before `left`, then reverse exactly right-left+1 nodes.",
         "Reconnect the reversed segment to the nodes on both sides.",
         "A dummy head handles the case where left is 1."],
        notes=[NODE_NOTE],
        explanations=["1,4,3,2,5.", "A single node reverses to itself."],
    ))

    add(P(
        "rotate-list-right", "Rotate List", "medium", T, LL,
        "Rotate the list right by `k` positions and print the resulting values.",
        [p_list(), p_int("k", "positions to rotate")], OUT_INT_LIST,
        lambda values, k: (lambda s: values[len(values) - s:] + values[:len(values) - s])(k % len(values)),
        [([1, 2, 3, 4, 5], 2), ([1, 2], 0)],
        lambda rng: [(ints(rng, n, -40, 40), rng.randint(0, 2 * n)) for n in SIZES],
        ["1 <= n <= 2000", "0 <= k <= 10^9"],
        ["Reduce k modulo the length first.",
         "Find the new tail at position n - k, then make its successor the new head.",
         "Close the loop by linking the old tail to the old head, then break it at the new tail."],
        notes=[NODE_NOTE],
        explanations=["4,5,1,2,3.", "k is 0, so nothing moves."],
    ))

    add(P(
        "odd-even-list-reorder", "Odd Even Positions", "medium", T, LL,
        "Group the nodes at odd positions before those at even positions (positions are 1-based), keeping "
        "the relative order inside each group. Print the resulting values.",
        [p_list()], OUT_INT_LIST,
        lambda values: values[0::2] + values[1::2],
        [([1, 2, 3, 4, 5],), ([1, 2],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Maintain two chains, one for odd positions and one for even.",
         "Append alternate nodes to each, then link the odd tail to the even head.",
         "Position parity matters, not the value parity."],
        notes=[NODE_NOTE],
        explanations=["1,3,5 then 2,4.", "1 then 2."],
    ))

    add(P(
        "swap-pairs-in-list", "Swap Nodes In Pairs", "medium", T, REV,
        "Swap every two adjacent nodes and print the resulting values. A final unpaired node stays put.",
        [p_list()], OUT_INT_LIST, lambda values: _swap_pairs(values),
        [([1, 2, 3, 4],), ([1, 2, 3],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["This is the k-group reversal with k fixed at 2.",
         "Relink three pointers per swap: the predecessor and the two nodes.",
         "Stop when fewer than two nodes remain."],
        notes=[NODE_NOTE],
        explanations=["2,1,4,3.", "2,1,3 — the last node is unpaired."],
    ))

    add(P(
        "add-two-numbers-lists", "Add Two Numbers", "medium", T + ["Math"], LL,
        "Each list stores the digits of a non-negative integer in reverse order, least significant first. "
        "Print the digits of their sum in the same reverse order.",
        [Param("a", INT_LIST, "digits of the first number, least significant first"),
         Param("b", INT_LIST, "digits of the second number, least significant first")],
        OUT_INT_LIST, lambda a, b: _add_digit_lists(a, b),
        [([2, 4, 3], [5, 6, 4]), ([9], [9, 9])],
        lambda rng: [([rng.randint(0, 9) for _ in range(n)], [rng.randint(0, 9) for _ in range(m)])
                     for n, m in ((1, 1), (1, 3), (3, 1), (4, 4), (9, 6), (25, 30), (90, 70))],
        ["1 <= n, m <= 2000", "0 <= digit <= 9"],
        ["Walk both lists together adding digit by digit with a carry.",
         "The reverse ordering means you start at the least significant digit, which is exactly what you want.",
         "Emit a final node when a carry remains after both lists end."],
        notes=[NODE_NOTE],
        explanations=["342 + 465 = 807 gives 7,0,8.", "9 + 99 = 108 gives 8,0,1."],
    ))

    add(P(
        "intersection-node-of-lists", "Intersection Of Two Lists", "medium", T, FS,
        "Two lists have lengths `n` and `m` and share a common suffix of length `common`. Print the "
        "1-based position in the first list where the shared suffix begins, or `-1` if `common` is 0.",
        [p_int("n", "length of the first list"), p_int("m", "length of the second list"),
         p_int("common", "length of the shared suffix")], OUT_INT,
        lambda n, m, common: n - common + 1 if common > 0 else -1,
        [(5, 6, 3), (4, 4, 0)],
        lambda rng: [(lambda n, m: (n, m, rng.randint(0, min(n, m))))(rng.randint(1, 40), rng.randint(1, 40))
                     for _ in range(8)],
        ["1 <= n, m <= 2000", "0 <= common <= min(n, m)"],
        ["Walk both lists to measure their lengths, then advance the longer one by the difference.",
         "Move both pointers together; they meet at the first shared node.",
         "Alternatively switch each pointer to the other list's head on reaching the end — they align "
         "after n+m steps."],
        explanations=["The suffix of length 3 starts at position 3.", "The lists never merge."],
    ))

    add(P(
        "sort-linked-list-values", "Sort Linked List", "medium", T + ["Sorting & Searching"], LL,
        "Print the list's values in non-decreasing order.",
        [p_list()], OUT_INT_LIST, sorted,
        [([4, 2, 1, 3],), ([1],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Merge sort suits linked lists because it needs no random access.",
         "Split with fast and slow pointers, sort each half, then merge.",
         "That gives O(n log n) time with O(log n) recursion depth."],
        notes=[NODE_NOTE],
    ))

    add(P(
        "partition-list-around-value", "Partition List", "medium", T, LL,
        "Reorder the list so every value less than `x` comes before every value greater than or equal to "
        "`x`, preserving the relative order within each group. Print the resulting values.",
        [p_list(), p_int("x", "the partition value")], OUT_INT_LIST,
        lambda values, x: [v for v in values if v < x] + [v for v in values if v >= x],
        [([1, 4, 3, 2, 5, 2], 3), ([1], 0)],
        lambda rng: [(ints(rng, n, -20, 20), rng.randint(-20, 20)) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= values[i], x <= 10^6"],
        ["Build two separate chains with dummy heads: one for smaller values, one for the rest.",
         "Append each node to the matching chain in order.",
         "Join the two chains and terminate the second one."],
        notes=[NODE_NOTE],
        explanations=["1,2,2 then 4,3,5.", "Nothing is below 0."],
    ))

    add(P(
        "reorder-list-alternate-ends", "Reorder List", "medium", T, REV,
        "Reorder the list as first node, last node, second node, second-to-last node, and so on. Print "
        "the resulting values.",
        [p_list()], OUT_INT_LIST, lambda values: _reorder(values),
        [([1, 2, 3, 4],), ([1, 2, 3],)], g_list(),
        ["1 <= n <= 2000", "-10^6 <= values[i] <= 10^6"],
        ["Find the middle, reverse the second half, then interleave the two halves.",
         "Each of those three steps is a standard linked-list routine.",
         "Terminate the merged list properly so it does not loop."],
        notes=[NODE_NOTE],
        explanations=["1,4,2,3.", "1,3,2."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _merge(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def _maybe_palindrome(rng, n):
    if rng.random() < 0.45:
        half = ints(rng, (n + 1) // 2, 1, 5)
        return half + half[::-1][n % 2:]
    return ints(rng, n, 1, 5)


def _reverse_k_groups(values, k):
    result = []
    for start in range(0, len(values), k):
        block = values[start:start + k]
        result.extend(reversed(block) if len(block) == k else block)
    return result


def _reverse_between(values, left, right):
    result = list(values)
    result[left - 1:right] = reversed(result[left - 1:right])
    return result


def _swap_pairs(values):
    result = list(values)
    for index in range(0, len(result) - 1, 2):
        result[index], result[index + 1] = result[index + 1], result[index]
    return result


def _add_digit_lists(a, b):
    result = []
    carry = 0
    for index in range(max(len(a), len(b))):
        total = carry
        if index < len(a):
            total += a[index]
        if index < len(b):
            total += b[index]
        result.append(total % 10)
        carry = total // 10
    if carry:
        result.append(carry)
    return result


def _reorder(values):
    result = []
    left, right = 0, len(values) - 1
    while left <= right:
        result.append(values[left])
        if left != right:
            result.append(values[right])
        left += 1
        right -= 1
    return result
