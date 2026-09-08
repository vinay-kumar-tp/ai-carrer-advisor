"""Two-pointer techniques on arrays and strings."""

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
    p_nums,
    sorted_ints,
    word,
)

T = ["Two Pointers"]
TP = ["Two Pointers"]
SIZES = (2, 3, 4, 7, 12, 30, 90, 220)


def p_sorted(name="nums", desc="sorted in non-decreasing order"):
    return Param(name, INT_LIST, desc)


def g_sorted(lo=-60, hi=60, sizes=SIZES):
    def gen(rng: random.Random):
        return [(sorted_ints(rng, n, lo, hi),) for n in sizes]

    return gen


def g_sorted_target(lo=-30, hi=30, sizes=SIZES):
    def gen(rng: random.Random):
        return [(sorted_ints(rng, n, lo, hi), rng.randint(2 * lo, 2 * hi)) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "two-sum-sorted-indices", "Two Sum In Sorted Array", "easy", T + ["Arrays"], TP,
        "The array `nums` is sorted in non-decreasing order. Find two different positions whose values "
        "sum to `target` and print their 0-based indices in increasing order. Print `-1` if no pair "
        "exists. If several pairs work, print the one with the smallest first index.",
        [p_sorted(), p_int("target", "required pair sum")], OUT_INT_LIST,
        lambda nums, target: _two_sum_sorted(nums, target),
        [([2, 7, 11, 15], 9), ([1, 2], 7)],
        g_sorted_target(),
        ["2 <= n <= 2000", "nums is sorted in non-decreasing order", "-10^6 <= nums[i], target <= 10^6"],
        ["Put one pointer at each end of the array.",
         "If the pair sum is too large move the right pointer left; if too small move the left pointer right.",
         "Sortedness is what makes this O(n) — no hash map needed.",
         "Print -1 on a single line when the pointers cross without a match."],
        explanations=["2 + 7 = 9 at indices 0 and 1.", "No pair sums to 7."],
        out_desc="Print the two indices separated by a space, or -1.",
        brute=lambda nums, target: _two_sum_brute(nums, target),
    ))

    add(P(
        "two-sum-closest", "Closest Pair Sum", "medium", T + ["Arrays"], TP,
        "The array `nums` is sorted. Print the sum of the two elements (at different positions) whose "
        "total is closest to `target`. If two sums tie, print the smaller sum.",
        [p_sorted(), p_int("target")], OUT_INT,
        lambda nums, target: _closest_pair_sum(nums, target),
        [([1, 3, 4, 7, 10], 15), ([1, 2], 100)],
        g_sorted_target(),
        ["2 <= n <= 2000", "nums is sorted in non-decreasing order", "-10^6 <= nums[i], target <= 10^6"],
        ["Walk two pointers inwards from both ends.",
         "Track the best absolute difference seen so far.",
         "Move the pointer that brings the sum closer to the target.",
         "On a tie prefer the smaller sum, so compare before overwriting."],
        explanations=["4 + 10 = 14 is closest to 15.", "The only pair sums to 3."],
        brute=lambda nums, target: min(
            (nums[i] + nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums))),
            key=lambda s: (abs(s - target), s),
        ),
    ))

    add(P(
        "three-sum-exists", "Three Sum Exists", "medium", T + ["Arrays"], TP,
        "Print `YES` if three elements at distinct positions of `nums` sum to `target`, else `NO`.",
        [p_nums(), p_int("target")], OUT_BOOL,
        lambda nums, target: _three_sum_exists(nums, target),
        [([1, 2, 4, 8], 7), ([1, 2], 3)],
        lambda rng: [(ints(rng, n, -20, 20), rng.randint(-30, 30)) for n in (1, 2, 3, 5, 9, 20, 60, 140)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["Sort the array first so two pointers become usable.",
         "Fix the first element, then two-pointer the remaining suffix for the needed pair.",
         "That gives O(n^2) instead of the O(n^3) triple loop.",
         "Answer NO when fewer than three elements exist."],
        explanations=["1 + 2 + 4 = 7.", "Only two elements are available."],
        brute=lambda nums, target: any(
            nums[i] + nums[j] + nums[k] == target
            for i in range(len(nums)) for j in range(i + 1, len(nums)) for k in range(j + 1, len(nums))
        ),
    ))

    add(P(
        "three-sum-closest", "Closest Triple Sum", "medium", T + ["Arrays"], TP,
        "Print the sum of three elements at distinct positions of `nums` that is closest to `target`. "
        "If two sums tie, print the smaller one.",
        [Param("nums", INT_LIST, "at least 3 elements"), p_int("target")], OUT_INT,
        lambda nums, target: _closest_triple(nums, target),
        [([-1, 2, 1, -4], 1), ([1, 1, 1], 10)],
        lambda rng: [(ints(rng, n, -25, 25), rng.randint(-40, 40)) for n in (3, 4, 5, 8, 15, 40, 100)],
        ["3 <= n <= 2000", "-10^6 <= nums[i], target <= 10^6"],
        ["Sort, then fix one index and two-pointer the rest.",
         "Track the closest sum, preferring the smaller value on ties.",
         "Overall O(n^2)."],
        explanations=["-1 + 2 + 1 = 2 is closest to 1.", "The only triple sums to 3."],
        brute=lambda nums, target: min(
            (nums[i] + nums[j] + nums[k]
             for i in range(len(nums)) for j in range(i + 1, len(nums)) for k in range(j + 1, len(nums))),
            key=lambda s: (abs(s - target), s),
        ),
    ))

    add(P(
        "count-pairs-with-difference", "Count Pairs With Difference", "medium", T + ["Arrays"], TP,
        "Count the pairs of positions `(i, j)` with `i < j` and `|nums[i] - nums[j]| == k`.",
        [p_nums(), p_int("k", "the required absolute difference")], OUT_INT,
        lambda nums, k: _count_pairs_diff(nums, k),
        [([1, 5, 3, 4, 2], 2), ([1, 1, 1], 0)],
        lambda rng: [(ints(rng, n, 1, 12), rng.randint(0, 5)) for n in (1, 2, 4, 8, 16, 45, 120)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6", "0 <= k <= 10^6"],
        ["Sorting lets two pointers sweep the array in O(n log n).",
         "A frequency map handles it in O(n): for each value count occurrences of value + k.",
         "k = 0 is special — pairs come from duplicates, contributing count*(count-1)/2.",
         "Do not double count: fix an ordering or halve the total."],
        explanations=["The qualifying pairs are (1,3), (5,3) and (4,2), so 3 in total.",
                      "All three pairs of equal 1s differ by 0."],
        brute=lambda nums, k: sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
                                  if abs(nums[i] - nums[j]) == k),
    ))

    add(P(
        "container-with-most-water", "Container With Most Water", "medium", T + ["Arrays"], TP,
        "Each `heights[i]` is a vertical line at position `i`. Print the largest area of water that can "
        "be held between two lines, where the area is the distance between them times the shorter height.",
        [Param("heights", INT_LIST, "non-negative heights")], OUT_INT,
        lambda heights: _max_water(heights),
        [([1, 8, 6, 2, 5, 4, 8, 3, 7],), ([1, 1],)],
        lambda rng: [(ints(rng, n, 0, 40),) for n in (2, 3, 5, 9, 18, 45, 120, 250)],
        ["2 <= n <= 2000", "0 <= heights[i] <= 10^6"],
        ["Start with the widest pair: one pointer at each end.",
         "The area is limited by the shorter line, so move that pointer inwards.",
         "Moving the taller line could never improve the area at a smaller width.",
         "One pass gives O(n)."],
        explanations=["Lines at indices 1 and 8 hold 7 * 7 = 49.", "Width 1 times height 1."],
        brute=lambda heights: max(min(heights[i], heights[j]) * (j - i)
                                  for i in range(len(heights)) for j in range(i + 1, len(heights))),
    ))

    add(P(
        "trapping-rain-water", "Trapping Rain Water", "hard", T + ["Arrays"], TP,
        "Each `heights[i]` is a bar of width 1. Print the total units of water trapped between the bars "
        "after it rains.",
        [Param("heights", INT_LIST, "non-negative heights")], OUT_INT,
        lambda heights: _trap(heights),
        [([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), ([3, 0, 3],)],
        lambda rng: [(ints(rng, n, 0, 20),) for n in (1, 2, 3, 6, 12, 40, 120, 260)],
        ["1 <= n <= 2000", "0 <= heights[i] <= 10^5"],
        ["Water above bar i is min(maxLeft, maxRight) - heights[i], clamped at 0.",
         "Precomputing prefix and suffix maxima gives an O(n) time, O(n) space solution.",
         "Two pointers achieve O(1) space: advance from the side with the smaller running maximum.",
         "The first and last bars never hold water."],
        explanations=["Six units collect in the dips.", "Three units sit between the two towers of 3."],
        brute=lambda heights: sum(
            max(0, min(max(heights[:i + 1]), max(heights[i:])) - heights[i]) for i in range(len(heights))
        ),
        pattern_note="When the answer depends on a maximum from both sides, either precompute both "
                     "directions or move two pointers inwards from the smaller side, which guarantees the "
                     "other side's maximum is at least as large.",
    ))

    add(P(
        "merge-two-sorted-arrays", "Merge Two Sorted Arrays", "easy", T + ["Arrays"], TP,
        "Merge the two sorted arrays `a` and `b` into one sorted array and print it.",
        [Param("a", INT_LIST, "sorted ascending"), Param("b", INT_LIST, "sorted ascending")], OUT_INT_LIST,
        lambda a, b: _merge(a, b),
        [([1, 3, 5], [2, 4]), ([1], [1])],
        lambda rng: [(sorted_ints(rng, n, -40, 40), sorted_ints(rng, m, -40, 40))
                     for n, m in ((1, 1), (1, 3), (3, 1), (4, 4), (9, 6), (25, 30), (90, 70))],
        ["1 <= n, m <= 2000", "both arrays are sorted in non-decreasing order",
         "-10^6 <= values <= 10^6"],
        ["Compare the fronts of both arrays and take the smaller.",
         "Advance only the pointer you consumed from.",
         "When one array runs out, append the remainder of the other.",
         "This is the merge step of merge sort."],
    ))

    add(P(
        "intersection-of-sorted-arrays", "Intersection Of Sorted Arrays", "easy", T + ["Arrays"], TP,
        "Both `a` and `b` are sorted. Print the common values with multiplicity (a value appearing twice "
        "in both appears twice in the answer), in non-decreasing order. Print an empty line if there are none.",
        [Param("a", INT_LIST, "sorted ascending"), Param("b", INT_LIST, "sorted ascending")], OUT_INT_LIST,
        lambda a, b: _intersect_multi(a, b),
        [([1, 2, 2, 3], [2, 2, 4]), ([1], [2])],
        lambda rng: [(sorted_ints(rng, n, 1, 12), sorted_ints(rng, m, 1, 12))
                     for n, m in ((1, 1), (2, 3), (5, 4), (9, 9), (25, 18), (70, 60))],
        ["1 <= n, m <= 2000", "both arrays are sorted in non-decreasing order"],
        ["Advance the pointer with the smaller value.",
         "On equality record the value and advance both pointers.",
         "Advancing both on a match is what preserves multiplicity correctly."],
        explanations=["2 appears twice in both.", "Nothing is shared."],
    ))

    add(P(
        "remove-duplicates-keep-two", "Remove Duplicates Keeping Two", "medium", T + ["Arrays"], TP,
        "The array `nums` is sorted. Remove extra copies so no value appears more than twice, keeping "
        "the sorted order. Print the resulting array.",
        [p_sorted()], OUT_INT_LIST, lambda nums: _keep_at_most_two(nums),
        [([1, 1, 1, 2, 2, 3],), ([5],)],
        lambda rng: [(sorted(ints(rng, n, 1, max(2, n // 3))),) for n in (1, 2, 4, 8, 16, 45, 120, 250)],
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Keep a write pointer for the next output slot.",
         "Write an element when the slot index is below 2 or it differs from the value two slots back.",
         "That single comparison enforces the at-most-twice rule.",
         "The same idea generalises to at most k copies."],
        explanations=["Only two 1s survive.", "A single element is untouched."],
    ))

    add(P(
        "squares-of-sorted-array", "Squares Of A Sorted Array", "easy", T + ["Arrays"], TP,
        "The array `nums` is sorted and may contain negatives. Print the squares of its elements in "
        "non-decreasing order.",
        [p_sorted()], OUT_INT_LIST, lambda nums: _sorted_squares(nums),
        [([-4, -1, 0, 3, 10],), ([-2],)],
        g_sorted(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order", "-10^5 <= nums[i] <= 10^5"],
        ["The largest square sits at one of the two ends.",
         "Compare absolute values at both pointers and fill the output from the back.",
         "That gives O(n) without sorting again.",
         "Sorting the squares directly is O(n log n) and also accepted."],
        explanations=["Squares 16,1,0,9,100 sort to 0,1,9,16,100.", "A single value squares to 4."],
        brute=lambda nums: sorted(v * v for v in nums),
    ))

    add(P(
        "partition-array-by-pivot", "Partition Around Pivot", "easy", T + ["Arrays"], TP,
        "Rearrange `nums` so every element strictly less than `pivot` comes first (in their original "
        "relative order), followed by every element greater than or equal to `pivot` (also in original "
        "relative order). Print the result.",
        [p_nums(), p_int("pivot", "the partition value")], OUT_INT_LIST,
        lambda nums, pivot: [v for v in nums if v < pivot] + [v for v in nums if v >= pivot],
        [([3, 1, 4, 2], 3), ([5, 5], 5)],
        lambda rng: [(ints(rng, n, -20, 20), rng.randint(-20, 20)) for n in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= n <= 2000", "-10^6 <= nums[i], pivot <= 10^6"],
        ["A stable partition preserves relative order within each group.",
         "Two passes collecting each group is the simplest correct approach.",
         "A single in-place swap pass would not be stable."],
        explanations=["[1,2] then [3,4].", "Nothing is below the pivot."],
    ))

    add(P(
        "longest-mountain-length", "Longest Mountain", "medium", T + ["Arrays"], TP,
        "A mountain is a subarray that strictly increases and then strictly decreases, with at least one "
        "element on each side of the peak. Print the length of the longest mountain, or `0` if there is none.",
        [p_nums()], OUT_INT, lambda nums: _longest_mountain(nums),
        [([2, 1, 4, 7, 3, 2, 5],), ([2, 2, 2],)],
        lambda rng: [(ints(rng, n, 1, 8),) for n in (1, 2, 3, 5, 9, 20, 60, 150)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Scan for a strict increase, follow it to a peak, then follow the strict decrease.",
         "A mountain needs at least one up step and one down step, so length >= 3.",
         "Resume scanning from the end of the mountain you just measured.",
         "Plateaus break a mountain because the change must be strict."],
        explanations=["[1,4,7,3,2] has length 5.", "No strict changes exist."],
        brute=lambda nums: _longest_mountain_brute(nums),
    ))

    add(P(
        "valid-palindrome-ignoring-case", "Palindrome Ignoring Non Letters", "easy",
        T + ["Strings"], TP,
        "The string `s` mixes lowercase letters and digits. Print `YES` if the letters alone (in order) "
        "form a palindrome, ignoring every digit, else `NO`.",
        [Param("s", "str", "lowercase letters and digits")], OUT_BOOL,
        lambda s: _letters_palindrome(s),
        [("a1b2b3a",), ("ab1c",)],
        lambda rng: [("".join(rng.choice("aabb0123") for _ in range(n)),) for n in (1, 2, 4, 8, 16, 45, 120)],
        ["1 <= |s| <= 2000", "s contains lowercase letters and digits only"],
        ["Use two pointers and skip any character that is not a letter.",
         "Compare only the letters the pointers land on.",
         "A string with no letters counts as a palindrome."],
        explanations=["The letters spell abba.", "The letters spell abc."],
    ))

    add(P(
        "min-swaps-to-group-ones", "Minimum Swaps To Group Ones", "medium",
        T + ["Arrays", "Sliding Window"], TP,
        "Given a binary array `nums`, print the fewest swaps of any two elements needed to bring all "
        "the `1`s together into one contiguous block. Print `0` if there are no ones.",
        [Param("nums", INT_LIST, "each value is 0 or 1")], OUT_INT,
        lambda nums: _min_swaps_group_ones(nums),
        [([1, 0, 1, 0, 1],), ([0, 0],)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)],) for n in (1, 2, 4, 9, 20, 55, 140, 300)],
        ["1 <= n <= 2000", "nums[i] is 0 or 1"],
        ["Let k be the total number of ones; the answer block has exactly length k.",
         "Slide a window of length k and count the zeros inside it.",
         "The minimum zero count over all windows is the answer, since each zero needs one swap.",
         "Zero ones means nothing to group."],
        explanations=["A window of three holding one zero needs one swap.", "There are no ones."],
        brute=lambda nums: _min_swaps_brute(nums),
    ))

    add(P(
        "sort-array-by-parity", "Sort By Parity", "easy", T + ["Arrays"], TP,
        "Rearrange `nums` so all even values come before all odd values, keeping the original relative "
        "order inside each group. Print the result.",
        [p_nums()], OUT_INT_LIST,
        lambda nums: [v for v in nums if v % 2 == 0] + [v for v in nums if v % 2 != 0],
        [([3, 1, 2, 4],), ([1, 3],)],
        lambda rng: [(ints(rng, n, 0, 40),) for n in (1, 2, 4, 9, 25, 70, 180)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^6"],
        ["Collect evens in one pass and odds in another to stay stable.",
         "A two-pointer swap is faster but reorders within the groups.",
         "The relative order requirement is what forces the stable approach."],
        explanations=["Evens [2,4] then odds [3,1].", "There are no evens."],
    ))

    add(P(
        "backspace-string-compare", "Backspace String Compare", "medium", T + ["Strings", "Stack & Queue"], TP,
        "In both strings the character `#` means 'delete the previous character'. Print `YES` if `a` and "
        "`b` become equal after applying all backspaces, else `NO`.",
        [Param("a", "str", "letters and # characters"), Param("b", "str", "letters and # characters")],
        OUT_BOOL, lambda a, b: _apply_backspace(a) == _apply_backspace(b),
        [("ab#c", "ad#c"), ("a#c", "b")],
        lambda rng: [("".join(rng.choice("abc##") for _ in range(n)) or "a",
                      "".join(rng.choice("abc##") for _ in range(m)) or "a")
                     for n, m in ((1, 1), (2, 3), (5, 5), (9, 7), (20, 22), (60, 55))],
        ["1 <= |a|, |b| <= 2000", "each character is a lowercase letter or #"],
        ["Building both results with a stack is the clearest solution.",
         "A backspace at the start of the string deletes nothing.",
         "Comparing from the back with two pointers achieves O(1) extra space."],
        explanations=["Both reduce to ac.", "They reduce to c and b."],
    ))

    add(P(
        "reverse-array-in-groups", "Reverse In Groups", "easy", T + ["Arrays"], TP,
        "Reverse every consecutive block of `k` elements of `nums`. A trailing block shorter than `k` is "
        "reversed too. Print the result.",
        [p_nums(), p_int("k", "group size")], OUT_INT_LIST,
        lambda nums, k: _reverse_groups(nums, k),
        [([1, 2, 3, 4, 5], 3), ([1, 2], 5)],
        lambda rng: [(ints(rng, n, -30, 30), rng.randint(1, max(1, n + 2)))
                     for n in (1, 2, 4, 7, 15, 40, 120)],
        ["1 <= n <= 2000", "1 <= k <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Step through the array in strides of k.",
         "Reverse each slice with two pointers, clamping the right end at n-1.",
         "k = 1 leaves the array unchanged; k >= n reverses the whole array."],
        explanations=["[3,2,1] then [5,4].", "k exceeds n, so the whole array reverses."],
    ))

    add(P(
        "count-good-triplets", "Count Good Triplets", "medium", T + ["Arrays"], TP,
        "Count triples of positions `i < j < k` where `nums[i] <= nums[j] <= nums[k]`.",
        [p_nums()], OUT_INT, lambda nums: _count_non_decreasing_triples(nums),
        [([1, 2, 3],), ([3, 2, 1],)],
        lambda rng: [(ints(rng, n, 1, 8),) for n in (1, 2, 3, 5, 9, 20, 50, 90)],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Fix the middle index j.",
         "Count how many earlier elements are <= nums[j] and how many later elements are >= nums[j].",
         "Multiply those two counts and sum over all j.",
         "That turns an O(n^3) enumeration into O(n^2)."],
        explanations=["Only (1,2,3) qualifies.", "The array strictly decreases."],
        brute=lambda nums: sum(
            1 for i in range(len(nums)) for j in range(i + 1, len(nums)) for k in range(j + 1, len(nums))
            if nums[i] <= nums[j] <= nums[k]
        ),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            # The window may hold duplicates of nums[right]; the documented
            # tie-break wants the smallest second index, so slide back over them.
            while right - 1 > left and nums[right - 1] == nums[right]:
                right -= 1
            return [left, right]
        if total < target:
            left += 1
        else:
            right -= 1
    return [-1]


def _two_sum_brute(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return [-1]


def _closest_pair_sum(nums, target):
    left, right = 0, len(nums) - 1
    best = nums[left] + nums[right]
    while left < right:
        total = nums[left] + nums[right]
        if (abs(total - target), total) < (abs(best - target), best):
            best = total
        if total == target:
            return total
        if total < target:
            left += 1
        else:
            right -= 1
    return best


def _three_sum_exists(nums, target):
    values = sorted(nums)
    n = len(values)
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            total = values[i] + values[left] + values[right]
            if total == target:
                return True
            if total < target:
                left += 1
            else:
                right -= 1
    return False


def _closest_triple(nums, target):
    values = sorted(nums)
    n = len(values)
    best = values[0] + values[1] + values[2]
    for i in range(n - 2):
        left, right = i + 1, n - 1
        while left < right:
            total = values[i] + values[left] + values[right]
            if (abs(total - target), total) < (abs(best - target), best):
                best = total
            if total == target:
                return total
            if total < target:
                left += 1
            else:
                right -= 1
    return best


def _count_pairs_diff(nums, k):
    counts: dict[int, int] = {}
    for value in nums:
        counts[value] = counts.get(value, 0) + 1
    if k == 0:
        return sum(count * (count - 1) // 2 for count in counts.values())
    return sum(count * counts.get(value + k, 0) for value, count in counts.items())


def _max_water(heights):
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        best = max(best, min(heights[left], heights[right]) * (right - left))
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return best


def _trap(heights):
    if len(heights) < 3:
        return 0
    left, right = 0, len(heights) - 1
    left_max, right_max = heights[left], heights[right]
    total = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, heights[left])
            total += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            total += right_max - heights[right]
    return total


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


def _intersect_multi(a, b):
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            result.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return result


def _keep_at_most_two(nums):
    result: list[int] = []
    for value in nums:
        if len(result) < 2 or value != result[-2]:
            result.append(value)
    return result


def _sorted_squares(nums):
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    for slot in range(n - 1, -1, -1):
        if abs(nums[left]) > abs(nums[right]):
            result[slot] = nums[left] * nums[left]
            left += 1
        else:
            result[slot] = nums[right] * nums[right]
            right -= 1
    return result


def _longest_mountain(nums):
    n = len(nums)
    best = 0
    index = 1
    while index < n - 1:
        if nums[index - 1] < nums[index] > nums[index + 1]:
            left = index - 1
            while left > 0 and nums[left - 1] < nums[left]:
                left -= 1
            right = index + 1
            while right < n - 1 and nums[right] > nums[right + 1]:
                right += 1
            best = max(best, right - left + 1)
            index = right
        else:
            index += 1
    return best


def _longest_mountain_brute(nums):
    n = len(nums)
    best = 0
    for i in range(n):
        for j in range(i + 2, n):
            window = nums[i:j + 1]
            peak = window.index(max(window))
            if peak == 0 or peak == len(window) - 1:
                continue
            up = all(window[t] < window[t + 1] for t in range(peak))
            down = all(window[t] > window[t + 1] for t in range(peak, len(window) - 1))
            if up and down:
                best = max(best, len(window))
    return best


def _letters_palindrome(s):
    letters = [ch for ch in s if ch.isalpha()]
    return letters == letters[::-1]


def _min_swaps_group_ones(nums):
    total_ones = sum(nums)
    if total_ones == 0:
        return 0
    zeros_in_window = sum(1 for v in nums[:total_ones] if v == 0)
    best = zeros_in_window
    for index in range(total_ones, len(nums)):
        if nums[index] == 0:
            zeros_in_window += 1
        if nums[index - total_ones] == 0:
            zeros_in_window -= 1
        best = min(best, zeros_in_window)
    return best


def _min_swaps_brute(nums):
    total_ones = sum(nums)
    if total_ones == 0:
        return 0
    best = None
    for start in range(len(nums) - total_ones + 1):
        zeros = sum(1 for v in nums[start:start + total_ones] if v == 0)
        best = zeros if best is None else min(best, zeros)
    return best


def _apply_backspace(text):
    stack: list[str] = []
    for ch in text:
        if ch == "#":
            if stack:
                stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)


def _reverse_groups(nums, k):
    result = list(nums)
    for start in range(0, len(result), k):
        end = min(start + k - 1, len(result) - 1)
        while start < end:
            result[start], result[end] = result[end], result[start]
            start += 1
            end -= 1
    return result


def _count_non_decreasing_triples(nums):
    n = len(nums)
    total = 0
    for j in range(n):
        left = sum(1 for i in range(j) if nums[i] <= nums[j])
        right = sum(1 for k in range(j + 1, n) if nums[k] >= nums[j])
        total += left * right
    return total
