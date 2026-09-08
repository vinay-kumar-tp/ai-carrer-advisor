"""Fixed and variable sized sliding windows."""

from __future__ import annotations

import random
from collections import Counter, deque

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    Param,
    STR,
    ints,
    p_int,
    p_nums,
    word,
)

T = ["Sliding Window"]
SW = ["Sliding Window"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)
SMALL = "abc"


def g_nums_k(lo=-30, hi=30, sizes=SIZES):
    """k is always a valid window length for the generated array."""
    def gen(rng: random.Random):
        return [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, lo, hi)) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "max-sum-window-k", "Maximum Sum Window", "easy", T + ["Arrays"], SW,
        "Print the largest sum of any contiguous subarray of `nums` of exactly length `k`.",
        [p_nums(), p_int("k", "window length")], OUT_INT,
        lambda nums, k: _max_window_sum(nums, k),
        [([2, 1, 5, 1, 3, 2], 3), ([4], 1)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sum the first k elements to seed the window.",
         "Slide by adding the incoming element and subtracting the outgoing one.",
         "Track the best sum, giving O(n) instead of O(n*k)."],
        explanations=["[5,1,3] sums to 9.", "The only window is [4]."],
        brute=lambda nums, k: max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1)),
        pattern_note="A fixed-size window keeps a running aggregate: add the entering element, remove the "
                     "leaving one. Nothing inside the window is ever re-read.",
    ))

    add(P(
        "min-sum-window-k", "Minimum Sum Window", "easy", T + ["Arrays"], SW,
        "Print the smallest sum of any contiguous subarray of `nums` of exactly length `k`.",
        [p_nums(), p_int("k", "window length")], OUT_INT,
        lambda nums, k: -_max_window_sum([-v for v in nums], k),
        [([2, 1, 5, 1, 3, 2], 3), ([7], 1)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Mirror the maximum version, tracking the minimum instead.",
         "Or negate every element, find the maximum, then negate the answer.",
         "Seed the running sum with the first k elements."],
        brute=lambda nums, k: min(sum(nums[i:i + k]) for i in range(len(nums) - k + 1)),
    ))

    add(P(
        "max-in-each-window", "Sliding Window Maximum", "hard", T + ["Arrays", "Stack & Queue"], SW,
        "Print the maximum of every contiguous window of length `k` in `nums`, left to right, space "
        "separated.",
        [p_nums(), p_int("k", "window length")], OUT_INT_LIST,
        lambda nums, k: _window_maxima(nums, k),
        [([1, 3, -1, -3, 5, 3, 6, 7], 3), ([9], 1)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["A monotonic deque of indices solves this in O(n).",
         "Keep the deque decreasing: before pushing, pop every smaller value from the back.",
         "Pop from the front when its index falls out of the window.",
         "The front always holds the index of the current window's maximum."],
        explanations=["Window maxima are 3,3,5,5,6,7.", "The single window's maximum is 9."],
        brute=lambda nums, k: [max(nums[i:i + k]) for i in range(len(nums) - k + 1)],
        pattern_note="A monotonic deque discards elements that can never win again: if a newer element is "
                     "larger, every older smaller element is permanently dominated.",
    ))

    add(P(
        "min-in-each-window", "Sliding Window Minimum", "hard", T + ["Arrays", "Stack & Queue"], SW,
        "Print the minimum of every contiguous window of length `k` in `nums`, left to right, space "
        "separated.",
        [p_nums(), p_int("k", "window length")], OUT_INT_LIST,
        lambda nums, k: [-v for v in _window_maxima([-x for x in nums], k)],
        [([1, 3, -1, -3, 5, 3, 6, 7], 3), ([2], 1)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Use an increasing monotonic deque instead of a decreasing one.",
         "Or negate the values, compute window maxima and negate back.",
         "Each index is pushed and popped at most once, giving O(n)."],
        brute=lambda nums, k: [min(nums[i:i + k]) for i in range(len(nums) - k + 1)],
    ))

    add(P(
        "count-distinct-in-windows", "Distinct Values Per Window", "medium",
        T + ["Arrays", "Hashing"], SW,
        "Print the number of distinct values in every contiguous window of length `k` in `nums`, left to "
        "right, space separated.",
        [p_nums(), p_int("k", "window length")], OUT_INT_LIST,
        lambda nums, k: _distinct_per_window(nums, k),
        [([1, 2, 1, 3, 4, 3], 3), ([5], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, 1, 6)) for n in SIZES],
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Maintain a frequency map for the current window.",
         "When a count drops to zero, remove the key so the map size is the distinct count.",
         "Add the entering element and remove the leaving one on each slide."],
        explanations=["Windows give 2,3,3,3 distinct values.", "One element is one distinct value."],
        brute=lambda nums, k: [len(set(nums[i:i + k])) for i in range(len(nums) - k + 1)],
    ))

    add(P(
        "smallest-window-sum-at-least", "Shortest Subarray With Sum At Least K", "medium",
        T + ["Arrays"], SW,
        "Given an array of **positive** integers `nums` and an integer `k`, print the length of the "
        "shortest contiguous subarray whose sum is at least `k`. Print `0` if none exists.",
        [Param("nums", INT_LIST, "positive integers"), p_int("k", "the sum threshold")], OUT_INT,
        lambda nums, k: _min_window_sum_at_least(nums, k),
        [([2, 3, 1, 2, 4, 3], 7), ([1, 1], 9)],
        lambda rng: [(ints(rng, n, 1, 12), rng.randint(1, 40)) for n in SIZES],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^4", "1 <= k <= 10^9"],
        ["Because every value is positive, the window sum grows as the right edge moves.",
         "Expand right until the sum reaches k, then shrink from the left while it still does.",
         "Record the smallest valid length seen.",
         "Positivity is essential — with negatives this monotonicity breaks and you need prefix sums."],
        explanations=["[4,3] has length 2.", "The total is only 2."],
        brute=lambda nums, k: min([len(nums) + 1] + [j - i for i in range(len(nums))
                                                     for j in range(i + 1, len(nums) + 1)
                                                     if sum(nums[i:j]) >= k]) % (len(nums) + 1),
    ))

    add(P(
        "longest-window-sum-at-most", "Longest Subarray With Sum At Most K", "medium",
        T + ["Arrays"], SW,
        "Given an array of **positive** integers `nums` and an integer `k`, print the length of the "
        "longest contiguous subarray whose sum is at most `k`. Print `0` if every element exceeds `k`.",
        [Param("nums", INT_LIST, "positive integers"), p_int("k", "the sum limit")], OUT_INT,
        lambda nums, k: _max_window_sum_at_most(nums, k),
        [([2, 1, 5, 1, 3, 2], 8), ([9, 9], 3)],
        lambda rng: [(ints(rng, n, 1, 12), rng.randint(0, 40)) for n in SIZES],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^4", "0 <= k <= 10^9"],
        ["Grow the right edge and add to the running sum.",
         "While the sum exceeds k, shrink from the left.",
         "After each step the window is valid, so record its length.",
         "The answer is 0 when no single element fits."],
        explanations=["[2,1,5] sums to 8.", "Both elements exceed 3."],
        brute=lambda nums, k: max([0] + [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                         if sum(nums[i:j]) <= k]),
    ))

    add(P(
        "longest-window-k-distinct", "Longest Substring With K Distinct", "medium",
        T + ["Strings", "Hashing"], SW,
        "Print the length of the longest substring of `s` containing at most `k` distinct characters.",
        [Param("s", STR, "lowercase letters"), p_int("k", "the distinct-character limit")], OUT_INT,
        lambda s, k: _longest_k_distinct(s, k),
        [("eceba", 2), ("abc", 0)],
        lambda rng: [(word(rng, n, SMALL), rng.randint(0, 4)) for n in (1, 2, 4, 9, 20, 55, 140, 300)],
        ["1 <= |s| <= 2000", "0 <= k <= 26", "s contains lowercase English letters only"],
        ["Track character counts inside the window.",
         "When the map holds more than k keys, shrink from the left until it does not.",
         "Record the window length after each valid step.",
         "k = 0 means the answer is 0."],
        explanations=["ece has length 3 with two distinct characters.", "No characters are allowed."],
        brute=lambda s, k: max([0] + [j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                                      if len(set(s[i:j])) <= k]),
    ))

    add(P(
        "longest-window-exactly-k-distinct", "Longest Substring With Exactly K Distinct", "medium",
        T + ["Strings", "Hashing"], SW,
        "Print the length of the longest substring of `s` containing **exactly** `k` distinct characters. "
        "Print `0` if no such substring exists.",
        [Param("s", STR, "lowercase letters"), p_int("k", "the exact distinct count")], OUT_INT,
        lambda s, k: _longest_exactly_k(s, k),
        [("aabacbebebe", 3), ("aaa", 2)],
        lambda rng: [(word(rng, n, SMALL), rng.randint(1, 4)) for n in (1, 2, 4, 9, 20, 55, 140, 280)],
        ["1 <= |s| <= 2000", "1 <= k <= 26", "s contains lowercase English letters only"],
        ["Compute the longest window with at most k distinct characters.",
         "A window with exactly k distinct characters is longest when the at-most-k window happens to "
         "hold k keys, so track the best length only while the map size equals k.",
         "Alternatively subtract: atMost(k) - atMost(k-1) answers the counting variant, not the length one.",
         "Return 0 when the string never reaches k distinct characters."],
        explanations=["cbebebe has length 7 with exactly {b,c,e}.", "Only one distinct character exists."],
        brute=lambda s, k: max([0] + [j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                                      if len(set(s[i:j])) == k]),
    ))

    add(P(
        "count-windows-k-distinct", "Count Substrings With K Distinct", "hard",
        T + ["Strings", "Hashing"], SW,
        "Count the substrings of `s` containing exactly `k` distinct characters.",
        [Param("s", STR, "lowercase letters"), p_int("k", "the exact distinct count")], OUT_INT,
        lambda s, k: _count_at_most(s, k) - _count_at_most(s, k - 1),
        [("pqpqs", 2), ("aaa", 2)],
        lambda rng: [(word(rng, n, SMALL), rng.randint(1, 4)) for n in (1, 2, 4, 9, 20, 55, 140, 260)],
        ["1 <= |s| <= 2000", "1 <= k <= 26", "s contains lowercase English letters only"],
        ["Counting 'exactly k' directly is awkward; counting 'at most k' with a sliding window is easy.",
         "For a valid window ending at index r, every left edge in the window starts a valid substring, "
         "so add (r - left + 1).",
         "Then exactly(k) = atMost(k) - atMost(k-1).",
         "This is a standard counting trick worth remembering."],
        explanations=["Seven substrings have exactly two distinct characters.",
                      "The string has only one distinct character."],
        brute=lambda s, k: sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                               if len(set(s[i:j])) == k),
    ))

    add(P(
        "fruit-into-baskets", "Longest Window With Two Distinct", "medium",
        T + ["Arrays", "Hashing"], SW,
        "Print the length of the longest contiguous subarray of `nums` containing at most two distinct "
        "values.",
        [p_nums()], OUT_INT, lambda nums: _longest_at_most_distinct(nums, 2),
        [([1, 2, 1, 2, 3],), ([7],)],
        lambda rng: [(ints(rng, n, 1, 5),) for n in (1, 2, 4, 9, 20, 55, 140, 300)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["This is the at-most-k-distinct window with k fixed at 2.",
         "Keep counts of the values inside the window.",
         "Shrink from the left whenever a third distinct value appears."],
        explanations=["[1,2,1,2] has length 4.", "A single element qualifies."],
        brute=lambda nums: max(j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                               if len(set(nums[i:j])) <= 2),
    ))

    add(P(
        "max-consecutive-ones-k-flips", "Max Consecutive Ones With K Flips", "medium",
        T + ["Arrays"], SW,
        "Given a binary array `nums`, you may flip at most `k` zeros to ones. Print the length of the "
        "longest run of ones you can achieve.",
        [Param("nums", INT_LIST, "each value is 0 or 1"), p_int("k", "flips allowed")], OUT_INT,
        lambda nums, k: _longest_ones_with_flips(nums, k),
        [([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), ([0, 0], 0)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)], rng.randint(0, 3))
                     for n in (1, 2, 4, 9, 20, 55, 140, 300)],
        ["1 <= n <= 2000", "nums[i] is 0 or 1", "0 <= k <= n"],
        ["Slide a window that is allowed to contain at most k zeros.",
         "Expand right, counting zeros; when the count exceeds k, shrink from the left.",
         "The answer is the largest valid window length.",
         "k = 0 reduces to the longest existing run of ones."],
        explanations=["Flipping the two zeros at indices 4 and 5 yields a run of 6.",
                      "No flips allowed and no ones present."],
        brute=lambda nums, k: max([0] + [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                         if nums[i:j].count(0) <= k]),
    ))

    add(P(
        "longest-repeating-char-replacement", "Longest Repeating Character Replacement", "medium",
        T + ["Strings", "Hashing"], SW,
        "You may change at most `k` characters of `s` to any lowercase letter. Print the length of the "
        "longest substring that can be made to contain a single repeated character.",
        [Param("s", STR, "lowercase letters"), p_int("k", "changes allowed")], OUT_INT,
        lambda s, k: _char_replacement(s, k),
        [("aababba", 1), ("abc", 0)],
        lambda rng: [(word(rng, n, SMALL), rng.randint(0, 3)) for n in (1, 2, 4, 9, 20, 55, 140, 280)],
        ["1 <= |s| <= 2000", "0 <= k <= |s|", "s contains lowercase English letters only"],
        ["A window is valid when its length minus the count of its most frequent character is at most k.",
         "That difference is exactly the number of characters you would have to change.",
         "Expand right and shrink left whenever the window becomes invalid.",
         "Tracking the running maximum frequency is enough — it never needs to decrease for correctness."],
        explanations=["Changing one character makes a run of 3 (for example aaa).",
                      "No changes allowed and no repeats exist."],
        brute=lambda s, k: max(j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)
                               if (j - i) - max(Counter(s[i:j]).values()) <= k),
    ))

    add(P(
        "count-anagram-window-occurrences", "Count Anagram Windows", "medium",
        T + ["Strings", "Hashing"], SW,
        "Count how many substrings of `s` of length `|pattern|` are anagrams of `pattern`.",
        [Param("s", STR, "the text"), Param("pattern", STR, "the pattern")], OUT_INT,
        lambda s, pattern: _count_anagram_windows(s, pattern),
        [("cbaebabacd", "abc"), ("abc", "xyz")],
        lambda rng: [(word(rng, n, SMALL), word(rng, rng.randint(1, 3), SMALL))
                     for n in (1, 3, 6, 14, 35, 90, 220)],
        ["1 <= |s| <= 2000", "1 <= |pattern| <= 2000", "lowercase English letters only"],
        ["Compare frequency counts of a fixed-length window against the pattern's counts.",
         "Update the window counts incrementally as it slides.",
         "Two 26-slot arrays compare in constant time.",
         "Print 0 when the pattern is longer than s."],
        explanations=["cba at index 0 and bac at index 6 are anagrams of abc.", "No window matches."],
        brute=lambda s, pattern: sum(1 for i in range(len(s) - len(pattern) + 1)
                                     if Counter(s[i:i + len(pattern)]) == Counter(pattern)),
    ))

    add(P(
        "max-average-window-value", "Maximum Window Average", "easy", T + ["Arrays"], SW,
        "Print the largest average of any contiguous subarray of `nums` of exactly length `k`.",
        [p_nums(), p_int("k", "window length")], "float",
        lambda nums, k: _max_window_sum(nums, k) / k,
        [([1, 12, -5, -6, 50, 3], 4), ([5], 1)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Find the maximum window sum first.",
         "Divide by k at the very end to avoid repeated floating-point work.",
         "Print exactly 6 decimal places."],
        explanations=["The best sum 51 over 4 elements gives 12.75.", "5 / 1 = 5."],
    ))

    add(P(
        "count-subarrays-product-less-than-k", "Subarrays With Product Below K", "medium",
        T + ["Arrays"], SW,
        "Given an array of **positive** integers `nums`, count the contiguous subarrays whose product is "
        "strictly less than `k`.",
        [Param("nums", INT_LIST, "positive integers"), p_int("k", "the product limit")], OUT_INT,
        lambda nums, k: _count_product_below(nums, k),
        [([10, 5, 2, 6], 100), ([1, 2], 0)],
        lambda rng: [(ints(rng, n, 1, 8), rng.randint(0, 200)) for n in (1, 2, 4, 9, 20, 55, 140, 280)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 100", "0 <= k <= 10^9"],
        ["With positive values the window product grows as the right edge moves.",
         "Shrink from the left while the product is at least k.",
         "Each valid right edge contributes (right - left + 1) subarrays.",
         "k <= 1 yields 0 because every product is at least 1."],
        explanations=["Eight subarrays have a product below 100.", "No product is below 0."],
        brute=lambda nums, k: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                  if _prod(nums[i:j]) < k),
    ))

    add(P(
        "first-negative-in-window", "First Negative Per Window", "medium", T + ["Arrays", "Stack & Queue"], SW,
        "For every contiguous window of length `k` in `nums`, print the first negative value it contains, "
        "or `0` if it has none. Print the answers space separated.",
        [p_nums(), p_int("k", "window length")], OUT_INT_LIST,
        lambda nums, k: _first_negative_windows(nums, k),
        [([-8, 2, 3, -6, 10], 2), ([1, 2], 2)],
        g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Keep a queue of the indices of negative values currently in the window.",
         "Discard front indices that have slid out of range.",
         "The front of the queue is the first negative; an empty queue means print 0."],
        explanations=["Windows give -8, 0, -6, -6.", "The window has no negative value."],
        brute=lambda nums, k: [next((v for v in nums[i:i + k] if v < 0), 0)
                               for i in range(len(nums) - k + 1)],
    ))

    add(P(
        "window-sum-equals-target-exists", "Window With Exact Sum Exists", "easy", T + ["Arrays"], SW,
        "Given an array of **positive** integers `nums`, print `YES` if some contiguous subarray sums to "
        "exactly `target`, else `NO`.",
        [Param("nums", INT_LIST, "positive integers"), p_int("target")], OUT_BOOL,
        lambda nums, target: _has_window_sum(nums, target),
        [([1, 4, 20, 3, 10, 5], 33), ([1, 4], 9)],
        lambda rng: [(ints(rng, n, 1, 15), rng.randint(1, 60)) for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^4", "1 <= target <= 10^9"],
        ["With positive values a two-pointer window works: grow right, shrink left when the sum overshoots.",
         "Stop as soon as the sum matches.",
         "For arrays containing negatives you would need prefix sums with a hash set instead."],
        explanations=["[20,3,10] sums to 33.", "No subarray sums to 9."],
        brute=lambda nums, target: any(sum(nums[i:j]) == target for i in range(len(nums))
                                       for j in range(i + 1, len(nums) + 1)),
    ))

    add(P(
        "count-windows-with-all-values", "Windows Containing All Distinct Values", "medium",
        T + ["Arrays", "Hashing"], SW,
        "Let `d` be the number of distinct values in `nums`. Count the contiguous subarrays that contain "
        "all `d` distinct values.",
        [p_nums()], OUT_INT, lambda nums: _count_windows_all_distinct(nums),
        [([1, 2, 1, 3],), ([4, 4],)],
        lambda rng: [(ints(rng, n, 1, 4),) for n in (1, 2, 4, 9, 20, 55, 140, 260)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["First count the distinct values in the whole array.",
         "Then slide a window, shrinking from the left while it still holds all of them.",
         "Once minimal for a given right edge, every earlier left edge also works, adding (left + 1) windows.",
         "A single distinct value makes every subarray qualify."],
        explanations=["Subarrays [1,2,1,3] and [2,1,3] contain all of {1,2,3}.",
                      "All three subarrays contain the only value."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                               if len(set(nums[i:j])) == len(set(nums))),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _prod(values):
    result = 1
    for value in values:
        result *= value
    return result


def _max_window_sum(nums, k):
    running = sum(nums[:k])
    best = running
    for index in range(k, len(nums)):
        running += nums[index] - nums[index - k]
        best = max(best, running)
    return best


def _window_maxima(nums, k):
    window: deque[int] = deque()
    result = []
    for index, value in enumerate(nums):
        while window and nums[window[-1]] <= value:
            window.pop()
        window.append(index)
        if window[0] <= index - k:
            window.popleft()
        if index >= k - 1:
            result.append(nums[window[0]])
    return result


def _distinct_per_window(nums, k):
    counts: dict[int, int] = {}
    result = []
    for index, value in enumerate(nums):
        counts[value] = counts.get(value, 0) + 1
        if index >= k:
            outgoing = nums[index - k]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
        if index >= k - 1:
            result.append(len(counts))
    return result


def _min_window_sum_at_least(nums, k):
    best = 0
    running = 0
    left = 0
    for right, value in enumerate(nums):
        running += value
        while running >= k:
            length = right - left + 1
            if best == 0 or length < best:
                best = length
            running -= nums[left]
            left += 1
    return best


def _max_window_sum_at_most(nums, k):
    best = 0
    running = 0
    left = 0
    for right, value in enumerate(nums):
        running += value
        while left <= right and running > k:
            running -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best


def _longest_k_distinct(s, k):
    if k == 0:
        return 0
    counts: dict[str, int] = {}
    best = 0
    left = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            outgoing = s[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        best = max(best, right - left + 1)
    return best


def _longest_exactly_k(s, k):
    counts: dict[str, int] = {}
    best = 0
    left = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            outgoing = s[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        if len(counts) == k:
            best = max(best, right - left + 1)
    return best


def _count_at_most(s, k):
    if k <= 0:
        return 0
    counts: dict[str, int] = {}
    total = 0
    left = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while len(counts) > k:
            outgoing = s[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        total += right - left + 1
    return total


def _longest_at_most_distinct(nums, k):
    counts: dict[int, int] = {}
    best = 0
    left = 0
    for right, value in enumerate(nums):
        counts[value] = counts.get(value, 0) + 1
        while len(counts) > k:
            outgoing = nums[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        best = max(best, right - left + 1)
    return best


def _longest_ones_with_flips(nums, k):
    zeros = 0
    best = 0
    left = 0
    for right, value in enumerate(nums):
        if value == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def _char_replacement(s, k):
    counts: dict[str, int] = {}
    best = 0
    left = 0
    most = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        most = max(most, counts[ch])
        while (right - left + 1) - most > k:
            counts[s[left]] -= 1
            left += 1
            most = max(counts.values()) if counts else 0
        best = max(best, right - left + 1)
    return best


def _count_anagram_windows(s, pattern):
    size = len(pattern)
    if size > len(s):
        return 0
    need = Counter(pattern)
    window = Counter(s[:size])
    total = 1 if window == need else 0
    for index in range(size, len(s)):
        window[s[index]] += 1
        outgoing = s[index - size]
        window[outgoing] -= 1
        if window[outgoing] == 0:
            del window[outgoing]
        if window == need:
            total += 1
    return total


def _count_product_below(nums, k):
    if k <= 1:
        return 0
    total = 0
    product = 1
    left = 0
    for right, value in enumerate(nums):
        product *= value
        while product >= k and left <= right:
            product //= nums[left]
            left += 1
        total += right - left + 1
    return total


def _first_negative_windows(nums, k):
    negatives: deque[int] = deque()
    result = []
    for index, value in enumerate(nums):
        if value < 0:
            negatives.append(index)
        while negatives and negatives[0] <= index - k:
            negatives.popleft()
        if index >= k - 1:
            result.append(nums[negatives[0]] if negatives else 0)
    return result


def _has_window_sum(nums, target):
    running = 0
    left = 0
    for right, value in enumerate(nums):
        running += value
        while running > target and left <= right:
            running -= nums[left]
            left += 1
        if running == target:
            return True
    return False


def _count_windows_all_distinct(nums):
    needed = len(set(nums))
    counts: dict[int, int] = {}
    total = 0
    left = 0
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
        # Advance `left` past every position that still leaves a complete window.
        while len(counts) == needed:
            outgoing = nums[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        # Now [left..right] is incomplete, so lefts 0..left-1 all give valid windows.
        total += left
    return total
