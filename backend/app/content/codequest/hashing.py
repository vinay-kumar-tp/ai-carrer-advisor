"""Hash map and frequency-counting problems."""

from __future__ import annotations

import random
from collections import Counter

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR_LIST,
    P,
    Param,
    STR,
    STR_LIST,
    ints,
    p_int,
    p_nums,
    word,
    words,
)

T = ["Hashing"]
H = ["Hashing / Frequency"]
SIZES = (1, 2, 4, 9, 20, 55, 140, 300)
SMALL = "abc"


def g_small(lo=1, hi=8, sizes=SIZES):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "two-sum-indices", "Two Sum Indices", "easy", T + ["Arrays"], H,
        "Find two different positions of `nums` whose values sum to `target` and print their 0-based "
        "indices in increasing order. Print `-1` if no pair exists. If several pairs work, print the "
        "one whose second index is smallest.",
        [p_nums(), p_int("target", "required pair sum")], OUT_INT_LIST,
        lambda nums, target: _two_sum(nums, target),
        [([2, 7, 11, 15], 9), ([3, 3], 7)],
        lambda rng: [(ints(rng, n, -20, 20), rng.randint(-30, 30)) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["Scan once, keeping a map from value to its earliest index.",
         "For each element look up target - value in the map before inserting the current element.",
         "Inserting after the lookup guarantees you never pair an element with itself.",
         "This finds the pair with the smallest second index, which is the required tie-break."],
        explanations=["2 + 7 = 9 at indices 0 and 1.", "No pair sums to 7."],
        out_desc="Print the two indices separated by a space, or -1.",
        brute=lambda nums, target: _two_sum_brute(nums, target),
        pattern_note="A hash map turns 'does the complement exist?' into an O(1) question, converting the "
                     "O(n^2) pair search into a single pass.",
    ))

    add(P(
        "contains-duplicate", "Contains Duplicate", "easy", T + ["Arrays"], H,
        "Print `YES` if any value appears at least twice in `nums`, else `NO`.",
        [p_nums()], OUT_BOOL, lambda nums: len(set(nums)) != len(nums),
        [([1, 2, 3, 1],), ([1, 2],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Insert values into a set and stop at the first one already present.",
         "Comparing the set size against n also works.",
         "Sorting and checking neighbours is O(n log n) with O(1) extra space."],
    ))

    add(P(
        "contains-duplicate-within-k", "Duplicate Within Distance K", "medium", T + ["Arrays"], H,
        "Print `YES` if `nums` contains two equal values at positions at most `k` apart, else `NO`.",
        [p_nums(), p_int("k", "maximum index distance")], OUT_BOOL,
        lambda nums, k: _duplicate_within_k(nums, k),
        [([1, 2, 3, 1], 3), ([1, 2, 3, 1], 2)],
        lambda rng: [(ints(rng, n, 1, 6), rng.randint(0, 5)) for n in SIZES],
        ["1 <= n <= 2000", "0 <= k <= n", "-10^6 <= nums[i] <= 10^6"],
        ["Keep a sliding window of the last k values in a set.",
         "Remove the element that falls out of the window before checking the new one.",
         "Alternatively store each value's last index and compare distances.",
         "k = 0 can never produce a match since two positions must differ."],
        explanations=["The two 1s are 3 apart.", "They are 3 apart, which exceeds 2."],
        brute=lambda nums, k: any(nums[i] == nums[j] for i in range(len(nums))
                                  for j in range(i + 1, min(len(nums), i + k + 1))),
    ))

    add(P(
        "frequency-map-sorted", "Frequency Table", "easy", T + ["Arrays"], H,
        "Print each distinct value of `nums` followed by its count, one pair per line, ordered by "
        "increasing value.",
        [p_nums()], OUT_STR_LIST, lambda nums: _frequency_lines(nums),
        [([2, 1, 2, 3],), ([5],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count with a hash map in one pass.",
         "Sort the distinct keys before printing so the output is deterministic.",
         "Print the value and the count separated by a single space."],
        explanations=["1 appears once, 2 twice, 3 once.", "5 appears once."],
        out_desc="Print `value count` on each line.",
    ))

    add(P(
        "elements-appearing-once", "Values Appearing Once", "easy", T + ["Arrays"], H,
        "Print the values of `nums` that occur exactly once, in ascending order. Print an empty line if "
        "there are none.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: sorted(v for v, c in Counter(nums).items() if c == 1),
        [([1, 2, 2, 3],), ([4, 4],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Build the frequency map, then filter for count 1.",
         "Sort the survivors before printing.",
         "The result can legitimately be empty."],
    ))

    add(P(
        "elements-appearing-more-than-k", "Values Appearing More Than K Times", "easy",
        T + ["Arrays"], H,
        "Print the values of `nums` occurring strictly more than `k` times, in ascending order. Print an "
        "empty line if there are none.",
        [p_nums(), p_int("k", "the count threshold")], OUT_INT_LIST,
        lambda nums, k: sorted(v for v, c in Counter(nums).items() if c > k),
        [([1, 1, 2, 2, 2], 1), ([1, 2], 5)],
        lambda rng: [(ints(rng, n, 1, 5), rng.randint(0, 4)) for n in SIZES],
        ["1 <= n <= 2000", "0 <= k <= n", "-10^6 <= nums[i] <= 10^6"],
        ["Count first, then filter with a strict comparison.",
         "k = 0 keeps every distinct value.",
         "Sort the result for a deterministic output."],
        explanations=["Only 2 appears more than once.", "Nothing appears more than 5 times."],
    ))

    add(P(
        "longest-consecutive-sequence", "Longest Consecutive Sequence", "medium",
        T + ["Arrays"], H,
        "Print the length of the longest run of consecutive integers that can be formed from the values "
        "of `nums` (the values need not be adjacent in the array).",
        [p_nums()], OUT_INT, lambda nums: _longest_consecutive(nums),
        [([100, 4, 200, 1, 3, 2],), ([5, 5],)],
        lambda rng: [(ints(rng, n, 1, max(3, n)),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Put the values in a hash set to get O(1) membership tests.",
         "Only start counting from a value whose predecessor is absent — that is the head of a run.",
         "Walk upwards from each head while the next value exists.",
         "Each value is visited at most twice, so the whole thing is O(n)."],
        explanations=["1,2,3,4 gives length 4.", "Only the single value 5 forms a run."],
        brute=lambda nums: _longest_consecutive_brute(nums),
    ))

    add(P(
        "first-repeating-element", "First Repeating Value", "easy", T + ["Arrays"], H,
        "Print the value of `nums` whose **first** occurrence comes earliest among values that appear "
        "more than once. Print `-1` if every value is unique.",
        [p_nums()], OUT_INT, lambda nums: _first_repeating(nums),
        [([1, 5, 3, 4, 3, 5, 6],), ([1, 2, 3],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count all values first.",
         "Then scan the array left to right and return the first value with count above 1.",
         "Two passes are needed because a repeat may appear far to the right."],
        explanations=["5 repeats and its first occurrence (index 1) precedes 3's (index 2).",
                      "Nothing repeats."],
        brute=lambda nums: next((v for v in nums if nums.count(v) > 1), -1),
    ))

    add(P(
        "subarray-with-zero-sum-exists", "Zero Sum Subarray Exists", "easy",
        T + ["Arrays", "Prefix Sum"], H,
        "Print `YES` if `nums` has a non-empty contiguous subarray summing to `0`, else `NO`.",
        [p_nums()], OUT_BOOL, lambda nums: _has_zero_sum(nums),
        [([4, 2, -3, 1, 6],), ([1, 2],)],
        lambda rng: [(ints(rng, n, -5, 5),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Track prefix sums in a set.",
         "A repeated prefix sum (or a prefix sum of 0) proves a zero-sum subarray exists.",
         "Seed the set with 0 to catch subarrays starting at index 0."],
        explanations=["2 + (-3) + 1 = 0.", "Every subarray sums above zero."],
        brute=lambda nums: any(sum(nums[i:j]) == 0 for i in range(len(nums))
                               for j in range(i + 1, len(nums) + 1)),
    ))

    add(P(
        "group-strings-by-length", "Group Words By Length", "easy", T + ["Strings"], H,
        "For each distinct word length present, print the length followed by how many words have it, one "
        "pair per line, ordered by increasing length.",
        [Param("wordsList", STR_LIST, "the words")], OUT_STR_LIST,
        lambda wordsList: [f"{length} {count}" for length, count
                           in sorted(Counter(len(w) for w in wordsList).items())],
        [(["a", "bb", "cc", "ddd"],), (["x"],)],
        lambda rng: [(words(rng, count, 1, 6),) for count in (1, 2, 5, 12, 35, 90)],
        ["1 <= number of words <= 1000", "1 <= |word| <= 200"],
        ["Count occurrences of each length with a map.",
         "Sort the keys before printing.",
         "The counts must sum to the number of words."],
        explanations=["One word of length 1, two of length 2, one of length 3.", "A single word."],
        out_desc="Print `length count` on each line.",
    ))

    add(P(
        "check-array-permutation", "Arrays Are Permutations", "easy", T + ["Arrays"], H,
        "Print `YES` if `a` and `b` contain the same values with the same multiplicities, else `NO`.",
        [Param("a", INT_LIST, "first array"), Param("b", INT_LIST, "second array")], OUT_BOOL,
        lambda a, b: Counter(a) == Counter(b),
        [([1, 2, 2], [2, 1, 2]), ([1, 2], [1, 1])],
        lambda rng: [(lambda arr: (arr, _maybe_shuffle(rng, arr)))(ints(rng, n, 1, 6)) for n in SIZES],
        ["1 <= n, m <= 2000", "-10^6 <= values <= 10^6"],
        ["Different lengths can be rejected immediately.",
         "Compare frequency maps rather than sorting for O(n).",
         "Sorting both and comparing is the simpler O(n log n) alternative."],
    ))

    add(P(
        "count-pairs-sum-divisible-k", "Pairs With Sum Divisible By K", "medium",
        T + ["Arrays"], H,
        "Count the pairs of positions `(i, j)` with `i < j` where `nums[i] + nums[j]` is divisible by "
        "the positive integer `k`.",
        [p_nums(), p_int("k", "the divisor")], OUT_INT,
        lambda nums, k: _count_pairs_divisible(nums, k),
        [([1, 3, 2, 6, 1, 2], 3), ([1, 2], 5)],
        lambda rng: [(ints(rng, n, 1, 20), rng.randint(1, 6)) for n in (1, 2, 4, 9, 20, 55, 140)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^6", "1 <= k <= 10^4",
         "the answer fits in a 64-bit signed integer"],
        ["Bucket the values by their remainder modulo k.",
         "Remainders r and k-r pair up; count bucket[r] * bucket[k-r].",
         "Remainder 0 pairs with itself, contributing C(count, 2).",
         "When k is even, remainder k/2 also pairs with itself."],
        explanations=["Five pairs have a sum divisible by 3.", "1 + 2 = 3 is not divisible by 5."],
        brute=lambda nums, k: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                                  if (nums[i] + nums[j]) % k == 0),
    ))

    add(P(
        "find-all-duplicates", "Find All Duplicates", "easy", T + ["Arrays"], H,
        "Print every value of `nums` that appears more than once, in ascending order, each listed once. "
        "Print an empty line if there are none.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: sorted(v for v, c in Counter(nums).items() if c > 1),
        [([4, 3, 2, 7, 8, 2, 3, 1],), ([1, 2],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count values, then keep those with count above 1.",
         "Report each duplicated value once, not once per extra copy.",
         "Sort the result before printing."],
        explanations=["2 and 3 both repeat.", "Nothing repeats."],
    ))

    add(P(
        "intersection-count-multiset", "Common Values With Multiplicity", "easy",
        T + ["Arrays"], H,
        "Print how many values `a` and `b` share counting multiplicity: a value present twice in `a` and "
        "three times in `b` contributes 2.",
        [Param("a", INT_LIST, "first array"), Param("b", INT_LIST, "second array")], OUT_INT,
        lambda a, b: sum((Counter(a) & Counter(b)).values()),
        [([1, 2, 2, 3], [2, 2, 4]), ([1], [2])],
        lambda rng: [(ints(rng, n, 1, 8), ints(rng, m, 1, 8))
                     for n, m in ((1, 1), (2, 3), (5, 4), (12, 9), (30, 25), (90, 70))],
        ["1 <= n, m <= 2000", "-10^6 <= values <= 10^6"],
        ["Count both arrays.",
         "For each value take the smaller of the two counts.",
         "Sum those minima."],
        explanations=["2 appears twice in both.", "Nothing is shared."],
    ))

    add(P(
        "most-frequent-even-value", "Most Frequent Even Value", "easy", T + ["Arrays"], H,
        "Print the most frequent even value in `nums`, breaking ties by the smaller value. Print `-1` if "
        "there is no even value.",
        [p_nums()], OUT_INT, lambda nums: _most_frequent_even(nums),
        [([0, 1, 2, 2, 4, 4, 1],), ([1, 3],)],
        lambda rng: [(ints(rng, n, 0, 8),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^6"],
        ["Count only the even values.",
         "Pick the maximum count, then the smallest value achieving it.",
         "Print -1 when the even bucket is empty."],
        explanations=["2 and 4 both appear twice, so 2 wins.", "There are no even values."],
    ))

    add(P(
        "sum-of-unique-elements", "Sum Of Unique Values", "easy", T + ["Arrays"], H,
        "Print the sum of the values of `nums` that appear exactly once. Print `0` if there are none.",
        [p_nums()], OUT_INT,
        lambda nums: sum(v for v, c in Counter(nums).items() if c == 1),
        [([1, 2, 3, 2],), ([1, 1],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count first, then add only the values with count 1.",
         "Add each qualifying value once, not once per occurrence.",
         "An empty selection sums to 0."],
        explanations=["1 + 3 = 4.", "1 appears twice, so nothing is unique."],
    ))

    add(P(
        "check-anagram-of-palindrome", "Can Form Palindrome", "easy", T + ["Strings"], H,
        "Print `YES` if the characters of `s` can be rearranged into a palindrome, else `NO`.",
        [Param("s", STR, "lowercase letters")], OUT_BOOL,
        lambda s: sum(1 for count in Counter(s).values() if count % 2) <= 1,
        [("aabb",), ("abc",)],
        lambda rng: [(word(rng, n, SMALL),) for n in (1, 2, 3, 5, 9, 20, 60, 150)],
        ["1 <= |s| <= 2000", "s contains lowercase English letters only"],
        ["A palindrome allows at most one character with an odd count — the middle one.",
         "Count the characters and tally how many counts are odd.",
         "The answer is YES when that tally is 0 or 1."],
        explanations=["abba is a palindrome.", "All three counts are odd."],
    ))

    add(P(
        "count-distinct-pairs-sum", "Distinct Pair Sums", "medium", T + ["Arrays"], H,
        "Print how many distinct values can be written as the sum of two elements of `nums` at different "
        "positions.",
        [Param("nums", INT_LIST, "at least 2 elements")], OUT_INT,
        lambda nums: len({nums[i] + nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums))}),
        [([1, 2, 3],), ([2, 2],)],
        lambda rng: [(ints(rng, n, 1, 12),) for n in (2, 3, 5, 9, 20, 55, 120)],
        ["2 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Collect every pair sum in a set.",
         "The set's size is the answer.",
         "The double loop is O(n^2) which passes at these limits."],
        explanations=["Sums 3,4,5 give 3 distinct values.", "The only sum is 4."],
    ))

    add(P(
        "top-frequent-words", "Top Frequent Words", "medium", T + ["Strings"], H,
        "Print the `k` most frequent words, one per line, ordered by descending frequency and then "
        "alphabetically.",
        [Param("wordsList", STR_LIST, "the words"), p_int("k", "how many to report")], OUT_STR_LIST,
        lambda wordsList, k: _top_words(wordsList, k),
        [(["i", "love", "code", "i", "love", "you"], 2), (["a"], 1)],
        lambda rng: [(lambda ws: (ws, rng.randint(1, len(set(ws)))))(words(rng, count, 1, 3, SMALL))
                     for count in (1, 2, 5, 12, 35, 90)],
        ["1 <= number of words <= 1000", "1 <= k <= number of distinct words"],
        ["Count word occurrences with a map.",
         "Sort the distinct words by (-count, word) and take the first k.",
         "A heap of size k avoids a full sort.",
         "The tie-break makes the answer unique, so apply it exactly."],
        explanations=["i and love both appear twice; i sorts first.", "The only word."],
    ))

    add(P(
        "count-good-pairs", "Count Equal Pairs", "easy", T + ["Arrays"], H,
        "Count the pairs of positions `(i, j)` with `i < j` and `nums[i] == nums[j]`.",
        [p_nums()], OUT_INT,
        lambda nums: sum(c * (c - 1) // 2 for c in Counter(nums).values()),
        [([1, 2, 3, 1, 1, 3],), ([1, 2],)], g_small(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["A value appearing c times contributes C(c,2) = c(c-1)/2 pairs.",
         "Count occurrences, then sum that formula over the map.",
         "This is O(n) versus the O(n^2) double loop."],
        explanations=["Three pairs of 1s plus one pair of 3s gives 4.", "No two values are equal."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                               if nums[i] == nums[j]),
    ))

    add(P(
        "missing-and-repeating", "Missing And Repeating", "medium", T + ["Arrays"], H,
        "The array `nums` holds `n` values from `1..n` where exactly one value is missing and exactly one "
        "appears twice. Print the repeating value followed by the missing value.",
        [Param("nums", INT_LIST, "n values from 1..n, one missing and one repeated")], OUT_INT_LIST,
        lambda nums: _missing_and_repeating(nums),
        [([1, 3, 3, 4],), ([1, 1],)],
        lambda rng: [(_missing_repeat_case(rng, n),) for n in (2, 3, 4, 8, 16, 45, 120, 250)],
        ["2 <= n <= 2000", "nums holds n values in 1..n with one missing and one repeated"],
        ["A frequency array of size n+1 reveals both values in one pass.",
         "Sum and sum-of-squares equations also determine them in O(1) space.",
         "The expected sum is n(n+1)/2, so the difference is repeat - missing."],
        explanations=["3 repeats and 2 is missing.", "1 repeats and 2 is missing."],
        out_desc="Print `repeating missing`.",
        brute=lambda nums: [next(v for v in nums if nums.count(v) == 2),
                            next(v for v in range(1, len(nums) + 1) if v not in set(nums))],
    ))

    add(P(
        "subarrays-with-equal-distinct", "Subarrays Matching Whole Array Distinct", "medium",
        T + ["Arrays", "Sliding Window"], H,
        "Count the contiguous subarrays of `nums` whose number of distinct values equals the number of "
        "distinct values in the whole array.",
        [p_nums()], OUT_INT, lambda nums: _count_complete_subarrays(nums),
        [([1, 3, 1, 2, 2],), ([5, 5, 5],)],
        lambda rng: [(ints(rng, n, 1, 4),) for n in (1, 2, 4, 9, 20, 55, 140, 260)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Count the whole array's distinct values first.",
         "Slide a window, shrinking from the left while it still holds all of them.",
         "Once minimal for a right edge, every smaller left edge also works.",
         "Add the number of valid left positions for each right edge."],
        explanations=["Four subarrays contain all of {1,2,3}.", "Every subarray has the single value 5."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                               if len(set(nums[i:j])) == len(set(nums))),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _two_sum(nums, target):
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return [seen[complement], index]
        if value not in seen:
            seen[value] = index
    return [-1]


def _two_sum_brute(nums, target):
    best = None
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == target:
                candidate = [i, j]
                if best is None or (candidate[1], candidate[0]) < (best[1], best[0]):
                    best = candidate
                break
    return best if best is not None else [-1]


def _duplicate_within_k(nums, k):
    if k <= 0:
        return False
    window: set[int] = set()
    for index, value in enumerate(nums):
        if index > k:
            window.discard(nums[index - k - 1])
        if value in window:
            return True
        window.add(value)
    return False


def _frequency_lines(nums):
    counts = Counter(nums)
    return [f"{value} {counts[value]}" for value in sorted(counts)]


def _longest_consecutive(nums):
    values = set(nums)
    best = 0
    for value in values:
        if value - 1 in values:
            continue
        length = 1
        current = value
        while current + 1 in values:
            current += 1
            length += 1
        best = max(best, length)
    return best


def _longest_consecutive_brute(nums):
    values = sorted(set(nums))
    best = current = 1
    for index in range(1, len(values)):
        if values[index] == values[index - 1] + 1:
            current += 1
        else:
            current = 1
        best = max(best, current)
    return best


def _first_repeating(nums):
    counts = Counter(nums)
    for value in nums:
        if counts[value] > 1:
            return value
    return -1


def _has_zero_sum(nums):
    seen = {0}
    running = 0
    for value in nums:
        running += value
        if running in seen:
            return True
        seen.add(running)
    return False


def _maybe_shuffle(rng, arr):
    if rng.random() < 0.5:
        copy = list(arr)
        rng.shuffle(copy)
        return copy
    return ints(rng, len(arr), 1, 6)


def _count_pairs_divisible(nums, k):
    buckets = [0] * k
    for value in nums:
        buckets[value % k] += 1
    total = buckets[0] * (buckets[0] - 1) // 2
    for remainder in range(1, k // 2 + 1):
        complement = k - remainder
        if remainder == complement:
            total += buckets[remainder] * (buckets[remainder] - 1) // 2
        else:
            total += buckets[remainder] * buckets[complement]
    return total


def _most_frequent_even(nums):
    counts = Counter(v for v in nums if v % 2 == 0)
    if not counts:
        return -1
    best = max(counts.values())
    return min(value for value, count in counts.items() if count == best)


def _top_words(wordsList, k):
    counts = Counter(wordsList)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [wordItem for wordItem, _ in ordered[:k]]


def _missing_and_repeating(nums):
    n = len(nums)
    counts = [0] * (n + 1)
    for value in nums:
        counts[value] += 1
    repeating = next(v for v in range(1, n + 1) if counts[v] == 2)
    missing = next(v for v in range(1, n + 1) if counts[v] == 0)
    return [repeating, missing]


def _missing_repeat_case(rng, n):
    missing = rng.randint(1, n)
    repeating = rng.choice([v for v in range(1, n + 1) if v != missing])
    values = [v for v in range(1, n + 1) if v != missing] + [repeating]
    rng.shuffle(values)
    return values


def _count_complete_subarrays(nums):
    needed = len(set(nums))
    counts: dict[int, int] = {}
    total = 0
    left = 0
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
        while len(counts) == needed:
            outgoing = nums[left]
            counts[outgoing] -= 1
            if counts[outgoing] == 0:
                del counts[outgoing]
            left += 1
        total += left
    return total
