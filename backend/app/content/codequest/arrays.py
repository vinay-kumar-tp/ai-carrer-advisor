"""Array fundamentals, traversal and in-place rearrangement problems."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    INT,
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    P,
    Param,
    ints,
    p_int,
    p_nums,
)

T = ["Arrays"]
SIM = ["Simulation"]
TWO = ["Two Pointers"]
SORT = ["Sorting"]
HASH = ["Hashing / Frequency"]

C_SMALL = ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"]


def g_nums(lo=-100, hi=100, sizes=(1, 2, 3, 5, 8, 12, 30, 80, 200)):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def g_nums_pos(lo=1, hi=100, sizes=(1, 2, 3, 5, 9, 15, 40, 120)):
    return g_nums(lo, hi, sizes)


def g_nums_k(lo=-100, hi=100, sizes=(1, 2, 4, 7, 11, 25, 60, 150)):
    def gen(rng: random.Random):
        out = []
        for n in sizes:
            arr = ints(rng, n, lo, hi)
            out.append((arr, rng.randint(1, n)))
        return out

    return gen


def specs():
    out: list = []
    add = out.append

    # ── Traversal / aggregate basics ──────────────────────────────
    add(P(
        "array-sum", "Array Sum", "easy", T, SIM,
        "Given an integer array `nums`, print the sum of all its elements.",
        [p_nums()], OUT_INT, lambda nums: sum(nums),
        [([1, 2, 3, 4],), ([-5, 5],)], g_nums(),
        C_SMALL, ["Keep a running total as you scan.", "Initialise the total to 0, never to nums[0].",
                  "One pass is enough — O(n) time, O(1) extra space."],
        explanations=["1 + 2 + 3 + 4 = 10.", "-5 + 5 = 0."],
        out_desc="Print the total.",
    ))

    add(P(
        "array-maximum", "Array Maximum", "easy", T, SIM,
        "Given an integer array `nums`, print the largest element.",
        [p_nums()], OUT_INT, lambda nums: max(nums),
        [([3, 9, 2, 9, 1],), ([-7],)], g_nums(),
        C_SMALL, ["Track the best value seen so far.",
                  "Start the answer at nums[0], not 0 — the array may be all negative.",
                  "Compare each element against the running maximum."],
        explanations=["9 is the largest value.", "A single element is trivially the maximum."],
    ))

    add(P(
        "array-minimum", "Array Minimum", "easy", T, SIM,
        "Given an integer array `nums`, print the smallest element.",
        [p_nums()], OUT_INT, lambda nums: min(nums),
        [([3, 9, 2, 9, 1],), ([-4, -9, -1],)], g_nums(),
        C_SMALL, ["Mirror of finding the maximum.", "Initialise from nums[0].",
                  "A single pass suffices."],
    ))

    add(P(
        "second-largest-element", "Second Largest Element", "easy", T, SIM,
        "Given an integer array `nums`, print the second largest **distinct** value. "
        "If fewer than two distinct values exist, print `-1`.",
        [p_nums()], OUT_INT,
        lambda nums: (sorted(set(nums), reverse=True) + [None])[1] if len(set(nums)) >= 2 else -1,
        [([3, 9, 2, 9, 1],), ([5, 5, 5],)], g_nums(-20, 20),
        C_SMALL,
        ["Duplicates of the maximum do not count as second largest.",
         "Track the best and the second best in one pass, skipping values equal to the best.",
         "Alternatively deduplicate, sort descending and take index 1.",
         "Remember the -1 case when everything is equal."],
        explanations=["Distinct values are {1,2,3,9}; the second largest is 3.",
                      "Only one distinct value exists, so print -1."],
    ))

    add(P(
        "second-smallest-element", "Second Smallest Element", "easy", T, SIM,
        "Given an integer array `nums`, print the second smallest **distinct** value. "
        "If fewer than two distinct values exist, print `-1`.",
        [p_nums()], OUT_INT,
        lambda nums: sorted(set(nums))[1] if len(set(nums)) >= 2 else -1,
        [([4, 1, 7, 1],), ([2, 2],)], g_nums(-20, 20),
        C_SMALL, ["Deduplicate first, then look at the second position.",
                  "Or track the two smallest distinct values in one pass.",
                  "Print -1 when all elements are identical."],
    ))

    add(P(
        "count-even-odd", "Count Even And Odd", "easy", T, SIM,
        "Given an integer array `nums`, print two integers: the count of even elements "
        "followed by the count of odd elements.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [sum(1 for x in nums if x % 2 == 0), sum(1 for x in nums if x % 2 != 0)],
        [([1, 2, 3, 4, 5],), ([-2, -3],)], g_nums(),
        C_SMALL, ["Use the remainder when divided by 2.",
                  "For negative numbers, `x % 2 == 0` still identifies evens correctly in most languages; "
                  "checking `abs(x) % 2` is always safe.",
                  "The two counts must sum to n."],
        explanations=["Evens {2,4} and odds {1,3,5}.", "-2 is even, -3 is odd."],
        out_desc="Print `evenCount oddCount`.",
    ))

    add(P(
        "sum-of-even-numbers", "Sum Of Even Numbers", "easy", T, SIM,
        "Given an integer array `nums`, print the sum of its even elements. "
        "If there are no even elements, print `0`.",
        [p_nums()], OUT_INT, lambda nums: sum(x for x in nums if x % 2 == 0),
        [([1, 2, 3, 4],), ([1, 3, 5],)], g_nums(),
        C_SMALL, ["Filter, then add.", "Guard the empty case by starting the sum at 0.",
                  "One pass, O(1) extra space."],
    ))

    add(P(
        "count-positive-negative-zero", "Count Positive Negative Zero", "easy", T, SIM,
        "Given an integer array `nums`, print three integers: the number of positive, negative "
        "and zero elements, in that order.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [sum(1 for x in nums if x > 0), sum(1 for x in nums if x < 0), sum(1 for x in nums if x == 0)],
        [([1, -2, 0, 4, 0],), ([-1, -1],)], g_nums(-5, 5),
        C_SMALL, ["Three counters, one pass.", "Zero belongs to neither the positive nor the negative bucket.",
                  "The three counts must sum to n."],
        out_desc="Print `positive negative zero`.",
    ))

    add(P(
        "array-average", "Array Average", "easy", T, SIM,
        "Given an integer array `nums`, print the average of its elements.",
        [p_nums()], "float", lambda nums: sum(nums) / len(nums),
        [([1, 2, 3, 4],), ([5],)], g_nums(),
        C_SMALL, ["Sum the elements, then divide by n.",
                  "Divide as real numbers — integer division would truncate.",
                  "Print exactly 6 decimal places."],
        explanations=["10 / 4 = 2.5.", "5 / 1 = 5."],
        out_desc="Print the average.",
    ))

    add(P(
        "range-of-array", "Array Range", "easy", T, SIM,
        "Given an integer array `nums`, print the difference between its largest and smallest element.",
        [p_nums()], OUT_INT, lambda nums: max(nums) - min(nums),
        [([4, 1, 9],), ([7, 7],)], g_nums(),
        C_SMALL, ["Find the maximum and the minimum.", "The answer is max - min and is never negative.",
                  "Both extremes can be found in a single pass."],
    ))

    add(P(
        "reverse-array", "Reverse Array", "easy", T, TWO,
        "Given an integer array `nums`, print its elements in reverse order.",
        [p_nums()], OUT_INT_LIST, lambda nums: list(reversed(nums)),
        [([1, 2, 3, 4],), ([9],)], g_nums(),
        C_SMALL, ["Swap the first element with the last, the second with the second-to-last, and so on.",
                  "Stop when the two pointers meet in the middle.",
                  "This needs no extra array — O(1) space."],
    ))

    add(P(
        "rotate-array-left", "Rotate Array Left", "easy", T, SIM,
        "Given an integer array `nums` and an integer `k`, rotate the array left by `k` positions "
        "and print the result. Rotating left by 1 moves `nums[0]` to the end.",
        [p_nums(), p_int("k", "number of positions to rotate")], OUT_INT_LIST,
        lambda nums, k: nums[k % len(nums):] + nums[:k % len(nums)],
        [([1, 2, 3, 4, 5], 2), ([1, 2, 3], 3)],
        lambda rng: [(ints(rng, n, -50, 50), rng.randint(0, 2 * n)) for n in (1, 2, 3, 6, 10, 25, 60, 140)],
        ["1 <= n <= 2000", "0 <= k <= 2n", "-10^6 <= nums[i] <= 10^6"],
        ["Reduce k modulo n first — rotating by n changes nothing.",
         "The answer is the suffix starting at index k followed by the prefix before it.",
         "A three-reversal trick does this in O(1) extra space.",
         "Handle k = 0 and k = n as no-ops."],
        explanations=["Moving 1 and 2 to the back gives [3,4,5,1,2].",
                      "k equals n, so the array is unchanged."],
    ))

    add(P(
        "rotate-array-right", "Rotate Array Right", "easy", T, SIM,
        "Given an integer array `nums` and an integer `k`, rotate the array right by `k` positions "
        "and print the result. Rotating right by 1 moves the last element to the front.",
        [p_nums(), p_int("k", "number of positions to rotate")], OUT_INT_LIST,
        lambda nums, k: (lambda s: nums[len(nums) - s:] + nums[:len(nums) - s])(k % len(nums)),
        [([1, 2, 3, 4, 5], 2), ([1, 2], 0)],
        lambda rng: [(ints(rng, n, -50, 50), rng.randint(0, 2 * n)) for n in (1, 2, 3, 6, 10, 25, 60, 140)],
        ["1 <= n <= 2000", "0 <= k <= 2n", "-10^6 <= nums[i] <= 10^6"],
        ["A right rotation by k equals a left rotation by n - k.",
         "Reduce k modulo n before anything else.",
         "Watch the k = 0 case so you do not shift by n."],
        explanations=["[4,5] moves to the front giving [4,5,1,2,3].", "k = 0 leaves the array as is."],
    ))

    add(P(
        "move-zeroes", "Move Zeroes", "easy", T, TWO,
        "Given an integer array `nums`, move every `0` to the end while keeping the relative order "
        "of the non-zero elements. Print the resulting array.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [x for x in nums if x != 0] + [0] * nums.count(0),
        [([0, 1, 0, 3, 12],), ([0, 0],)],
        lambda rng: [([rng.choice([0, 0, rng.randint(-9, 9)]) for _ in range(n)],)
                     for n in (1, 2, 4, 7, 12, 30, 90, 200)],
        C_SMALL,
        ["Keep a write pointer for the next non-zero slot.",
         "Copy every non-zero element forward, then fill the tail with zeros.",
         "Relative order of the non-zero values must not change, so do not sort or swap blindly.",
         "One pass, O(1) extra space."],
        explanations=["Non-zero order 1,3,12 is preserved, then two zeros follow.",
                      "All elements are zero, so nothing moves."],
    ))

    add(P(
        "remove-duplicates-sorted", "Remove Duplicates From Sorted Array", "easy", T, TWO,
        "Given a **sorted** integer array `nums`, remove duplicates so each value appears once, "
        "keeping the sorted order. Print the resulting array.",
        [Param("nums", INT_LIST, "sorted non-decreasing")], OUT_INT_LIST,
        lambda nums: sorted(set(nums)),
        [([1, 1, 2, 2, 3],), ([4],)],
        lambda rng: [(sorted(ints(rng, n, 1, max(2, n // 2))),) for n in (1, 2, 3, 6, 10, 25, 70, 160)],
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order", "-10^6 <= nums[i] <= 10^6"],
        ["Because the array is sorted, duplicates are adjacent.",
         "Compare each element with the previous kept one.",
         "A write pointer lets you do this in place in O(n)."],
    ))

    add(P(
        "remove-element", "Remove All Occurrences", "easy", T, TWO,
        "Given an integer array `nums` and an integer `val`, remove every occurrence of `val` and "
        "print the remaining elements in their original order. Print an empty line if nothing remains.",
        [p_nums(), p_int("val", "value to remove")], OUT_INT_LIST,
        lambda nums, val: [x for x in nums if x != val],
        [([3, 2, 2, 3], 3), ([1, 1], 1)],
        lambda rng: [(ints(rng, n, 1, 6), rng.randint(1, 6)) for n in (1, 2, 4, 8, 15, 40, 100, 200)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], val <= 10^6"],
        ["Use a write pointer that only advances when you keep an element.",
         "Order of the kept elements must be preserved.",
         "Printing nothing is the correct output when every element is removed."],
        explanations=["Removing both 3s leaves [2,2].", "Everything is removed, so the output line is empty."],
    ))

    add(P(
        "linear-search", "Linear Search", "easy", T + ["Sorting & Searching"], SIM,
        "Given an integer array `nums` and an integer `target`, print the index of the **first** "
        "occurrence of `target` (0-based), or `-1` if it is absent.",
        [p_nums(), p_int("target", "value to find")], OUT_INT,
        lambda nums, target: nums.index(target) if target in nums else -1,
        [([4, 7, 1, 7], 7), ([1, 2], 5)],
        lambda rng: [(ints(rng, n, 1, 10), rng.randint(1, 12)) for n in (1, 2, 4, 9, 20, 50, 120, 200)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["Scan left to right and stop at the first match.",
         "Return immediately so you report the first index, not the last.",
         "Print -1 when the loop finishes without a match."],
        explanations=["The first 7 sits at index 1.", "5 is not present."],
    ))

    add(P(
        "count-occurrences", "Count Occurrences", "easy", T + ["Hashing"], HASH,
        "Given an integer array `nums` and an integer `target`, print how many times `target` occurs.",
        [p_nums(), p_int("target")], OUT_INT, lambda nums, target: nums.count(target),
        [([1, 2, 2, 3, 2], 2), ([5], 9)],
        lambda rng: [(ints(rng, n, 1, 8), rng.randint(1, 8)) for n in (1, 3, 6, 12, 25, 60, 150)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["A single counter is enough.", "Do not stop at the first match — count all of them.",
         "Print 0 when the value never appears."],
    ))

    add(P(
        "sum-of-array-except-self-index", "Sum Except Current Index", "easy", T + ["Prefix Sum"], ["Prefix Sum"],
        "Given an integer array `nums`, print an array where position `i` holds the sum of every "
        "element except `nums[i]`.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [sum(nums) - x for x in nums],
        [([1, 2, 3, 4],), ([5, 5],)], g_nums(-50, 50),
        C_SMALL, ["Compute the total once.", "Each answer is total - nums[i].",
                  "This avoids the O(n^2) nested loop."],
        explanations=["Total 10 gives [9,8,7,6].", "Total 10 gives [5,5]."],
    ))

    add(P(
        "product-except-self", "Product Except Self", "medium", T + ["Prefix Sum"], ["Prefix Sum"],
        "Given an integer array `nums`, print an array where position `i` holds the product of all "
        "elements except `nums[i]`. Solve it without using division.",
        [p_nums()], OUT_INT_LIST, _product_except_self,
        [([1, 2, 3, 4],), ([2, 0, 3],)],
        lambda rng: [(ints(rng, n, -6, 6),) for n in (1, 2, 3, 5, 8, 14, 30, 60)],
        ["1 <= n <= 2000", "-9 <= nums[i] <= 9", "The answer fits in a 64-bit signed integer"],
        ["Build prefix products from the left and suffix products from the right.",
         "answer[i] = prefix[i] * suffix[i], where prefix[0] = suffix[n-1] = 1.",
         "Zeros are handled automatically by this approach — no special cases.",
         "Two passes, O(n) time."],
        explanations=["Products are 24, 12, 8, 6.", "The single 0 makes every other position 0."],
        brute=lambda nums: [_prod_without(nums, i) for i in range(len(nums))],
    ))

    add(P(
        "running-sum", "Running Sum", "easy", T + ["Prefix Sum"], ["Prefix Sum"],
        "Given an integer array `nums`, print its running sums: position `i` holds "
        "`nums[0] + ... + nums[i]`.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [sum(nums[:i + 1]) for i in range(len(nums))],
        [([1, 2, 3, 4],), ([-1, 1],)], g_nums(),
        C_SMALL, ["Carry a running total while you walk the array.",
                  "Each output equals the previous output plus the current element.",
                  "The last value equals the sum of the whole array."],
    ))

    add(P(
        "max-consecutive-ones", "Max Consecutive Ones", "easy", T, SIM,
        "Given a binary array `nums` containing only `0` and `1`, print the length of the longest "
        "run of consecutive `1`s.",
        [Param("nums", INT_LIST, "each value is 0 or 1")], OUT_INT,
        lambda nums: max((len(run) for run in "".join(map(str, nums)).split("0")), default=0),
        [([1, 1, 0, 1, 1, 1],), ([0, 0],)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)],) for n in (1, 2, 5, 10, 25, 60, 150, 300)],
        ["1 <= n <= 2000", "nums[i] is 0 or 1"],
        ["Keep a current run length and a best run length.",
         "Reset the current length to 0 whenever you see a 0.",
         "Update the best value after every increment, not only at the end."],
        explanations=["The run 1,1,1 at the end has length 3.", "There are no ones, so the answer is 0."],
    ))

    add(P(
        "longest-equal-run", "Longest Equal Run", "easy", T, SIM,
        "Given an integer array `nums`, print the length of the longest run of consecutive equal values.",
        [p_nums()], OUT_INT, lambda nums: _longest_equal_run(nums),
        [([1, 2, 2, 2, 3],), ([4],)],
        lambda rng: [(ints(rng, n, 1, 3),) for n in (1, 2, 5, 9, 20, 50, 120)],
        C_SMALL, ["Compare each element with its predecessor.",
                  "Extend the run when they match, otherwise restart at 1.",
                  "The answer is at least 1 for a non-empty array."],
    ))

    add(P(
        "is-sorted-ascending", "Is Array Sorted", "easy", T, SIM,
        "Given an integer array `nums`, print `YES` if it is sorted in non-decreasing order, "
        "otherwise print `NO`.",
        [p_nums()], OUT_BOOL,
        lambda nums: all(nums[i] <= nums[i + 1] for i in range(len(nums) - 1)),
        [([1, 2, 2, 5],), ([3, 1],)],
        lambda rng: [((sorted(ints(rng, n, -20, 20)) if rng.random() < 0.5 else ints(rng, n, -20, 20)),)
                     for n in (1, 2, 3, 6, 12, 30, 80)],
        C_SMALL, ["Check every adjacent pair.", "Equal neighbours are allowed in non-decreasing order.",
                  "A single element is always sorted."],
    ))

    add(P(
        "count-inversions-pairs", "Count Descending Pairs", "medium", T + ["Sorting & Searching"], SORT,
        "Given an integer array `nums`, count the pairs of indices `(i, j)` with `i < j` and "
        "`nums[i] > nums[j]`.",
        [p_nums()], OUT_INT, lambda nums: _count_inversions(nums),
        [([2, 1, 3],), ([3, 2, 1],)],
        lambda rng: [(ints(rng, n, -30, 30),) for n in (1, 2, 4, 8, 16, 40, 120, 300)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6", "The answer fits in a 64-bit signed integer"],
        ["The brute force is a double loop — correct but O(n^2).",
         "Merge sort counts these pairs while merging: when you take from the right half, "
         "every remaining element in the left half forms a pair.",
         "A Binary Indexed Tree over compressed values also works.",
         "The maximum possible answer is n(n-1)/2."],
        explanations=["Only (2,1) is descending.", "All three pairs are descending."],
        brute=lambda nums: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > nums[j]),
    ))

    add(P(
        "leaders-in-array", "Leaders In Array", "easy", T, SIM,
        "An element is a **leader** if it is strictly greater than every element to its right. "
        "The last element is always a leader. Print all leaders in their original left-to-right order.",
        [p_nums()], OUT_INT_LIST, lambda nums: _leaders(nums),
        [([16, 17, 4, 3, 5, 2],), ([1, 2, 3],)], g_nums(-30, 30),
        C_SMALL, ["Scanning right to left lets you track the maximum suffix value.",
                  "An element is a leader when it beats that running maximum.",
                  "Collect leaders while scanning backwards, then reverse to restore the original order."],
        explanations=["17, 5 and 2 each beat everything on their right.",
                      "Only the last element qualifies here."],
        brute=lambda nums: [nums[i] for i in range(len(nums)) if all(nums[i] > nums[j] for j in range(i + 1, len(nums)))],
    ))

    add(P(
        "equilibrium-index", "Equilibrium Index", "easy", T + ["Prefix Sum"], ["Prefix Sum"],
        "Print the smallest index `i` where the sum of elements strictly before `i` equals the sum "
        "of elements strictly after `i`. Print `-1` if no such index exists.",
        [p_nums()], OUT_INT, lambda nums: _equilibrium(nums),
        [([-7, 1, 5, 2, -4, 3, 0],), ([1, 2, 3],)], g_nums(-15, 15),
        C_SMALL, ["Compute the total sum first.",
                  "Walk left to right maintaining the prefix sum before i; the right sum is total - prefix - nums[i].",
                  "Compare the two and return the first index that matches.",
                  "Both edge indices are valid candidates (empty side sums to 0)."],
        explanations=["At index 3 the left sum is -1 and the right sum is -1.",
                      "No index balances the two sides."],
        brute=lambda nums: next((i for i in range(len(nums)) if sum(nums[:i]) == sum(nums[i + 1:])), -1),
    ))

    add(P(
        "majority-element-strict", "Majority Element", "easy", T + ["Hashing"], HASH,
        "An element is the majority if it appears **more than** `n/2` times. Print the majority "
        "element, or `-1` if there is none.",
        [p_nums()], OUT_INT, lambda nums: _majority(nums),
        [([3, 3, 4, 2, 3, 3],), ([1, 2],)],
        lambda rng: [(_maybe_majority(rng, n),) for n in (1, 2, 3, 5, 9, 20, 51, 120)],
        C_SMALL, ["A frequency map gives an O(n) time, O(n) space answer.",
                  "Boyer-Moore voting finds a candidate in O(1) space: keep a candidate and a count.",
                  "The voting candidate must be verified with a second pass — it is only a candidate.",
                  "Strictly more than n/2, so 2 out of 4 does not qualify."],
        explanations=["3 appears 4 times out of 6, which is more than 3.",
                      "Neither value exceeds half the length."],
        brute=lambda nums: next((x for x in set(nums) if nums.count(x) * 2 > len(nums)), -1),
    ))

    add(P(
        "find-missing-number", "Missing Number", "easy", T + ["Math"], ["Math & Number Theory"],
        "The array `nums` contains `n` distinct integers taken from `0..n`, so exactly one value is "
        "missing. Print the missing value.",
        [Param("nums", INT_LIST, "n distinct values from 0..n")], OUT_INT,
        lambda nums: len(nums) * (len(nums) + 1) // 2 - sum(nums),
        [([3, 0, 1],), ([0],)],
        lambda rng: [(_missing_case(rng, n),) for n in (1, 2, 3, 5, 10, 30, 90, 200)],
        ["1 <= n <= 2000", "nums holds n distinct values in the range 0..n"],
        ["The numbers 0..n sum to n(n+1)/2.",
         "Subtract the actual sum from the expected sum.",
         "XOR-ing all indices and values also cancels every present number.",
         "Both approaches run in O(n) time and O(1) space."],
        explanations=["0..3 minus {3,0,1} leaves 2.", "0..1 minus {0} leaves 1."],
        brute=lambda nums: next(v for v in range(len(nums) + 1) if v not in set(nums)),
    ))

    add(P(
        "find-duplicate-number", "Find The Duplicate", "medium", T + ["Hashing"], HASH,
        "The array `nums` has `n + 1` elements, each in the range `1..n`, and exactly one value is "
        "repeated. Print the repeated value.",
        [Param("nums", INT_LIST, "n+1 values from 1..n with one repeat")], OUT_INT,
        lambda nums: _find_duplicate(nums),
        [([1, 3, 4, 2, 2],), ([1, 1],)],
        lambda rng: [(_dup_case(rng, n),) for n in (1, 2, 3, 6, 12, 30, 80, 200)],
        ["1 <= n <= 2000", "nums has n+1 elements, each in 1..n, exactly one value repeats"],
        ["A frequency array of size n+1 solves it immediately.",
         "Because values are in 1..n, treating the array as a linked list (i -> nums[i]) creates a cycle.",
         "Floyd's tortoise and hare then finds the cycle entrance, which is the duplicate — O(1) space.",
         "Summing and subtracting only works when the duplicate appears exactly twice."],
        brute=lambda nums: next(x for x in nums if nums.count(x) > 1),
    ))

    add(P(
        "single-number-xor", "Single Number", "easy", T + ["Bit Manipulation"], ["Bit Manipulation"],
        "Every element in `nums` appears exactly twice except one, which appears once. Print the "
        "element that appears once.",
        [Param("nums", INT_LIST, "all values paired except one")], OUT_INT,
        lambda nums: _xor_all(nums),
        [([4, 1, 2, 1, 2],), ([7],)],
        lambda rng: [(_single_case(rng, n),) for n in (1, 3, 5, 9, 15, 41, 101)],
        ["n is odd", "1 <= n <= 2001", "1 <= nums[i] <= 10^6"],
        ["XOR of a value with itself is 0, and XOR with 0 leaves a value unchanged.",
         "XOR every element together — the pairs cancel out.",
         "This is O(n) time and O(1) space, beating a hash set."],
        explanations=["4^1^2^1^2 = 4.", "A single element is the answer."],
        brute=lambda nums: next(x for x in nums if nums.count(x) == 1),
    ))

    add(P(
        "wave-sort-array", "Wave Arrangement", "medium", T + ["Sorting & Searching"], SORT,
        "Rearrange the array into a wave: after sorting ascending, swap every adjacent pair so the "
        "result satisfies `a[0] >= a[1] <= a[2] >= a[3] ...`. Print the resulting array.",
        [p_nums()], OUT_INT_LIST, lambda nums: _wave(nums),
        [([1, 2, 3, 4],), ([5, 1],)], g_nums(-20, 20),
        C_SMALL, ["Sort the array ascending first.",
                  "Then swap elements at positions (0,1), (2,3), (4,5) and so on.",
                  "A trailing element with no partner stays where it is.",
                  "This produces one valid wave; the checker expects exactly this construction."],
        explanations=["Sorted [1,2,3,4] becomes [2,1,4,3].", "Sorted [1,5] becomes [5,1]."],
    ))

    add(P(
        "sort-colors-counting", "Sort Binary Array", "easy", T + ["Sorting & Searching"], TWO,
        "Given an array containing only `0`s and `1`s, sort it in non-decreasing order and print it.",
        [Param("nums", INT_LIST, "each value is 0 or 1")], OUT_INT_LIST,
        lambda nums: [0] * nums.count(0) + [1] * nums.count(1),
        [([1, 0, 1, 0, 0],), ([1],)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)],) for n in (1, 2, 5, 11, 26, 60, 150)],
        ["1 <= n <= 2000", "nums[i] is 0 or 1"],
        ["Counting the zeros is enough to rebuild the array.",
         "A two-pointer partition also works in one pass.",
         "No general-purpose sort is needed for two distinct values."],
    ))

    add(P(
        "dutch-national-flag", "Sort Three Colors", "medium", T + ["Sorting & Searching"], TWO,
        "Given an array containing only `0`, `1` and `2`, sort it in non-decreasing order in a single "
        "pass and print it.",
        [Param("nums", INT_LIST, "each value is 0, 1 or 2")], OUT_INT_LIST,
        lambda nums: [0] * nums.count(0) + [1] * nums.count(1) + [2] * nums.count(2),
        [([2, 0, 2, 1, 1, 0],), ([2, 1],)],
        lambda rng: [([rng.randint(0, 2) for _ in range(n)],) for n in (1, 2, 6, 12, 30, 75, 180)],
        ["1 <= n <= 2000", "nums[i] is 0, 1 or 2"],
        ["Counting each of the three values is the simplest correct answer.",
         "The Dutch National Flag algorithm uses low, mid and high pointers for a true single pass.",
         "When you swap with the high pointer, do not advance mid — the swapped-in value is unexamined."],
    ))

    add(P(
        "max-difference-pair", "Maximum Profit Difference", "easy", T, ["Kadane's / Max Subarray"],
        "Given an integer array `nums`, find the maximum value of `nums[j] - nums[i]` where `i < j`. "
        "If no such pair gives a positive value, print `0`.",
        [p_nums()], OUT_INT, lambda nums: _max_diff(nums),
        [([7, 1, 5, 3, 6, 4],), ([7, 6, 4],)], g_nums(-40, 40),
        C_SMALL, ["Track the smallest value seen so far while scanning left to right.",
                  "At each position the best profit is current - minimumSoFar.",
                  "Clamp the answer at 0 for a strictly decreasing array.",
                  "This is the classic single-transaction stock problem."],
        explanations=["Buy at 1 and sell at 6 for a profit of 5.",
                      "Prices only fall, so the answer is 0."],
        brute=lambda nums: max([0] + [nums[j] - nums[i] for i in range(len(nums)) for j in range(i + 1, len(nums))]),
    ))

    add(P(
        "max-subarray-sum", "Maximum Subarray", "easy", T + ["Dynamic Programming"], ["Kadane's / Max Subarray"],
        "Given an integer array `nums`, find the contiguous non-empty subarray with the largest sum "
        "and print that sum.",
        [p_nums()], OUT_INT, lambda nums: _kadane(nums),
        [([-2, 1, -3, 4, -1, 2, 1, -5, 4],), ([-3, -1, -2],)],
        g_nums(-30, 30),
        C_SMALL, ["Kadane's algorithm runs in O(n).",
                  "At each index either extend the previous subarray or start fresh at the current element.",
                  "best = max(best, current) after every step.",
                  "Because the subarray must be non-empty, initialise with nums[0] rather than 0."],
        explanations=["The subarray [4,-1,2,1] sums to 6.",
                      "All values are negative, so the best single element -1 wins."],
        brute=lambda nums: max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
        pattern_note="Kadane's algorithm keeps one number: the best sum of a subarray ending here. "
                     "Extending a negative running sum can never help, so reset to the current element instead.",
    ))

    add(P(
        "max-subarray-product", "Maximum Product Subarray", "medium", T + ["Dynamic Programming"],
        ["Kadane's / Max Subarray"],
        "Given an integer array `nums`, find the contiguous non-empty subarray with the largest "
        "product and print that product.",
        [p_nums()], OUT_INT, lambda nums: _max_product(nums),
        [([2, 3, -2, 4],), ([-2, 0, -1],)],
        lambda rng: [(ints(rng, n, -6, 6),) for n in (1, 2, 3, 5, 9, 15, 30, 60)],
        ["1 <= n <= 2000", "-9 <= nums[i] <= 9", "The answer fits in a 64-bit signed integer"],
        ["A negative number flips the sign, so the smallest product matters too.",
         "Track both the maximum and the minimum product ending at each index.",
         "When the current element is negative, swap the running maximum and minimum before extending.",
         "Zeros reset both running products to the current element."],
        explanations=["[2,3] gives 6.", "The best single element is 0."],
        brute=lambda nums: max(_prod(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
    ))

    add(P(
        "min-subarray-sum", "Minimum Subarray Sum", "easy", T + ["Dynamic Programming"], ["Kadane's / Max Subarray"],
        "Given an integer array `nums`, find the contiguous non-empty subarray with the **smallest** "
        "sum and print that sum.",
        [p_nums()], OUT_INT, lambda nums: -_kadane([-x for x in nums]),
        [([3, -4, 2, -3, -1, 7, -5],), ([1, 2],)], g_nums(-30, 30),
        C_SMALL, ["Negate every element and run the maximum-subarray algorithm.",
                  "Negate the result to get back the minimum sum.",
                  "Or mirror Kadane's directly, keeping a running minimum."],
        brute=lambda nums: min(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
    ))

    add(P(
        "circular-subarray-sum", "Maximum Circular Subarray", "medium", T + ["Dynamic Programming"],
        ["Kadane's / Max Subarray"],
        "The array `nums` is circular, so a subarray may wrap from the end back to the start. Find "
        "the largest sum of a non-empty subarray and print it. No element may be used twice.",
        [p_nums()], OUT_INT, lambda nums: _max_circular(nums),
        [([1, -2, 3, -2],), ([-3, -2, -3],)],
        lambda rng: [(ints(rng, n, -20, 20),) for n in (1, 2, 3, 5, 9, 16, 40, 90)],
        C_SMALL, ["A non-wrapping answer is plain Kadane's.",
                  "A wrapping answer leaves out a contiguous middle block, so it equals total - minimumSubarray.",
                  "Take the maximum of the two cases.",
                  "If every element is negative, the wrapping formula would produce an empty subarray — "
                  "fall back to the plain Kadane's answer."],
        explanations=["The best subarray is [3] with sum 3; wrapping cannot beat it here.",
                      "All values are negative, so the best single element -2 wins."],
        brute=lambda nums: _circular_brute(nums),
    ))

    add(P(
        "rearrange-alternate-signs", "Alternate Positive And Negative", "medium", T, TWO,
        "Given an array with equal counts of positive and negative integers, rearrange it so signs "
        "alternate starting with a positive value, preserving the relative order within the positives "
        "and within the negatives. Print the result.",
        [Param("nums", INT_LIST, "equal number of positive and negative values, no zeros")], OUT_INT_LIST,
        lambda nums: _alternate_signs(nums),
        [([3, 1, -2, -5, 2, -4],), ([1, -1],)],
        lambda rng: [(_signed_case(rng, k),) for k in (1, 2, 3, 5, 8, 20, 50)],
        ["n is even and 2 <= n <= 2000", "nums contains exactly n/2 positive and n/2 negative values",
         "nums[i] != 0"],
        ["Split the array into a positive list and a negative list, keeping order.",
         "Then interleave them, positive first.",
         "Because the counts are equal, neither list runs out early."],
        explanations=["Positives [3,1,2] and negatives [-2,-5,-4] interleave to [3,-2,1,-5,2,-4].",
                      "One of each simply alternates."],
    ))

    add(P(
        "kth-largest-element", "Kth Largest Element", "medium", T + ["Heap", "Sorting & Searching"],
        ["Top-K Elements"],
        "Given an integer array `nums` and an integer `k`, print the `k`-th largest element. "
        "Duplicates count separately, so in `[3,3,1]` the 2nd largest is `3`.",
        [p_nums(), p_int("k", "1-based rank from the largest")], OUT_INT,
        lambda nums, k: sorted(nums, reverse=True)[k - 1],
        [([3, 2, 1, 5, 6, 4], 2), ([3, 3, 1], 2)], g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sorting descending and indexing k-1 is O(n log n) and always correct.",
         "A min-heap of size k gives O(n log k).",
         "Quickselect averages O(n).",
         "Do not deduplicate — ranks count repeated values separately."],
        explanations=["Sorted descending [6,5,4,3,2,1]; the 2nd is 5.",
                      "Sorted descending [3,3,1]; the 2nd is 3."],
    ))

    add(P(
        "kth-smallest-element", "Kth Smallest Element", "medium", T + ["Heap", "Sorting & Searching"],
        ["Top-K Elements"],
        "Given an integer array `nums` and an integer `k`, print the `k`-th smallest element. "
        "Duplicates count separately.",
        [p_nums(), p_int("k", "1-based rank from the smallest")], OUT_INT,
        lambda nums, k: sorted(nums)[k - 1],
        [([7, 10, 4, 3, 20, 15], 3), ([2, 2], 2)], g_nums_k(),
        ["1 <= k <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Sort ascending and take index k-1.",
         "A max-heap of size k keeps memory to O(k).",
         "Quickselect is the linear-average-time option."],
    ))

    add(P(
        "top-k-frequent-elements", "Top K Frequent Elements", "medium",
        T + ["Hashing", "Heap"], ["Top-K Elements"],
        "Given an integer array `nums` and an integer `k`, print the `k` most frequent values. "
        "Order them by descending frequency, breaking ties by the smaller value first.",
        [p_nums(), p_int("k", "how many values to report")], OUT_INT_LIST,
        lambda nums, k: _top_k_frequent(nums, k),
        [([1, 1, 1, 2, 2, 3], 2), ([4, 4, 5, 5], 2)],
        _gen_top_k,
        ["1 <= n <= 2000", "1 <= k <= number of distinct values in nums", "-10^6 <= nums[i] <= 10^6"],
        ["Count frequencies with a hash map.",
         "Sort the distinct values by (-frequency, value) and take the first k.",
         "A heap of size k avoids sorting everything.",
         "The tie-break rule makes the answer unique, so follow it exactly."],
        explanations=["1 appears 3 times, 2 appears twice.", "Both appear twice, so the smaller value 4 comes first."],
    ))

    add(P(
        "frequency-of-most-common", "Highest Frequency Count", "easy", T + ["Hashing"], HASH,
        "Given an integer array `nums`, print how many times the most frequent value appears.",
        [p_nums()], OUT_INT,
        lambda nums: max(nums.count(x) for x in set(nums)),
        [([1, 2, 2, 3, 2],), ([9],)],
        lambda rng: [(ints(rng, n, 1, max(2, n // 2)),) for n in (1, 3, 6, 12, 30, 80, 200)],
        C_SMALL, ["Build a frequency map in one pass.",
                  "The answer is the largest value in that map.",
                  "Counting with `nums.count` inside a loop is O(n^2) — prefer a map."],
    ))

    add(P(
        "array-intersection-sorted", "Array Intersection", "easy", T + ["Hashing"], HASH,
        "Given two integer arrays `a` and `b`, print the distinct values present in both, "
        "in ascending order. Print an empty line if there are none.",
        [Param("a", INT_LIST, "first array"), Param("b", INT_LIST, "second array")], OUT_INT_LIST,
        lambda a, b: sorted(set(a) & set(b)),
        [([1, 2, 2, 1], [2, 2]), ([1, 2], [3, 4])],
        lambda rng: [(ints(rng, n, 1, 12), ints(rng, m, 1, 12))
                     for n, m in ((1, 1), (2, 3), (5, 4), (10, 10), (25, 15), (60, 40))],
        ["1 <= n, m <= 2000", "-10^6 <= values <= 10^6"],
        ["Put one array in a hash set, then filter the other.",
         "Deduplicate the result before printing.",
         "Sort at the end so the output order is deterministic."],
        explanations=["Only 2 is common to both.", "The arrays share nothing, so the line is empty."],
    ))

    add(P(
        "array-union-sorted", "Array Union", "easy", T + ["Hashing"], HASH,
        "Given two integer arrays `a` and `b`, print every distinct value appearing in either array, "
        "in ascending order.",
        [Param("a", INT_LIST, "first array"), Param("b", INT_LIST, "second array")], OUT_INT_LIST,
        lambda a, b: sorted(set(a) | set(b)),
        [([1, 2, 2], [2, 3]), ([5], [5])],
        lambda rng: [(ints(rng, n, 1, 15), ints(rng, m, 1, 15))
                     for n, m in ((1, 1), (2, 3), (6, 4), (12, 12), (30, 20))],
        ["1 <= n, m <= 2000", "-10^6 <= values <= 10^6"],
        ["Insert both arrays into one set.", "Sort the set before printing.",
         "Duplicates within a single array collapse too."],
    ))

    add(P(
        "array-difference", "Array Difference", "easy", T + ["Hashing"], HASH,
        "Given two integer arrays `a` and `b`, print the distinct values that appear in `a` but not "
        "in `b`, in ascending order. Print an empty line if there are none.",
        [Param("a", INT_LIST, "first array"), Param("b", INT_LIST, "second array")], OUT_INT_LIST,
        lambda a, b: sorted(set(a) - set(b)),
        [([1, 2, 3], [2]), ([4], [4])],
        lambda rng: [(ints(rng, n, 1, 12), ints(rng, m, 1, 12))
                     for n, m in ((1, 1), (3, 2), (6, 6), (15, 8), (40, 25))],
        ["1 <= n, m <= 2000", "-10^6 <= values <= 10^6"],
        ["Build a set from b for O(1) membership tests.",
         "Keep values of a that are missing from that set.",
         "Deduplicate and sort the result."],
    ))

    add(P(
        "chunk-array-sums", "Block Sums", "easy", T, SIM,
        "Split `nums` into consecutive blocks of size `k` (the final block may be shorter) and print "
        "the sum of each block in order.",
        [p_nums(), p_int("k", "block size")], OUT_INT_LIST,
        lambda nums, k: [sum(nums[i:i + k]) for i in range(0, len(nums), k)],
        [([1, 2, 3, 4, 5], 2), ([4, 4], 5)],
        lambda rng: [(ints(rng, n, -20, 20), rng.randint(1, max(1, n + 2))) for n in (1, 2, 4, 7, 15, 40, 100)],
        ["1 <= n <= 2000", "1 <= k <= 2000 (k may exceed n)", "-10^6 <= nums[i] <= 10^6"],
        ["Step through the array in strides of k.",
         "Sum each window of up to k elements.",
         "The last block is short when n is not a multiple of k."],
        explanations=["Blocks [1,2], [3,4], [5] sum to 3, 7, 5.",
                      "k exceeds n, so there is one block summing to 8."],
    ))

    add(P(
        "cyclic-sort-missing", "First Missing Positive", "hard", T, ["Cyclic Sort"],
        "Given an integer array `nums`, print the smallest **positive** integer that does not appear "
        "in it.",
        [p_nums()], OUT_INT, lambda nums: _first_missing_positive(nums),
        [([3, 4, -1, 1],), ([1, 2, 3],)],
        lambda rng: [(ints(rng, n, -3, n + 2),) for n in (1, 2, 3, 5, 9, 20, 60, 150)],
        C_SMALL, ["The answer always lies in the range 1..n+1.",
                  "Values outside 1..n can be ignored entirely.",
                  "Place each value v in 1..n at index v-1 by swapping (cyclic sort), then scan for the "
                  "first index whose value is wrong.",
                  "This achieves O(n) time and O(1) extra space."],
        explanations=["1 is present, 2 is not.", "1, 2 and 3 are all present, so the answer is 4."],
        brute=lambda nums: next(v for v in range(1, len(nums) + 2) if v not in set(nums)),
    ))

    add(P(
        "rearrange-index-values", "Rearrange By Index", "easy", T, SIM,
        "The array `nums` is a permutation of `0..n-1`. Print the array `res` where "
        "`res[i] = nums[nums[i]]`.",
        [Param("nums", INT_LIST, "a permutation of 0..n-1")], OUT_INT_LIST,
        lambda nums: [nums[nums[i]] for i in range(len(nums))],
        [([0, 2, 1, 5, 3, 4],), ([0],)],
        lambda rng: [(_permutation(rng, n),) for n in (1, 2, 3, 5, 9, 20, 60, 150)],
        ["1 <= n <= 2000", "nums is a permutation of 0..n-1"],
        ["Read the value at index i, then use it as another index.",
         "Build a fresh output array — overwriting in place loses values you still need.",
         "Every index is valid because the input is a permutation of 0..n-1."],
    ))

    add(P(
        "count-pairs-with-sum", "Count Pairs With Sum", "easy", T + ["Hashing"], HASH,
        "Count the pairs of indices `(i, j)` with `i < j` and `nums[i] + nums[j] == target`.",
        [p_nums(), p_int("target", "required pair sum")], OUT_INT,
        lambda nums, target: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                                 if nums[i] + nums[j] == target),
        [([1, 5, 7, 1], 6), ([1, 1, 1], 2)],
        lambda rng: [(ints(rng, n, 1, 10), rng.randint(2, 20)) for n in (1, 2, 4, 8, 16, 40, 120)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["A hash map of counts lets you answer in O(n).",
         "While scanning, add the number of earlier elements equal to target - nums[i].",
         "Update the map after counting so you never pair an element with itself.",
         "Equal values contribute C(count, 2) pairs."],
        explanations=["Pairs (1,5) and (5,1) using indices (0,1) and (1,3).",
                      "All three pairs of 1s sum to 2."],
    ))

    add(P(
        "max-two-sum-pair", "Largest Pair Sum", "easy", T, SIM,
        "Given an integer array `nums` with at least two elements, print the largest sum obtainable "
        "from two different positions.",
        [Param("nums", INT_LIST, "at least 2 elements")], OUT_INT,
        lambda nums: sum(sorted(nums)[-2:]),
        [([3, 1, 4, 2],), ([-5, -2],)],
        lambda rng: [(ints(rng, n, -50, 50),) for n in (2, 3, 5, 9, 20, 60, 150)],
        ["2 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["The two largest elements always give the largest sum.",
         "Track the top two values in one pass instead of sorting.",
         "Negative arrays still work — pick the two least negative."],
    ))

    add(P(
        "min-two-sum-pair", "Smallest Pair Sum", "easy", T, SIM,
        "Given an integer array `nums` with at least two elements, print the smallest sum obtainable "
        "from two different positions.",
        [Param("nums", INT_LIST, "at least 2 elements")], OUT_INT,
        lambda nums: sum(sorted(nums)[:2]),
        [([3, 1, 4, 2],), ([-5, -2, 7],)],
        lambda rng: [(ints(rng, n, -50, 50),) for n in (2, 3, 5, 9, 20, 60, 150)],
        ["2 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["The two smallest elements give the smallest sum.",
         "Track the bottom two values in a single pass.",
         "Sorting also works and is easier to get right."],
    ))

    add(P(
        "peak-element-index", "Peak Element", "medium", T + ["Binary Search"], ["Modified Binary Search"],
        "An element is a peak if it is strictly greater than both neighbours; out-of-range neighbours "
        "count as negative infinity. Print the index of any peak — the checker accepts the **smallest** "
        "such index.",
        [p_nums()], OUT_INT, lambda nums: _first_peak(nums),
        [([1, 2, 3, 1],), ([5, 4, 3],)],
        lambda rng: [(ints(rng, n, -20, 20),) for n in (1, 2, 3, 5, 9, 20, 60, 140)],
        C_SMALL, ["A linear scan comparing each element with its neighbours is O(n).",
                  "Binary search also works: move toward the larger neighbour and a peak is guaranteed.",
                  "Because we require the smallest index, scan from the left and return the first peak.",
                  "The first or last element can be a peak."],
        explanations=["Index 2 holds 3, greater than 2 and 1.",
                      "Index 0 holds 5, and its missing left neighbour counts as -infinity."],
        brute=lambda nums: next(i for i in range(len(nums))
                                if (i == 0 or nums[i] > nums[i - 1]) and (i == len(nums) - 1 or nums[i] > nums[i + 1])),
    ))

    add(P(
        "count-elements-less-equal", "Count At Most X", "easy", T + ["Binary Search"], ["Binary Search"],
        "Given an integer array `nums` and an integer `x`, print how many elements are less than or "
        "equal to `x`.",
        [p_nums(), p_int("x", "threshold")], OUT_INT,
        lambda nums, x: sum(1 for v in nums if v <= x),
        [([1, 5, 3, 7], 4), ([9, 9], 1)],
        lambda rng: [(ints(rng, n, -30, 30), rng.randint(-30, 30)) for n in (1, 2, 5, 10, 25, 70, 180)],
        C_SMALL, ["A single counting pass is O(n).",
                  "If you sort first, binary search gives the count in O(log n) per query.",
                  "Remember the comparison is <=, not <."],
    ))

    add(P(
        "prefix-max-array", "Prefix Maximum Array", "easy", T + ["Prefix Sum"], ["Prefix Sum"],
        "Print an array where position `i` holds the maximum of `nums[0..i]`.",
        [p_nums()], OUT_INT_LIST, lambda nums: _prefix_max(nums),
        [([1, 3, 2, 5, 4],), ([-2, -5],)], g_nums(),
        C_SMALL, ["Carry a running maximum from left to right.",
                  "Each output is max(previousOutput, nums[i]).",
                  "The result is non-decreasing by construction."],
    ))

    add(P(
        "suffix-min-array", "Suffix Minimum Array", "easy", T + ["Prefix Sum"], ["Prefix Sum"],
        "Print an array where position `i` holds the minimum of `nums[i..n-1]`.",
        [p_nums()], OUT_INT_LIST, lambda nums: _suffix_min(nums),
        [([3, 1, 4, 2],), ([7],)], g_nums(),
        C_SMALL, ["Scan from the right, keeping a running minimum.",
                  "Fill the output array backwards.",
                  "The result is non-increasing when read left to right."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _gen_top_k(rng: random.Random):
    """k must never exceed the number of distinct values, so derive it from the array."""
    cases = []
    for n in (2, 4, 8, 15, 30, 70, 150):
        arr = ints(rng, n, 1, max(2, n // 3))
        cases.append((arr, rng.randint(1, len(set(arr)))))
    cases.append(([1, 2, 3], 3))
    cases.append(([5, 5, 5], 1))
    return cases


def _prod(values):
    result = 1
    for value in values:
        result *= value
    return result


def _prod_without(nums, skip):
    result = 1
    for index, value in enumerate(nums):
        if index != skip:
            result *= value
    return result


def _product_except_self(nums):
    n = len(nums)
    prefix = [1] * n
    for i in range(1, n):
        prefix[i] = prefix[i - 1] * nums[i - 1]
    suffix = 1
    result = [0] * n
    for i in range(n - 1, -1, -1):
        result[i] = prefix[i] * suffix
        suffix *= nums[i]
    return result


def _longest_equal_run(nums):
    best = current = 1
    for i in range(1, len(nums)):
        current = current + 1 if nums[i] == nums[i - 1] else 1
        best = max(best, current)
    return best


def _count_inversions(nums):
    def sort_count(arr):
        if len(arr) <= 1:
            return arr, 0
        mid = len(arr) // 2
        left, a = sort_count(arr[:mid])
        right, b = sort_count(arr[mid:])
        merged = []
        count = a + b
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
                count += len(left) - i
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, count

    return sort_count(list(nums))[1]


def _leaders(nums):
    result = []
    best = None
    for value in reversed(nums):
        if best is None or value > best:
            result.append(value)
            best = value
    return list(reversed(result))


def _equilibrium(nums):
    total = sum(nums)
    left = 0
    for index, value in enumerate(nums):
        if left == total - left - value:
            return index
        left += value
    return -1


def _majority(nums):
    candidate, count = None, 0
    for value in nums:
        if count == 0:
            candidate, count = value, 1
        elif value == candidate:
            count += 1
        else:
            count -= 1
    if candidate is not None and nums.count(candidate) * 2 > len(nums):
        return candidate
    return -1


def _maybe_majority(rng, n):
    if rng.random() < 0.5:
        value = rng.randint(1, 5)
        arr = [value] * (n // 2 + 1) + ints(rng, n - (n // 2 + 1), 6, 9)
        rng.shuffle(arr)
        return arr[:n] if len(arr) >= n else arr + [value] * (n - len(arr))
    return ints(rng, n, 1, 4)


def _missing_case(rng, n):
    missing = rng.randint(0, n)
    values = [v for v in range(n + 1) if v != missing]
    rng.shuffle(values)
    return values


def _find_duplicate(nums):
    seen = set()
    for value in nums:
        if value in seen:
            return value
        seen.add(value)
    return -1


def _dup_case(rng, n):
    values = list(range(1, n + 1))
    values.append(rng.randint(1, n))
    rng.shuffle(values)
    return values


def _xor_all(nums):
    result = 0
    for value in nums:
        result ^= value
    return result


def _single_case(rng, n):
    pairs = (n - 1) // 2
    values = []
    used = set()
    for _ in range(pairs):
        value = rng.randint(1, 500)
        while value in used:
            value = rng.randint(1, 500)
        used.add(value)
        values.extend([value, value])
    lone = rng.randint(501, 1000)
    values.append(lone)
    rng.shuffle(values)
    return values


def _wave(nums):
    arr = sorted(nums)
    for i in range(0, len(arr) - 1, 2):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return arr


def _max_diff(nums):
    best = 0
    lowest = nums[0]
    for value in nums[1:]:
        best = max(best, value - lowest)
        lowest = min(lowest, value)
    return best


def _kadane(nums):
    best = current = nums[0]
    for value in nums[1:]:
        current = max(value, current + value)
        best = max(best, current)
    return best


def _max_product(nums):
    best = high = low = nums[0]
    for value in nums[1:]:
        if value < 0:
            high, low = low, high
        high = max(value, high * value)
        low = min(value, low * value)
        best = max(best, high)
    return best


def _max_circular(nums):
    total = sum(nums)
    best = _kadane(nums)
    worst = -_kadane([-x for x in nums])
    if worst == total:  # every element is in the minimum subarray
        return best
    return max(best, total - worst)


def _circular_brute(nums):
    n = len(nums)
    best = None
    for start in range(n):
        running = 0
        for length in range(1, n + 1):
            running += nums[(start + length - 1) % n]
            best = running if best is None else max(best, running)
    return best


def _alternate_signs(nums):
    positives = [x for x in nums if x > 0]
    negatives = [x for x in nums if x < 0]
    result = []
    for pos, neg in zip(positives, negatives):
        result.extend([pos, neg])
    return result


def _signed_case(rng, k):
    positives = [rng.randint(1, 50) for _ in range(k)]
    negatives = [-rng.randint(1, 50) for _ in range(k)]
    merged = positives + negatives
    rng.shuffle(merged)
    return merged


def _top_k_frequent(nums, k):
    counts: dict[int, int] = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [value for value, _ in ordered[:k]]


def _first_missing_positive(nums):
    present = set(v for v in nums if v > 0)
    candidate = 1
    while candidate in present:
        candidate += 1
    return candidate


def _permutation(rng, n):
    values = list(range(n))
    rng.shuffle(values)
    return values


def _first_peak(nums):
    n = len(nums)
    for i in range(n):
        left_ok = i == 0 or nums[i] > nums[i - 1]
        right_ok = i == n - 1 or nums[i] > nums[i + 1]
        if left_ok and right_ok:
            return i
    return -1


def _prefix_max(nums):
    result = []
    best = nums[0]
    for value in nums:
        best = max(best, value)
        result.append(best)
    return result


def _suffix_min(nums):
    result = [0] * len(nums)
    best = nums[-1]
    for i in range(len(nums) - 1, -1, -1):
        best = min(best, nums[i])
        result[i] = best
    return result
