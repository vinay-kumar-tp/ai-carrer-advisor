"""Heaps, priority queues and top-K selection."""

from __future__ import annotations

import heapq
import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR_LIST,
    P,
    Param,
    ints,
    p_int,
    p_nums,
    words,
)

T = ["Heap"]
TK = ["Top-K Elements"]
TH = ["Two Heaps"]
KW = ["K-way Merge"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)


def g_nums_k(lo=-60, hi=60, sizes=SIZES):
    def gen(rng: random.Random):
        return [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, lo, hi)) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "k-largest-elements-sorted", "K Largest Elements", "medium", T + ["Arrays"], TK,
        "Print the `k` largest elements of `nums` in descending order, space separated. Duplicates count "
        "separately.",
        [p_nums(), p_int("k", "how many to report")], OUT_INT_LIST,
        lambda nums, k: sorted(nums, reverse=True)[:k],
        [([3, 2, 1, 5, 6, 4], 3), ([7], 1)], g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["A min-heap of size k keeps only the current best candidates in O(n log k).",
         "Push each element, then pop when the heap grows past k.",
         "Sort the heap contents descending at the end.",
         "Sorting the whole array is O(n log n) and also acceptable."],
        explanations=["6,5,4.", "The single element."],
    ))

    add(P(
        "k-smallest-elements-sorted", "K Smallest Elements", "medium", T + ["Arrays"], TK,
        "Print the `k` smallest elements of `nums` in ascending order, space separated.",
        [p_nums(), p_int("k", "how many to report")], OUT_INT_LIST,
        lambda nums, k: sorted(nums)[:k],
        [([3, 2, 1, 5, 6, 4], 2), ([7], 1)], g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Use a max-heap of size k, or negate values in a min-heap.",
         "Sort the survivors ascending before printing.",
         "Quickselect gives O(n) on average."],
    ))

    add(P(
        "kth-largest-in-stream", "Kth Largest In Stream", "medium", T + ["Arrays"], TK,
        "Process `nums` left to right. After each element, print the `k`-th largest value seen so far, or "
        "`-1` if fewer than `k` values have arrived. Print the answers space separated.",
        [p_nums(), p_int("k", "the rank to report")], OUT_INT_LIST,
        lambda nums, k: _kth_largest_stream(nums, k),
        [([4, 5, 8, 2], 3), ([1, 2], 1)], g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Keep a min-heap holding the k largest values seen so far.",
         "Push each arrival, then pop while the heap exceeds size k.",
         "The heap root is then the k-th largest.",
         "Report -1 until the heap first reaches size k."],
        explanations=["-1,-1,4,4.", "1,2."],
        brute=lambda nums, k: [sorted(nums[:i + 1], reverse=True)[k - 1] if i + 1 >= k else -1
                               for i in range(len(nums))],
    ))

    add(P(
        "running-median-of-stream", "Running Median", "hard", T + ["Arrays"], TH,
        "Process `nums` left to right. After each element, print the median of everything seen so far, "
        "rounded down to an integer when the count is even (use floor division of the two middle values' "
        "sum by 2). Print the answers space separated.",
        [p_nums()], OUT_INT_LIST, lambda nums: _running_median(nums),
        [([2, 1, 5, 7, 2, 0, 5],), ([4],)],
        lambda rng: [(ints(rng, n, -30, 30),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Keep a max-heap for the lower half and a min-heap for the upper half.",
         "Rebalance after each insert so the sizes differ by at most one.",
         "The median is the larger heap's root, or the floor of the average of both roots.",
         "Each step is O(log n), versus O(n log n) for re-sorting every time."],
        explanations=["2,1,2,3,2,2,2.", "The single value."],
        brute=lambda nums: [_median_floor(sorted(nums[:i + 1])) for i in range(len(nums))],
    ))

    add(P(
        "merge-k-sorted-lists-flat", "Merge K Sorted Arrays", "medium", T + ["Arrays"], KW,
        "The array `nums` is the concatenation of `k` sorted blocks, each of length `size`. Merge them all "
        "and print the fully sorted result.",
        [Param("nums", INT_LIST, "k sorted blocks laid end to end"), p_int("size", "length of each block")],
        OUT_INT_LIST, lambda nums, size: sorted(nums),
        [([1, 4, 5, 1, 3, 4], 3), ([2, 1], 1)],
        lambda rng: [(lambda size, k: ([v for _ in range(k) for v in sorted(ints(rng, size, -30, 30))], size))(
            size, k) for size, k in ((1, 1), (1, 3), (2, 2), (3, 4), (5, 6), (8, 12), (12, 20))],
        ["1 <= size <= 2000", "the length of nums is a multiple of size",
         "each block is sorted in non-decreasing order"],
        ["A min-heap holding one candidate per block merges in O(n log k).",
         "Pop the smallest, then push the next element from that same block.",
         "Merging pairs of blocks repeatedly is the divide-and-conquer alternative.",
         "Sorting everything is O(n log n) and passes here."],
        explanations=["1,1,3,4,4,5.", "1,2."],
    ))

    add(P(
        "smallest-range-covering-blocks", "Smallest Element After K Removals", "medium",
        T + ["Arrays"], TK,
        "Remove the `k` largest elements of `nums`, then print the largest of what remains. Print "
        "`-1000000000` if nothing remains.",
        [p_nums(), p_int("k", "how many largest elements to remove")], OUT_INT,
        lambda nums, k: sorted(nums, reverse=True)[k] if k < len(nums) else -1_000_000_000,
        [([5, 1, 3, 9], 2), ([4], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(0, len(arr))))(ints(rng, n, -60, 60)) for n in SIZES],
        ["1 <= n <= 2000", "0 <= k <= n", "-10^6 <= nums[i] <= 10^6"],
        ["Sorting descending makes the answer the element at index k.",
         "A heap of size k+1 also finds it without a full sort.",
         "Watch the case where k equals n and nothing is left."],
        explanations=["Removing 9 and 5 leaves 3 as the largest.", "Nothing remains."],
    ))

    add(P(
        "top-k-frequent-words-heap", "Top K Frequent Words By Heap", "medium",
        T + ["Strings", "Hashing"], TK,
        "Print the `k` most frequent words, one per line, ordered by descending frequency then "
        "alphabetically.",
        [Param("wordsList", "str[]", "the words"), p_int("k", "how many to report")], OUT_STR_LIST,
        lambda wordsList, k: _top_k_words(wordsList, k),
        [(["a", "b", "a", "c", "b", "a"], 2), (["x"], 1)],
        lambda rng: [(lambda ws: (ws, rng.randint(1, len(set(ws)))))(words(rng, count, 1, 3, "abc"))
                     for count in (1, 2, 5, 12, 35, 90, 200)],
        ["1 <= number of words <= 1000", "1 <= k <= number of distinct words"],
        ["Count the words, then push (count, word) pairs into a heap of size k.",
         "The comparison must invert frequency but not the word, which is why a custom key is needed.",
         "Sorting the distinct words by (-count, word) is the simplest correct approach."],
        explanations=["a appears 3 times, b twice.", "The only word."],
    ))

    add(P(
        "k-closest-to-target", "K Closest Values", "medium", T + ["Arrays", "Two Pointers"], TK,
        "Print the `k` values of `nums` closest to `target`, ordered by increasing distance and breaking "
        "ties by the smaller value. Print them space separated.",
        [p_nums(), p_int("target"), p_int("k", "how many to report")], OUT_INT_LIST,
        lambda nums, target, k: _k_closest(nums, target, k),
        [([1, 2, 3, 4, 5], 3, 3), ([7], 1, 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(-60, 60), rng.randint(1, len(arr))))(
            ints(rng, n, -60, 60)) for n in SIZES],
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["Sort by the key (abs(value - target), value) and take the first k.",
         "A max-heap of size k on the same key avoids a full sort.",
         "For a sorted input, a two-pointer sweep outwards from the target is O(k)."],
        explanations=["3,2,4 by increasing distance.", "The only value."],
    ))

    add(P(
        "min-cost-to-connect-ropes", "Minimum Cost To Connect Ropes", "medium", T, ["Greedy"],
        "Repeatedly join two ropes, paying the sum of their lengths. Print the minimum total cost to join "
        "every rope into one. Print `0` if there is only one rope.",
        [Param("lengths", INT_LIST, "positive rope lengths")], OUT_INT,
        lambda lengths: _connect_ropes(lengths),
        [([4, 3, 2, 6],), ([5],)],
        lambda rng: [(ints(rng, n, 1, 40),) for n in SIZES],
        ["1 <= n <= 2000", "1 <= lengths[i] <= 10^4",
         "the answer fits in a 64-bit signed integer"],
        ["Always join the two shortest ropes available.",
         "A min-heap gives you those in O(log n) per step.",
         "Push the combined rope back and repeat until one remains.",
         "Joining longer ropes early makes them pay again in later joins, which is why greedy works."],
        explanations=["2+3=5, 4+5=9, 6+9=15 totalling 29.", "Nothing to join."],
    ))

    add(P(
        "kth-smallest-in-sorted-matrix", "Kth Smallest In Sorted Matrix", "hard",
        T + ["Matrix", "Binary Search"], KW,
        "Every row of the matrix `mat` is sorted ascending. Print the `k`-th smallest value across the "
        "whole matrix.",
        [Param("mat", "int[][]", "each row is sorted ascending"), p_int("k", "1-based rank")], OUT_INT,
        lambda mat, k: sorted(value for row in mat for value in row)[k - 1],
        [([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8), ([[3]], 1)],
        lambda rng: [(lambda r, c: ([sorted(ints(rng, c, -40, 40)) for _ in range(r)],
                                    rng.randint(1, r * c)))(r, c)
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (5, 4), (8, 7), (14, 12))],
        ["1 <= r, c <= 200", "1 <= k <= r * c", "each row is sorted ascending"],
        ["A min-heap seeded with each row's first element merges the rows in O(k log r).",
         "Pop k times, pushing the next element from the row you popped from.",
         "Binary searching the value range and counting elements <= mid is another route.",
         "Flattening and sorting is O(rc log rc) and passes here."],
        explanations=["The 8th smallest is 13.", "The only value."],
    ))

    add(P(
        "reorganize-string-max-gap", "Most Frequent Character Count", "easy",
        T + ["Strings", "Hashing"], TK,
        "Print the number of occurrences of the most frequent character of `s`.",
        [Param("s", "str", "lowercase letters")], OUT_INT,
        lambda s: max(s.count(ch) for ch in set(s)),
        [("aabbbcc",), ("z",)],
        lambda rng: [("".join(rng.choice("abc") for _ in range(n)),) for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= |s| <= 2000", "s contains lowercase English letters only"],
        ["Count characters into a 26-slot array.",
         "The answer is the largest count.",
         "This is the value a max-heap would surface first when scheduling characters apart."],
        explanations=["b appears 3 times.", "One character."],
    ))

    add(P(
        "heapify-array-to-min-heap", "Build Min Heap", "medium", T, TK,
        "Build a binary min-heap from `nums` using the standard bottom-up sift-down procedure and print "
        "the resulting array layout.",
        [p_nums()], OUT_INT_LIST, lambda nums: _build_min_heap(nums),
        [([3, 1, 2],), ([5],)],
        lambda rng: [(ints(rng, n, -40, 40),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Start at the last internal node, index n/2 - 1, and sift down towards the front.",
         "Sifting down swaps a node with its smaller child until the heap property holds.",
         "Bottom-up heapify is O(n), better than n separate insertions at O(n log n).",
         "The exact layout depends on the procedure, so follow the standard one."],
        explanations=["1,3,2.", "A single element is already a heap."],
    ))

    add(P(
        "heap-sort-array", "Heap Sort", "medium", T + ["Sorting & Searching"], TK,
        "Sort `nums` ascending using a heap and print the result.",
        [p_nums()], OUT_INT_LIST, lambda nums: _heap_sort(nums),
        [([4, 1, 3, 2],), ([9],)],
        lambda rng: [(ints(rng, n, -60, 60),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Build a max-heap, then repeatedly swap the root to the end and shrink the heap.",
         "Sift down after each swap to restore the heap property.",
         "Heap sort is in-place and always O(n log n), though not stable."],
        brute=sorted,
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _kth_largest_stream(nums, k):
    heap: list[int] = []
    answers = []
    for value in nums:
        heapq.heappush(heap, value)
        if len(heap) > k:
            heapq.heappop(heap)
        answers.append(heap[0] if len(heap) == k else -1)
    return answers


def _median_floor(sorted_values):
    count = len(sorted_values)
    middle = count // 2
    if count % 2:
        return sorted_values[middle]
    return (sorted_values[middle - 1] + sorted_values[middle]) // 2


def _running_median(nums):
    lower: list[int] = []   # max-heap via negation
    upper: list[int] = []   # min-heap
    answers = []
    for value in nums:
        if lower and value <= -lower[0]:
            heapq.heappush(lower, -value)
        else:
            heapq.heappush(upper, value)
        if len(lower) > len(upper) + 1:
            heapq.heappush(upper, -heapq.heappop(lower))
        elif len(upper) > len(lower):
            heapq.heappush(lower, -heapq.heappop(upper))
        if len(lower) > len(upper):
            answers.append(-lower[0])
        else:
            answers.append((-lower[0] + upper[0]) // 2)
    return answers


def _top_k_words(wordsList, k):
    counts: dict[str, int] = {}
    for item in wordsList:
        counts[item] = counts.get(item, 0) + 1
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [item for item, _ in ordered[:k]]


def _k_closest(nums, target, k):
    return sorted(nums, key=lambda value: (abs(value - target), value))[:k]


def _connect_ropes(lengths):
    if len(lengths) == 1:
        return 0
    heap = list(lengths)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        first = heapq.heappop(heap)
        second = heapq.heappop(heap)
        combined = first + second
        total += combined
        heapq.heappush(heap, combined)
    return total


def _sift_down_min(values, start, size):
    root = start
    while True:
        child = 2 * root + 1
        if child >= size:
            break
        if child + 1 < size and values[child + 1] < values[child]:
            child += 1
        if values[child] < values[root]:
            values[root], values[child] = values[child], values[root]
            root = child
        else:
            break


def _build_min_heap(nums):
    values = list(nums)
    for start in range(len(values) // 2 - 1, -1, -1):
        _sift_down_min(values, start, len(values))
    return values


def _sift_down_max(values, start, size):
    root = start
    while True:
        child = 2 * root + 1
        if child >= size:
            break
        if child + 1 < size and values[child + 1] > values[child]:
            child += 1
        if values[child] > values[root]:
            values[root], values[child] = values[child], values[root]
            root = child
        else:
            break


def _heap_sort(nums):
    values = list(nums)
    size = len(values)
    for start in range(size // 2 - 1, -1, -1):
        _sift_down_max(values, start, size)
    for end in range(size - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        _sift_down_max(values, 0, end)
    return values
