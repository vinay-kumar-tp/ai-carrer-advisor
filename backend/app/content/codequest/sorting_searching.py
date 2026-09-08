"""Sorting algorithms and comparison-based ordering problems."""

from __future__ import annotations

import random
from functools import cmp_to_key

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR,
    OUT_STR_LIST,
    P,
    PAIR_LIST,
    Param,
    ints,
    p_int,
    p_nums,
    words,
)

T = ["Sorting & Searching"]
S = ["Sorting"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)


def g_nums(lo=-60, hi=60, sizes=SIZES):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "sort-array-ascending", "Sort Array", "easy", T + ["Arrays"], S,
        "Sort `nums` in non-decreasing order and print it.",
        [p_nums()], OUT_INT_LIST, sorted,
        [([3, 1, 2],), ([5],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Any O(n log n) sort works.",
         "Merge sort and heap sort guarantee the bound; quicksort averages it.",
         "Most languages ship a well-tuned sort in the standard library."],
    ))

    add(P(
        "sort-array-descending", "Sort Array Descending", "easy", T + ["Arrays"], S,
        "Sort `nums` in non-increasing order and print it.",
        [p_nums()], OUT_INT_LIST, lambda nums: sorted(nums, reverse=True),
        [([3, 1, 2],), ([5],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sort ascending and reverse, or pass a descending comparator.",
         "Reversing after sorting is O(n) and simplest.",
         "Duplicates may appear in any order since they are indistinguishable."],
    ))

    add(P(
        "bubble-sort-swap-count", "Bubble Sort Swap Count", "easy", T + ["Arrays"], S,
        "Print how many adjacent swaps a standard bubble sort performs while sorting `nums` ascending.",
        [p_nums()], OUT_INT, lambda nums: _bubble_swaps(nums),
        [([3, 1, 2],), ([1, 2],)], g_nums(-30, 30),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Simulate the passes, incrementing a counter on every swap.",
         "The total equals the number of inversions in the array.",
         "An already-sorted array needs zero swaps."],
        explanations=["Swapping (3,1) then (3,2) takes 2 swaps.", "Already sorted."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                               if nums[i] > nums[j]),
    ))

    add(P(
        "selection-sort-swap-count", "Selection Sort Swap Count", "easy", T + ["Arrays"], S,
        "Print how many swaps a standard selection sort performs on `nums`, where each pass swaps the "
        "minimum of the unsorted suffix into place and a swap is skipped when the element is already "
        "in position.",
        [p_nums()], OUT_INT, lambda nums: _selection_swaps(nums),
        [([3, 1, 2],), ([1, 2, 3],)], g_nums(-30, 30),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["For each index, locate the minimum of the remaining suffix.",
         "Count a swap only when that minimum is not already at the current index.",
         "Selection sort performs at most n-1 swaps."],
        explanations=["Two swaps place 1 and 2.", "No swaps are needed."],
    ))

    add(P(
        "insertion-sort-shift-count", "Insertion Sort Shift Count", "easy", T + ["Arrays"], S,
        "Print the total number of element shifts a standard insertion sort performs on `nums`.",
        [p_nums()], OUT_INT, lambda nums: _insertion_shifts(nums),
        [([3, 1, 2],), ([1, 2],)], g_nums(-30, 30),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Each element moves left past every larger element before it.",
         "Count one shift per position moved.",
         "The total equals the inversion count, matching bubble sort's swap count."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                               if nums[i] > nums[j]),
    ))

    add(P(
        "merge-sort-array", "Merge Sort", "medium", T + ["Arrays", "Recursion & D&C"],
        ["Recursion & D&C"],
        "Sort `nums` ascending using a divide-and-conquer approach and print the result.",
        [p_nums()], OUT_INT_LIST, lambda nums: _merge_sort(nums),
        [([5, 2, 4, 1],), ([3],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Split the array in half, sort each half recursively, then merge.",
         "The merge step walks both halves with two pointers.",
         "Merge sort is stable and always O(n log n), unlike quicksort's worst case.",
         "A single element is already sorted, which is the base case."],
        brute=sorted,
    ))

    add(P(
        "quick-sort-array", "Quick Sort", "medium", T + ["Arrays", "Recursion & D&C"],
        ["Recursion & D&C"],
        "Sort `nums` ascending using a partition-based approach and print the result.",
        [p_nums()], OUT_INT_LIST, lambda nums: _quick_sort(nums),
        [([5, 2, 4, 1],), ([2, 2],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Pick a pivot and partition the array into smaller, equal and larger parts.",
         "Recurse on the smaller and larger parts.",
         "A poorly chosen pivot degrades to O(n^2); random or median-of-three pivots avoid that.",
         "Handle duplicates by grouping equal elements with the pivot."],
        brute=sorted,
    ))

    add(P(
        "count-sort-small-range", "Counting Sort", "easy", T + ["Arrays"], S,
        "The values of `nums` all lie in `0..1000`. Sort the array ascending without comparisons and "
        "print the result.",
        [Param("nums", INT_LIST, "values in 0..1000")], OUT_INT_LIST,
        lambda nums: _counting_sort(nums),
        [([3, 1, 3, 0],), ([7],)],
        lambda rng: [(ints(rng, n, 0, 1000),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= nums[i] <= 1000"],
        ["Tally how many times each value occurs in an array of size 1001.",
         "Then emit each value that many times in ascending order.",
         "This runs in O(n + range), beating comparison sorts for a small range."],
        brute=sorted,
    ))

    add(P(
        "sort-by-frequency", "Sort By Frequency", "medium", T + ["Arrays", "Hashing"], S,
        "Sort `nums` by descending frequency, breaking ties by ascending value, and print the result "
        "with every occurrence included.",
        [p_nums()], OUT_INT_LIST, lambda nums: _sort_by_frequency(nums),
        [([1, 1, 2, 2, 2, 3],), ([4, 5],)],
        lambda rng: [(ints(rng, n, 1, 6),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count occurrences, then sort the distinct values by (-count, value).",
         "Emit each value its full number of times.",
         "The tie-break makes the output unique."],
        explanations=["2 appears three times, then 1 twice, then 3 once.",
                      "Both appear once, so ascending value decides."],
    ))

    add(P(
        "sort-by-absolute-value", "Sort By Absolute Value", "easy", T + ["Arrays"], S,
        "Sort `nums` by ascending absolute value, breaking ties by putting the smaller (more negative) "
        "value first. Print the result.",
        [p_nums()], OUT_INT_LIST, lambda nums: sorted(nums, key=lambda v: (abs(v), v)),
        [([-3, 1, -1, 2],), ([5],)], g_nums(-30, 30),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sort with a composite key of absolute value then the value itself.",
         "The tie-break matters when a number and its negation both appear.",
         "Most languages accept a tuple key directly."],
        explanations=["-1 and 1 tie on magnitude, so -1 comes first.", "A single element."],
    ))

    add(P(
        "sort-pairs-by-second", "Sort Pairs By Second Value", "easy", T, S,
        "Each entry of `pairs` holds two integers. Sort the entries by ascending second value, breaking "
        "ties by ascending first value, and print each pair on its own line.",
        [Param("pairs", PAIR_LIST, "each pair is a b")], OUT_STR_LIST,
        lambda pairs: [f"{a} {b}" for a, b in sorted(pairs, key=lambda p: (p[1], p[0]))],
        [([(1, 3), (2, 1), (4, 1)],), ([(5, 5)],)],
        lambda rng: [([(rng.randint(-20, 20), rng.randint(-20, 20)) for _ in range(m)],)
                     for m in (1, 2, 3, 6, 15, 40, 120)],
        ["1 <= m <= 2000", "-10^6 <= values <= 10^6"],
        ["Use a comparator or sort key based on the second element.",
         "Add the first element as a tie-break so the answer is unique.",
         "Print the two numbers separated by a space."],
        explanations=["(2,1) and (4,1) tie on 1, so 2 precedes 4.", "A single pair."],
        out_desc="Print `a b` on each line.",
    ))

    add(P(
        "largest-number-from-digits", "Largest Number From Array", "medium",
        T + ["Strings", "Greedy"], S,
        "Arrange the non-negative integers of `nums` into the largest possible concatenated number and "
        "print it as a string.",
        [Param("nums", INT_LIST, "non-negative integers")], OUT_STR,
        lambda nums: _largest_concat(nums),
        [([3, 30, 34, 5, 9],), ([0, 0],)],
        lambda rng: [(ints(rng, n, 0, 500),) for n in (1, 2, 3, 6, 12, 35, 100)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^9"],
        ["Compare two numbers a and b by which of the strings a+b or b+a is larger.",
         "That pairwise rule is a valid total order, so sorting with it works.",
         "Sorting by raw value or digit count is wrong — 3 must precede 30.",
         "An array of only zeros must print 0, not 00."],
        explanations=["9,5,34,3,30 concatenates to 9534330.", "Every value is zero."],
    ))

    add(P(
        "minimum-number-from-digits", "Smallest Number From Array", "medium",
        T + ["Strings", "Greedy"], S,
        "Arrange the positive integers of `nums` into the smallest possible concatenated number and "
        "print it as a string.",
        [Param("nums", INT_LIST, "positive integers")], OUT_STR,
        lambda nums: _smallest_concat(nums),
        [([3, 30, 34, 5, 9],), ([12],)],
        lambda rng: [(ints(rng, n, 1, 500),) for n in (1, 2, 3, 6, 12, 35, 100)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^9"],
        ["Sort with the comparator that puts a before b when a+b < b+a as strings.",
         "This is the mirror of the largest-number ordering.",
         "Because the values are positive there is no leading-zero edge case."],
        explanations=["3,30,34,5,9 becomes 3033459.", "A single value."],
    ))

    add(P(
        "kth-missing-positive-sorted", "Kth Missing Positive", "medium", T + ["Binary Search"], S,
        "The array `nums` is strictly increasing and contains positive integers. Print the `k`-th "
        "positive integer missing from it.",
        [Param("nums", INT_LIST, "strictly increasing positive integers"), p_int("k", "1-based rank")],
        OUT_INT, lambda nums, k: _kth_missing(nums, k),
        [([2, 3, 4, 7, 11], 5), ([1, 2, 3], 2)],
        lambda rng: [(_strict_increasing(rng, n), rng.randint(1, 20)) for n in (1, 2, 3, 6, 12, 40, 120)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^6", "nums is strictly increasing", "1 <= k <= 10^6"],
        ["Before index i, exactly nums[i] - (i+1) positive integers are missing.",
         "That count is non-decreasing, so binary search for the first index where it reaches k.",
         "The answer is then k plus the number of array elements before it.",
         "A linear scan also works at these limits."],
        explanations=["Missing are 1,5,6,8,9 so the 5th is 9.", "Missing are 4,5 so the 2nd is 5."],
        brute=lambda nums, k: _kth_missing_brute(nums, k),
    ))

    add(P(
        "find-h-index", "H Index", "medium", T + ["Arrays"], S,
        "Given citation counts `nums`, print the largest `h` such that at least `h` entries have a value "
        "of at least `h`.",
        [Param("nums", INT_LIST, "non-negative citation counts")], OUT_INT,
        lambda nums: _h_index(nums),
        [([3, 0, 6, 1, 5],), ([0, 0],)],
        lambda rng: [(ints(rng, n, 0, 25),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^6"],
        ["Sort descending, then find the largest index i (1-based) where nums[i-1] >= i.",
         "Counting sort over 0..n also solves it in O(n).",
         "The answer never exceeds n."],
        explanations=["Three papers have at least 3 citations.", "No paper has any citation."],
        brute=lambda nums: max((h for h in range(len(nums) + 1)
                                if sum(1 for v in nums if v >= h) >= h), default=0),
    ))

    add(P(
        "minimum-swaps-to-sort", "Minimum Swaps To Sort", "medium", T + ["Arrays", "Graphs"], S,
        "Print the minimum number of arbitrary swaps needed to sort `nums` ascending. All values are "
        "distinct.",
        [Param("nums", INT_LIST, "distinct integers")], OUT_INT,
        lambda nums: _min_swaps_to_sort(nums),
        [([4, 3, 2, 1],), ([1, 2],)],
        lambda rng: [(_distinct(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "all values are distinct", "-10^6 <= nums[i] <= 10^6"],
        ["Map each element to the index it belongs at, forming a permutation.",
         "That permutation decomposes into cycles.",
         "A cycle of length L needs L-1 swaps, so the answer is n minus the number of cycles.",
         "Fixed points are cycles of length 1 and cost nothing."],
        explanations=["Two swaps sort [4,3,2,1].", "Already sorted."],
    ))

    add(P(
        "three-way-partition-count", "Count In Three Ranges", "easy", T + ["Arrays"], S,
        "Print three integers: how many values of `nums` are less than `low`, how many lie in the "
        "inclusive range `[low, high]`, and how many exceed `high`.",
        [p_nums(), p_int("low"), p_int("high")], OUT_INT_LIST,
        lambda nums, low, high: [sum(1 for v in nums if v < low),
                                 sum(1 for v in nums if low <= v <= high),
                                 sum(1 for v in nums if v > high)],
        [([1, 5, 10, 3], 3, 8), ([1], 5, 9)],
        lambda rng: [(lambda lo: (ints(rng, n, -30, 30), lo, lo + rng.randint(0, 20)))(rng.randint(-30, 20))
                     for n in SIZES],
        ["1 <= n <= 2000", "low <= high", "-10^6 <= values <= 10^6"],
        ["Three counters and one pass are enough.",
         "The three counts must sum to n.",
         "Use inclusive comparisons for the middle bucket."],
        out_desc="Print `below inRange above`.",
        explanations=["1 is below, 5 and 3 are in range, 10 is above.", "1 is below 5."],
    ))

    add(P(
        "check-if-sorted-and-rotated", "Sorted And Rotated", "easy", T + ["Arrays"], S,
        "Print `YES` if `nums` can be obtained by rotating a non-decreasing array, else `NO`.",
        [p_nums()], OUT_BOOL, lambda nums: _sorted_rotated(nums),
        [([3, 4, 5, 1, 2],), ([2, 1, 3],)],
        lambda rng: [(_maybe_rotated(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count the positions where an element is greater than its successor, treating the array as circular.",
         "A sorted-and-rotated array has at most one such drop.",
         "A fully sorted array has zero drops, which also counts as a valid rotation."],
        explanations=["Rotating [1,2,3,4,5] gives this array.", "There are two drops."],
    ))

    add(P(
        "relative-sort-by-reference", "Sort By Reference Order", "medium", T + ["Arrays", "Hashing"], S,
        "Sort `nums` so values appearing in `order` come first in the order they appear there. Values "
        "absent from `order` follow, sorted ascending. Print the result.",
        [p_nums(), Param("order", INT_LIST, "the reference ordering")], OUT_INT_LIST,
        lambda nums, order: _relative_sort(nums, order),
        [([2, 3, 1, 3, 2, 4], [2, 1, 3]), ([5], [9])],
        lambda rng: [(ints(rng, n, 1, 6), _distinct_small(rng)) for n in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= n <= 2000", "1 <= |order| <= 100", "order contains distinct values"],
        ["Build a map from value to its rank in `order`.",
         "Sort with a key of (rank, value), giving absent values a rank beyond the end.",
         "Absent values then fall to the back and sort among themselves by value."],
        explanations=["2s, then 1, then 3s, then the leftover 4.", "5 is absent from order."],
    ))

    add(P(
        "count-elements-in-range-sorted", "Count In Range", "easy", T + ["Binary Search"], S,
        "The array `nums` is sorted. Print how many of its elements lie in the inclusive range "
        "`[low, high]`.",
        [Param("nums", INT_LIST, "sorted non-decreasing"), p_int("low"), p_int("high")], OUT_INT,
        lambda nums, low, high: sum(1 for v in nums if low <= v <= high),
        [([1, 2, 4, 4, 7], 2, 4), ([5], 1, 3)],
        lambda rng: [(lambda lo: (sorted(ints(rng, n, -30, 30)), lo, lo + rng.randint(0, 20)))(rng.randint(-30, 20))
                     for n in SIZES],
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order", "low <= high"],
        ["Binary search the first index with value >= low and the first with value > high.",
         "The difference between those positions is the count.",
         "Most standard libraries expose lower_bound / upper_bound equivalents."],
        explanations=["2, 4 and 4 fall in range.", "5 is outside the range."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _bubble_swaps(nums):
    values = list(nums)
    swaps = 0
    for end in range(len(values) - 1, 0, -1):
        for index in range(end):
            if values[index] > values[index + 1]:
                values[index], values[index + 1] = values[index + 1], values[index]
                swaps += 1
    return swaps


def _selection_swaps(nums):
    values = list(nums)
    swaps = 0
    for start in range(len(values)):
        smallest = start
        for index in range(start + 1, len(values)):
            if values[index] < values[smallest]:
                smallest = index
        if smallest != start:
            values[start], values[smallest] = values[smallest], values[start]
            swaps += 1
    return swaps


def _insertion_shifts(nums):
    values = list(nums)
    shifts = 0
    for index in range(1, len(values)):
        current = values[index]
        position = index - 1
        while position >= 0 and values[position] > current:
            values[position + 1] = values[position]
            position -= 1
            shifts += 1
        values[position + 1] = current
    return shifts


def _merge_sort(nums):
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    left = _merge_sort(nums[:mid])
    right = _merge_sort(nums[mid:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def _quick_sort(nums):
    if len(nums) <= 1:
        return list(nums)
    pivot = nums[len(nums) // 2]
    smaller = [v for v in nums if v < pivot]
    equal = [v for v in nums if v == pivot]
    larger = [v for v in nums if v > pivot]
    return _quick_sort(smaller) + equal + _quick_sort(larger)


def _counting_sort(nums):
    counts = [0] * 1001
    for value in nums:
        counts[value] += 1
    result = []
    for value, count in enumerate(counts):
        result.extend([value] * count)
    return result


def _sort_by_frequency(nums):
    counts: dict[int, int] = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    result = []
    for value, count in ordered:
        result.extend([value] * count)
    return result


def _concat_compare(a: str, b: str) -> int:
    if a + b > b + a:
        return -1
    if a + b < b + a:
        return 1
    return 0


def _largest_concat(nums):
    parts = sorted((str(v) for v in nums), key=cmp_to_key(_concat_compare))
    joined = "".join(parts)
    return "0" if joined.lstrip("0") == "" else joined


def _smallest_concat(nums):
    parts = sorted((str(v) for v in nums), key=cmp_to_key(lambda a, b: -_concat_compare(a, b)))
    return "".join(parts)


def _kth_missing(nums, k):
    missing_before = [value - (index + 1) for index, value in enumerate(nums)]
    low, high = 0, len(nums)
    while low < high:
        mid = (low + high) // 2
        if missing_before[mid] < k:
            low = mid + 1
        else:
            high = mid
    return k + low


def _kth_missing_brute(nums, k):
    present = set(nums)
    seen = 0
    value = 0
    while seen < k:
        value += 1
        if value not in present:
            seen += 1
    return value


def _strict_increasing(rng, n):
    values = []
    current = rng.randint(1, 4)
    for _ in range(n):
        values.append(current)
        current += rng.randint(1, 4)
    return values


def _h_index(nums):
    values = sorted(nums, reverse=True)
    h = 0
    for index, value in enumerate(values, start=1):
        if value >= index:
            h = index
        else:
            break
    return h


def _min_swaps_to_sort(nums):
    order = sorted(range(len(nums)), key=lambda i: nums[i])
    seen = [False] * len(nums)
    swaps = 0
    for start in range(len(nums)):
        if seen[start] or order[start] == start:
            continue
        length = 0
        node = start
        while not seen[node]:
            seen[node] = True
            node = order[node]
            length += 1
        swaps += length - 1
    return swaps


def _distinct(rng, n):
    values = rng.sample(range(-1000, 1000), n)
    return values


def _distinct_small(rng):
    size = rng.randint(1, 6)
    return rng.sample(range(1, 8), size)


def _sorted_rotated(nums):
    drops = sum(1 for index in range(len(nums)) if nums[index] > nums[(index + 1) % len(nums)])
    return drops <= 1


def _maybe_rotated(rng, n):
    base = sorted(ints(rng, n, -30, 30))
    if rng.random() < 0.6:
        shift = rng.randint(0, n - 1)
        return base[shift:] + base[:shift]
    return ints(rng, n, -30, 30)


def _relative_sort(nums, order):
    rank = {value: index for index, value in enumerate(order)}
    return sorted(nums, key=lambda v: (rank.get(v, len(order)), v))
