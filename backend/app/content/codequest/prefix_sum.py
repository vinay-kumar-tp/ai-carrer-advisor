"""Prefix sums and range queries."""

from __future__ import annotations

import random
from math import gcd

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    PAIR_LIST,
    Param,
    ints,
    p_int,
    p_nums,
)

T = ["Prefix Sum"]
PS = ["Prefix Sum"]


def g_queries(op_lo=-50, op_hi=50):
    def gen(rng: random.Random):
        cases = []
        for n in (1, 2, 3, 6, 12, 40, 120, 300):
            arr = ints(rng, n, op_lo, op_hi)
            queries = []
            for _ in range(min(8, n + 2)):
                left = rng.randint(0, n - 1)
                right = rng.randint(left, n - 1)
                queries.append((left, right))
            cases.append((arr, queries))
        return cases

    return gen


def _range_problem(slug, title, label, reducer, identity_note, extra_hints, difficulty="easy"):
    """Range queries differ only by the operation folded over the window."""
    return P(
        slug, title, difficulty, T + ["Arrays"], PS,
        f"Answer `m` queries on the array `nums`. Each query gives `l` and `r` (0-based, inclusive) "
        f"and asks for the {label} of `nums[l..r]`. Print one answer per query on a single line, "
        f"space separated.",
        [p_nums(), Param("queries", PAIR_LIST, "each pair is l r")], OUT_INT_LIST,
        lambda nums, queries: [reducer(nums[l:r + 1]) for l, r in queries],
        [([1, 2, 3, 4], [(0, 1), (1, 3)]), ([5], [(0, 0)])],
        g_queries(),
        ["1 <= n <= 2000", "1 <= m <= 2000", "0 <= l <= r < n", "-10^6 <= nums[i] <= 10^6"],
        extra_hints + [identity_note, "Answer every query in the order given."],
        out_desc="Print the answers space separated on one line.",
    )


def specs():
    out: list = []
    add = out.append

    add(_range_problem(
        "range-sum-queries", "Range Sum Queries", "sum", sum,
        "The sum of an empty range never occurs here because l <= r.",
        ["Build a prefix array where pre[i] is the sum of the first i elements.",
         "Then the answer is pre[r+1] - pre[l], which is O(1) per query.",
         "Recomputing each range directly would be O(n) per query."],
    ))

    add(_range_problem(
        "range-min-queries", "Range Minimum Queries", "minimum", min,
        "Prefix sums do not work for minimum — you need a sparse table or segment tree for O(1)/O(log n) queries.",
        ["A direct scan per query is O(n*m) and passes at these limits.",
         "A sparse table answers each query in O(1) after O(n log n) preprocessing.",
         "A segment tree gives O(log n) queries and supports updates."],
        difficulty="medium",
    ))

    add(_range_problem(
        "range-max-queries", "Range Maximum Queries", "maximum", max,
        "Like minimum, maximum is not invertible, so prefix arrays alone are not enough.",
        ["Scan each range directly for a simple O(n*m) solution.",
         "A sparse table or segment tree makes each query fast.",
         "Maximum is idempotent, which is what makes sparse tables valid."],
        difficulty="medium",
    ))

    add(_range_problem(
        "range-xor-queries", "Range XOR Queries", "XOR", lambda values: _fold_xor(values),
        "XOR is its own inverse, so prefix XOR works just like prefix sum.",
        ["Build a prefix XOR array.",
         "The answer is pre[r+1] ^ pre[l] because repeated terms cancel.",
         "This gives O(1) per query."],
    ))

    add(_range_problem(
        "range-gcd-queries", "Range GCD Queries", "greatest common divisor",
        lambda values: _fold_gcd(values),
        "GCD is not invertible, so use a sparse table rather than a prefix array.",
        ["A direct fold per query is O(n log V * m) and passes here.",
         "GCD is associative and idempotent, so a sparse table works.",
         "Fold with gcd(a, b) = gcd(b, a % b)."],
        difficulty="medium",
    ))

    add(P(
        "prefix-sum-array", "Prefix Sum Array", "easy", T + ["Arrays"], PS,
        "Print the prefix sum array of `nums`, where position `i` holds the sum of the first `i+1` "
        "elements.",
        [p_nums()], OUT_INT_LIST, lambda nums: _prefix(nums),
        [([1, 2, 3],), ([-1, 1],)],
        lambda rng: [(ints(rng, n, -50, 50),) for n in (1, 2, 4, 9, 25, 80, 200)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Carry a running total.", "Each output is the previous output plus the current element.",
         "This array is the foundation of every range-sum trick."],
    ))

    add(P(
        "subarray-sum-equals-k-count", "Subarrays With Sum K", "medium",
        T + ["Arrays", "Hashing"], PS,
        "Count the contiguous subarrays of `nums` whose elements sum to exactly `k`.",
        [p_nums(), p_int("k", "target sum")], OUT_INT,
        lambda nums, k: _count_subarrays_sum(nums, k),
        [([1, 1, 1], 2), ([1, 2, 3], 7)],
        lambda rng: [(ints(rng, n, -5, 5), rng.randint(-6, 10)) for n in (1, 2, 4, 8, 16, 45, 120, 250)],
        ["1 <= n <= 2000", "-10^4 <= nums[i] <= 10^4", "-10^9 <= k <= 10^9"],
        ["Let pre[i] be the sum of the first i elements; a subarray sums to k when pre[j] - pre[i] = k.",
         "So while scanning, count how many earlier prefix sums equal current - k.",
         "Keep those counts in a hash map, seeded with prefix sum 0 appearing once.",
         "Sliding windows do not work here because negative values break monotonicity."],
        explanations=["The two subarrays [1,1] both sum to 2.", "No subarray sums to 7."],
        brute=lambda nums, k: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                  if sum(nums[i:j]) == k),
        pattern_note="Prefix sums turn 'sum of a range' into 'difference of two prefixes', which lets a "
                     "hash map count matching pairs in one pass.",
    ))

    add(P(
        "subarray-sum-divisible-k", "Subarrays Divisible By K", "medium",
        T + ["Arrays", "Hashing"], PS,
        "Count the contiguous subarrays of `nums` whose sum is divisible by the positive integer `k`.",
        [p_nums(), p_int("k", "the divisor")], OUT_INT,
        lambda nums, k: _count_subarrays_divisible(nums, k),
        [([4, 5, 0, -2, -3, 1], 5), ([1, 2], 7)],
        lambda rng: [(ints(rng, n, -8, 8), rng.randint(1, 7)) for n in (1, 2, 4, 8, 16, 45, 120, 250)],
        ["1 <= n <= 2000", "-10^4 <= nums[i] <= 10^4", "1 <= k <= 10^4"],
        ["A range sum is divisible by k when the two prefix sums share a remainder modulo k.",
         "Count prefix remainders in a hash map or an array of size k.",
         "Seed remainder 0 with a count of 1 for subarrays starting at index 0.",
         "Normalise negative remainders by adding k."],
        explanations=["Seven subarrays have a sum divisible by 5.", "Neither 1, 2 nor 3 is divisible by 7."],
        brute=lambda nums, k: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                  if sum(nums[i:j]) % k == 0),
    ))

    add(P(
        "longest-subarray-sum-k", "Longest Subarray With Sum K", "medium",
        T + ["Arrays", "Hashing"], PS,
        "Print the length of the longest contiguous subarray of `nums` summing to exactly `k`. Print "
        "`0` if none exists.",
        [p_nums(), p_int("k", "target sum")], OUT_INT,
        lambda nums, k: _longest_subarray_sum(nums, k),
        [([1, -1, 5, -2, 3], 3), ([1, 2], 9)],
        lambda rng: [(ints(rng, n, -6, 6), rng.randint(-8, 12)) for n in (1, 2, 4, 9, 18, 45, 120, 250)],
        ["1 <= n <= 2000", "-10^4 <= nums[i] <= 10^4", "-10^9 <= k <= 10^9"],
        ["Store the earliest index at which each prefix sum occurs.",
         "When current - k has been seen, the subarray between the two positions sums to k.",
         "Only record the first occurrence of a prefix sum so the window stays as long as possible.",
         "Seed prefix sum 0 at index -1."],
        explanations=["[1,-1,5,-2] has length 4.", "No subarray sums to 9."],
        brute=lambda nums, k: max([0] + [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                         if sum(nums[i:j]) == k]),
    ))

    add(P(
        "count-zero-sum-subarrays", "Zero Sum Subarrays", "medium", T + ["Arrays", "Hashing"], PS,
        "Count the contiguous subarrays of `nums` whose elements sum to `0`.",
        [p_nums()], OUT_INT, lambda nums: _count_subarrays_sum(nums, 0),
        [([1, -1, 2, -2],), ([1, 2],)],
        lambda rng: [(ints(rng, n, -4, 4),) for n in (1, 2, 4, 8, 16, 45, 120, 250)],
        ["1 <= n <= 2000", "-10^4 <= nums[i] <= 10^4"],
        ["This is the sum-equals-k problem with k = 0.",
         "Two equal prefix sums bracket a zero-sum subarray.",
         "Count repeated prefix sums with a hash map, seeding 0 with count 1."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                               if sum(nums[i:j]) == 0),
    ))

    add(P(
        "equal-zero-one-subarray", "Longest Balanced Binary Subarray", "medium",
        T + ["Arrays", "Hashing"], PS,
        "Given a binary array `nums`, print the length of the longest contiguous subarray containing "
        "equally many `0`s and `1`s.",
        [Param("nums", INT_LIST, "each value is 0 or 1")], OUT_INT,
        lambda nums: _longest_subarray_sum([1 if v else -1 for v in nums], 0),
        [([0, 1, 0],), ([1, 1],)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)],) for n in (1, 2, 4, 9, 20, 50, 140, 300)],
        ["1 <= n <= 2000", "nums[i] is 0 or 1"],
        ["Replace every 0 with -1 so a balanced subarray becomes a zero-sum subarray.",
         "Then find the longest zero-sum subarray with prefix sums.",
         "Record the earliest index of each prefix sum.",
         "The answer is always even."],
        explanations=["[0,1] or [1,0] gives 2.", "There are no zeros."],
        brute=lambda nums: max([0] + [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                      if nums[i:j].count(0) == nums[i:j].count(1)]),
    ))

    add(P(
        "difference-array-updates", "Range Increment Updates", "medium", T + ["Arrays"], PS,
        "Start with an array of `n` zeros. Each update adds `1` to every position in the inclusive "
        "range `[l, r]`. Print the final array after applying all updates.",
        [p_int("n", "array length"), Param("updates", PAIR_LIST, "each pair is l r")], OUT_INT_LIST,
        lambda n, updates: _apply_range_updates(n, updates),
        [(5, [(0, 2), (1, 4)]), (1, [(0, 0)])],
        lambda rng: [(lambda n: (n, [(lambda l: (l, rng.randint(l, n - 1)))(rng.randint(0, n - 1))
                                     for _ in range(min(10, n + 2))]))(n)
                     for n in (1, 2, 3, 6, 12, 40, 120, 300)],
        ["1 <= n <= 2000", "1 <= number of updates <= 2000", "0 <= l <= r < n"],
        ["Applying each update directly is O(n) per update.",
         "A difference array records +1 at l and -1 at r+1 in O(1) per update.",
         "A prefix sum over the difference array reconstructs the final values.",
         "Guard the r+1 index when r is the last position."],
        explanations=["Counts become 1,2,2,1,1.", "The single cell is incremented once."],
        brute=lambda n, updates: _apply_range_updates_brute(n, updates),
    ))

    add(P(
        "max-average-subarray-k", "Maximum Average Subarray", "easy",
        T + ["Arrays", "Sliding Window"], ["Sliding Window"],
        "Print the largest sum of any contiguous subarray of `nums` of exactly length `k`.",
        [p_nums(), p_int("k", "window length")], OUT_INT,
        lambda nums, k: max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1)),
        [([1, 12, -5, -6, 50, 3], 4), ([5], 1)],
        lambda rng: [(lambda n: (ints(rng, n, -30, 30), rng.randint(1, n)))(n)
                     for n in (1, 2, 3, 6, 12, 40, 120, 300)],
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sum the first k elements, then slide: add the incoming element and drop the outgoing one.",
         "Track the best sum seen.",
         "Recomputing each window from scratch would be O(n*k)."],
        explanations=["[12,-5,-6,50] sums to 51.", "The only window is [5]."],
    ))

    add(P(
        "pivot-index", "Pivot Index", "easy", T + ["Arrays"], PS,
        "Print the smallest index where the sum of everything strictly to the left equals the sum of "
        "everything strictly to the right. Print `-1` if no such index exists.",
        [p_nums()], OUT_INT, lambda nums: _pivot(nums),
        [([1, 7, 3, 6, 5, 6],), ([1, 2, 3],)],
        lambda rng: [(ints(rng, n, -15, 15),) for n in (1, 2, 3, 6, 12, 40, 120, 250)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Compute the total, then sweep maintaining the left sum.",
         "The right sum equals total - left - current.",
         "Return the first index where the two match.",
         "Empty sides count as 0, so index 0 and index n-1 are valid candidates."],
        explanations=["At index 3 both sides sum to 11.", "No index balances."],
        brute=lambda nums: next((i for i in range(len(nums)) if sum(nums[:i]) == sum(nums[i + 1:])), -1),
    ))

    add(P(
        "count-prefix-positive", "Prefix Sums Positive Count", "easy", T + ["Arrays"], PS,
        "Print how many of the `n` prefix sums of `nums` are strictly positive.",
        [p_nums()], OUT_INT, lambda nums: sum(1 for value in _prefix(nums) if value > 0),
        [([1, -3, 4],), ([-1, -1],)],
        lambda rng: [(ints(rng, n, -20, 20),) for n in (1, 2, 4, 9, 25, 70, 200)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Build the running total and test its sign at each step.",
         "There are exactly n prefix sums, one ending at each index.",
         "No extra array is needed if you count as you go."],
        explanations=["Prefixes 1,-2,2 give two positives.", "Both prefixes are negative."],
    ))

    add(P(
        "can-split-equal-sum-halves", "Split Into Equal Halves", "easy", T + ["Arrays"], PS,
        "Print `YES` if `nums` can be cut at some position into two non-empty parts with equal sums, "
        "else `NO`.",
        [Param("nums", INT_LIST, "at least 2 elements")], OUT_BOOL,
        lambda nums: _can_split(nums),
        [([1, 2, 3],), ([1, 2],)],
        lambda rng: [(ints(rng, n, -10, 10),) for n in (2, 3, 4, 8, 16, 45, 120)],
        ["2 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Compute the total, then sweep the prefix sum.",
         "A valid cut exists when a prefix equals half the total.",
         "Skip the final position — both parts must be non-empty.",
         "An odd total can still split if values are negative, so do not shortcut on parity."],
        explanations=["1+2 equals 3.", "1 does not equal 2."],
        brute=lambda nums: any(sum(nums[:i]) == sum(nums[i:]) for i in range(1, len(nums))),
    ))

    add(P(
        "count-subarrays-with-average", "Subarrays With Given Average", "medium",
        T + ["Arrays", "Hashing"], PS,
        "Count the contiguous subarrays of `nums` whose average is exactly the integer `target`.",
        [p_nums(), p_int("target", "the required average")], OUT_INT,
        lambda nums, target: _count_subarrays_sum([v - target for v in nums], 0),
        [([1, 3, 2], 2), ([1, 1], 5)],
        lambda rng: [(ints(rng, n, -5, 5), rng.randint(-3, 3)) for n in (1, 2, 4, 9, 18, 45, 120, 250)],
        ["1 <= n <= 2000", "-10^4 <= nums[i], target <= 10^4"],
        ["A subarray of length L averages target exactly when its sum is L * target.",
         "Subtract target from every element; then you need zero-sum subarrays.",
         "Count equal prefix sums with a hash map."],
        explanations=["[1,3,2] and [3,2]... the subarrays averaging 2 are [1,3,2] and [2].",
                      "No subarray averages 5."],
        brute=lambda nums, target: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
                                       if sum(nums[i:j]) == (j - i) * target),
    ))

    add(P(
        "product-prefix-array", "Prefix Product Array", "easy", T + ["Arrays"], PS,
        "Print the prefix products of `nums`, where position `i` holds the product of the first `i+1` "
        "elements.",
        [p_nums()], OUT_INT_LIST, lambda nums: _prefix_product(nums),
        [([1, 2, 3, 4],), ([2, 0, 5],)],
        lambda rng: [(ints(rng, n, -4, 4),) for n in (1, 2, 3, 5, 9, 15, 25)],
        ["1 <= n <= 30", "-9 <= nums[i] <= 9", "the values fit in a 64-bit signed integer"],
        ["Carry a running product starting at 1.",
         "Each output is the previous output times the current element.",
         "Once a zero appears every later prefix product is 0."],
        explanations=["1,2,6,24.", "2,0,0."],
    ))

    add(P(
        "sum-of-all-subarray-sums", "Sum Of All Subarray Sums", "medium", T + ["Arrays"], PS,
        "Print the total of the sums of every contiguous subarray of `nums`.",
        [p_nums()], OUT_INT, lambda nums: _total_subarray_sums(nums),
        [([1, 2, 3],), ([5],)],
        lambda rng: [(ints(rng, n, -20, 20),) for n in (1, 2, 3, 6, 12, 40, 120, 250)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Count how many subarrays contain each index instead of enumerating subarrays.",
         "Index i appears in (i+1) * (n-i) subarrays.",
         "So the answer is the sum of nums[i] * (i+1) * (n-i), computed in O(n).",
         "The brute force is O(n^2) or worse."],
        explanations=["Subarray sums 1,2,3,3,5,6 total 20.", "Only [5] exists."],
        brute=lambda nums: sum(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _fold_xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def _fold_gcd(values):
    result = 0
    for value in values:
        result = gcd(result, abs(value))
    return result


def _prefix(nums):
    result = []
    running = 0
    for value in nums:
        running += value
        result.append(running)
    return result


def _prefix_product(nums):
    result = []
    running = 1
    for value in nums:
        running *= value
        result.append(running)
    return result


def _count_subarrays_sum(nums, k):
    counts = {0: 1}
    running = 0
    total = 0
    for value in nums:
        running += value
        total += counts.get(running - k, 0)
        counts[running] = counts.get(running, 0) + 1
    return total


def _count_subarrays_divisible(nums, k):
    counts = {0: 1}
    running = 0
    total = 0
    for value in nums:
        running = (running + value) % k
        total += counts.get(running, 0)
        counts[running] = counts.get(running, 0) + 1
    return total


def _longest_subarray_sum(nums, k):
    first_seen = {0: -1}
    running = 0
    best = 0
    for index, value in enumerate(nums):
        running += value
        if running - k in first_seen:
            best = max(best, index - first_seen[running - k])
        if running not in first_seen:
            first_seen[running] = index
    return best


def _apply_range_updates(n, updates):
    diff = [0] * (n + 1)
    for left, right in updates:
        diff[left] += 1
        diff[right + 1] -= 1
    result = []
    running = 0
    for index in range(n):
        running += diff[index]
        result.append(running)
    return result


def _apply_range_updates_brute(n, updates):
    values = [0] * n
    for left, right in updates:
        for index in range(left, right + 1):
            values[index] += 1
    return values


def _pivot(nums):
    total = sum(nums)
    left = 0
    for index, value in enumerate(nums):
        if left == total - left - value:
            return index
        left += value
    return -1


def _can_split(nums):
    total = sum(nums)
    left = 0
    for index in range(len(nums) - 1):
        left += nums[index]
        if left == total - left:
            return True
    return False


def _total_subarray_sums(nums):
    n = len(nums)
    return sum(value * (index + 1) * (n - index) for index, value in enumerate(nums))
