"""Binary search on sorted data and on the answer space."""

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

T = ["Binary Search"]
BS = ["Binary Search"]
MBS = ["Modified Binary Search"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 300)


def p_sorted(name="nums", desc="sorted in non-decreasing order"):
    return Param(name, INT_LIST, desc)


def g_sorted_target(lo=-40, hi=40, sizes=SIZES):
    def gen(rng: random.Random):
        cases = []
        for n in sizes:
            arr = sorted_ints(rng, n, lo, hi)
            # Mix hits and misses so both branches get exercised.
            target = rng.choice(arr) if rng.random() < 0.6 else rng.randint(lo - 5, hi + 5)
            cases.append((arr, target))
        return cases

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "binary-search-index", "Binary Search", "easy", T + ["Arrays"], BS,
        "The array `nums` is sorted. Print any index where `target` occurs, or `-1` if it is absent. "
        "If it occurs several times, print the **smallest** such index.",
        [p_sorted(), p_int("target", "the value to find")], OUT_INT,
        lambda nums, target: _lower_bound_exact(nums, target),
        [([1, 3, 5, 7], 5), ([1, 2], 4)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order", "-10^6 <= nums[i], target <= 10^6"],
        ["Maintain a search interval and halve it each step.",
         "Compute the midpoint as low + (high - low) / 2 to avoid overflow.",
         "Because duplicates are allowed, keep searching left after a hit to find the first index.",
         "Print -1 when the interval empties."],
        explanations=["5 sits at index 2.", "4 is absent."],
        brute=lambda nums, target: nums.index(target) if target in nums else -1,
        pattern_note="Binary search needs a monotone predicate. Here it is 'is nums[i] >= target', which "
                     "flips from false to true exactly once, so the boundary is findable in O(log n).",
    ))

    add(P(
        "first-occurrence-index", "First Occurrence", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted. Print the smallest index holding `target`, or `-1` if absent.",
        [p_sorted(), p_int("target")], OUT_INT,
        lambda nums, target: _lower_bound_exact(nums, target),
        [([1, 2, 2, 2, 3], 2), ([1, 2], 5)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Search for the boundary where values become >= target.",
         "On a match, record it and continue searching the left half.",
         "Verify the boundary index actually holds the target before returning it."],
        explanations=["The first 2 is at index 1.", "5 is absent."],
        brute=lambda nums, target: nums.index(target) if target in nums else -1,
    ))

    add(P(
        "last-occurrence-index", "Last Occurrence", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted. Print the largest index holding `target`, or `-1` if absent.",
        [p_sorted(), p_int("target")], OUT_INT,
        lambda nums, target: _last_occurrence(nums, target),
        [([1, 2, 2, 2, 3], 2), ([1, 2], 5)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Find the boundary where values become > target, then step back one.",
         "On a match, record it and continue searching the right half.",
         "Return -1 when the recorded index was never set."],
        explanations=["The last 2 is at index 3.", "5 is absent."],
        brute=lambda nums, target: max((i for i, v in enumerate(nums) if v == target), default=-1),
    ))

    add(P(
        "count-occurrences-sorted", "Count Occurrences In Sorted Array", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted. Print how many times `target` occurs.",
        [p_sorted(), p_int("target")], OUT_INT,
        lambda nums, target: _upper_bound(nums, target) - _lower_bound(nums, target),
        [([1, 2, 2, 2, 3], 2), ([1, 2], 5)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Find the first index with value >= target and the first with value > target.",
         "Their difference is the count.",
         "Two binary searches give O(log n) versus a linear scan's O(n)."],
        explanations=["2 occurs three times.", "5 never occurs."],
        brute=lambda nums, target: nums.count(target),
    ))

    add(P(
        "lower-bound-index", "Lower Bound", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted. Print the smallest index whose value is greater than or equal to "
        "`target`. Print `n` if every value is smaller.",
        [p_sorted(), p_int("target")], OUT_INT, _lb,
        [([1, 3, 5], 4), ([1, 2], 9)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Binary search the boundary of the predicate 'value >= target'.",
         "Keep the answer at n initially so an all-smaller array reports n.",
         "This is the standard lower_bound primitive."],
        explanations=["Index 2 holds 5, the first value >= 4.", "All values are below 9."],
        brute=lambda nums, target: sum(1 for v in nums if v < target),
    ))

    add(P(
        "upper-bound-index", "Upper Bound", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted. Print the smallest index whose value is strictly greater than "
        "`target`. Print `n` if no value exceeds it.",
        [p_sorted(), p_int("target")], OUT_INT, lambda nums, target: _upper_bound(nums, target),
        [([1, 3, 3, 5], 3), ([1, 2], 9)],
        g_sorted_target(),
        ["1 <= n <= 2000", "nums is sorted in non-decreasing order"],
        ["Binary search the boundary of 'value > target'.",
         "The only change from lower bound is a strict comparison.",
         "Print n when no element qualifies."],
        explanations=["Index 3 holds 5, the first value above 3.", "Nothing exceeds 9."],
        brute=lambda nums, target: sum(1 for v in nums if v <= target),
    ))

    add(P(
        "search-insert-position", "Search Insert Position", "easy", T + ["Arrays"], MBS,
        "The array `nums` is sorted with distinct values. Print the index of `target`, or the index where "
        "it should be inserted to keep the array sorted.",
        [Param("nums", INT_LIST, "sorted with distinct values"), p_int("target")], OUT_INT,
        lambda nums, target: _lb(nums, target),
        [([1, 3, 5, 6], 5), ([1, 3, 5, 6], 2)],
        lambda rng: [(lambda arr: (arr, rng.randint(-45, 45)))(sorted(set(ints(rng, n, -40, 40))) or [0])
                     for n in SIZES],
        ["1 <= n <= 2000", "nums is sorted and holds distinct values"],
        ["This is exactly the lower-bound query.",
         "A hit returns the element's index; a miss returns the insertion point.",
         "Both cases fall out of the same boundary search."],
        explanations=["5 is at index 2.", "2 would be inserted at index 1."],
        brute=lambda nums, target: sum(1 for v in nums if v < target),
    ))

    add(P(
        "search-rotated-sorted-array", "Search In Rotated Sorted Array", "medium",
        T + ["Arrays"], MBS,
        "The array `nums` was sorted ascending with distinct values, then rotated. Print the index of "
        "`target`, or `-1` if absent.",
        [Param("nums", INT_LIST, "a rotated strictly increasing array"), p_int("target")], OUT_INT,
        lambda nums, target: _search_rotated(nums, target),
        [([4, 5, 6, 7, 0, 1, 2], 0), ([4, 5, 6, 7, 0, 1, 2], 3)],
        lambda rng: [(lambda arr: (arr, rng.choice(arr) if rng.random() < 0.6 else rng.randint(-50, 50)))(
            _rotated_distinct(rng, n)) for n in SIZES],
        ["1 <= n <= 2000", "all values are distinct", "-10^6 <= nums[i], target <= 10^6"],
        ["At every step one of the two halves is properly sorted.",
         "Compare the midpoint with the endpoints to work out which half that is.",
         "If the target lies inside the sorted half, search there; otherwise search the other half.",
         "This keeps the search O(log n) despite the rotation."],
        explanations=["0 sits at index 4.", "3 is absent."],
        brute=lambda nums, target: nums.index(target) if target in nums else -1,
    ))

    add(P(
        "find-rotation-index", "Rotation Count", "medium", T + ["Arrays"], MBS,
        "The array `nums` was sorted ascending with distinct values, then rotated. Print the index of its "
        "smallest element, which equals the number of rotations applied.",
        [Param("nums", INT_LIST, "a rotated strictly increasing array")], OUT_INT,
        lambda nums: _rotation_index(nums),
        [([4, 5, 6, 7, 0, 1, 2],), ([1, 2, 3],)],
        lambda rng: [(_rotated_distinct(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "all values are distinct"],
        ["The minimum is the only element smaller than its predecessor.",
         "Compare the midpoint with the last element to decide which half holds the minimum.",
         "An unrotated array returns 0."],
        explanations=["0 sits at index 4.", "No rotation was applied."],
        brute=lambda nums: nums.index(min(nums)),
    ))

    add(P(
        "find-minimum-rotated", "Minimum In Rotated Array", "medium", T + ["Arrays"], MBS,
        "The array `nums` was sorted ascending with distinct values, then rotated. Print its smallest "
        "element.",
        [Param("nums", INT_LIST, "a rotated strictly increasing array")], OUT_INT,
        lambda nums: nums[_rotation_index(nums)],
        [([4, 5, 6, 7, 0, 1, 2],), ([2, 3, 4],)],
        lambda rng: [(_rotated_distinct(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "all values are distinct"],
        ["Binary search for the rotation point.",
         "If nums[mid] is greater than the last element, the minimum lies to the right.",
         "Otherwise it is at mid or to the left."],
        brute=min,
    ))

    add(P(
        "square-root-binary-search", "Square Root By Binary Search", "easy", T, BS,
        "Print the largest integer `r` with `r * r <= n`, using binary search.",
        [p_int("n")], OUT_INT, lambda n: _isqrt(n),
        [(8,), (0,)],
        lambda rng: [(rng.randint(0, 10 ** 9),) for _ in range(8)],
        ["0 <= n <= 10^9"],
        ["Search r in the interval 0..n (or 0..46341, which is enough here).",
         "The predicate 'r*r <= n' is monotone, so binary search applies.",
         "Watch for overflow when squaring in fixed-width languages."],
        explanations=["2*2 <= 8 but 3*3 > 8.", "0 is its own root."],
    ))

    add(P(
        "nth-root-integer", "Integer Nth Root", "medium", T, BS,
        "Print the largest integer `r` with `r^k <= n`, for a positive `n` and `k`.",
        [p_int("n"), p_int("k", "the root degree")], OUT_INT,
        lambda n, k: _integer_root(n, k),
        [(27, 3), (16, 2)],
        lambda rng: [(rng.randint(1, 10 ** 9), rng.randint(1, 8)) for _ in range(8)],
        ["1 <= n <= 10^9", "1 <= k <= 20"],
        ["Binary search r; the predicate 'r^k <= n' is monotone.",
         "Cap the exponentiation once it exceeds n to avoid huge intermediate values.",
         "k = 1 makes the answer n itself."],
        explanations=["3^3 = 27.", "4^2 = 16."],
    ))

    add(P(
        "min-capacity-ship-packages", "Minimum Capacity To Ship", "medium", T + ["Greedy"], BS,
        "Packages with the given `weights` must be shipped in order within `days` days. Each day you ship "
        "a contiguous block whose total does not exceed the ship's capacity. Print the smallest capacity "
        "that makes this possible.",
        [Param("weights", INT_LIST, "positive package weights"), p_int("days", "days available")],
        OUT_INT, lambda weights, days: _min_capacity(weights, days),
        [([1, 2, 3, 4, 5], 3), ([3], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, 1, 30))
                     for n in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= n <= 2000", "1 <= weights[i] <= 10^4", "1 <= days <= n"],
        ["Binary search the capacity between max(weights) and sum(weights).",
         "For a candidate capacity, greedily fill each day and count the days used.",
         "Fewer days used than allowed means the capacity can shrink.",
         "The predicate 'capacity works' is monotone, which is what makes this searchable."],
        explanations=["Capacity 6 allows [1,2,3], [4], [5].", "One package in one day."],
        brute=lambda weights, days: next(c for c in range(max(weights), sum(weights) + 1)
                                         if _days_needed(weights, c) <= days),
    ))

    add(P(
        "min-max-page-allocation", "Split Array Largest Sum", "hard", T + ["Greedy"], BS,
        "Split `nums` into exactly `k` non-empty contiguous parts so the largest part sum is as small as "
        "possible. Print that smallest possible largest sum.",
        [Param("nums", INT_LIST, "positive integers"), p_int("k", "number of parts")], OUT_INT,
        lambda nums, k: _min_largest_sum(nums, k),
        [([7, 2, 5, 10, 8], 2), ([5], 1)],
        lambda rng: [(lambda arr: (arr, rng.randint(1, len(arr))))(ints(rng, n, 1, 25))
                     for n in (1, 2, 3, 6, 12, 30, 80)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^4", "1 <= k <= n"],
        ["Binary search the answer between max(nums) and sum(nums).",
         "Greedily count how many parts a candidate limit needs.",
         "If it needs at most k parts the limit is feasible, so try smaller.",
         "This is the same shape as the ship-capacity problem."],
        explanations=["[7,2,5] and [10,8] give a maximum of 18.", "One part holds everything."],
        brute=lambda nums, k: next(limit for limit in range(max(nums), sum(nums) + 1)
                                   if _parts_needed(nums, limit) <= k),
    ))

    add(P(
        "koko-eating-bananas", "Minimum Eating Speed", "medium", T + ["Greedy"], BS,
        "There are piles of bananas with the given sizes. Eating at speed `s` per hour, a pile takes "
        "`ceil(size / s)` hours and you never split an hour across piles. Print the smallest integer "
        "speed that finishes all piles within `hours` hours.",
        [Param("piles", INT_LIST, "positive pile sizes"), p_int("hours", "hours available")], OUT_INT,
        lambda piles, hours: _min_speed(piles, hours),
        [([3, 6, 7, 11], 8), ([5], 5)],
        lambda rng: [(lambda arr: (arr, rng.randint(len(arr), len(arr) + 20)))(ints(rng, n, 1, 30))
                     for n in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= n <= 2000", "1 <= piles[i] <= 10^4", "n <= hours <= 10^9"],
        ["Binary search the speed between 1 and max(piles).",
         "For a candidate speed, sum ceil(pile / speed) across the piles.",
         "Hours needed decreases as speed increases, so the predicate is monotone.",
         "Compute the ceiling with integer arithmetic: (pile + speed - 1) / speed."],
        explanations=["Speed 4 finishes in 1+2+2+3 = 8 hours.", "Speed 1 finishes the single pile in 5 hours."],
        brute=lambda piles, hours: next(s for s in range(1, max(piles) + 1)
                                        if sum(-(-p // s) for p in piles) <= hours),
    ))

    add(P(
        "find-peak-binary-search", "Peak Element By Binary Search", "medium", T + ["Arrays"], MBS,
        "The array `nums` has no two adjacent equal values. Print the index of a peak, where a peak is "
        "strictly greater than its neighbours and out-of-range neighbours count as negative infinity. "
        "The checker accepts the **smallest** such index.",
        [Param("nums", INT_LIST, "no two adjacent values are equal")], OUT_INT,
        lambda nums: _first_peak(nums),
        [([1, 2, 3, 1],), ([1],)],
        lambda rng: [(_no_adjacent_equal(rng, n),) for n in SIZES],
        ["1 <= n <= 2000", "no two adjacent values are equal"],
        ["Binary search works because moving toward the larger neighbour always keeps a peak in range.",
         "Since the smallest index is required, a left-to-right scan is the simplest correct answer.",
         "The first and last positions can be peaks."],
        explanations=["Index 2 holds 3.", "The only element is a peak."],
        brute=lambda nums: next(i for i in range(len(nums))
                                if (i == 0 or nums[i] > nums[i - 1])
                                and (i == len(nums) - 1 or nums[i] > nums[i + 1])),
    ))

    add(P(
        "median-of-two-sorted", "Median Of Two Sorted Arrays", "hard", T + ["Arrays"], MBS,
        "Both `a` and `b` are sorted. Print the median of their combined multiset. If the total count is "
        "even, print the average of the two middle values.",
        [Param("a", INT_LIST, "sorted ascending"), Param("b", INT_LIST, "sorted ascending")], "float",
        lambda a, b: _median_two(a, b),
        [([1, 3], [2]), ([1, 2], [3, 4])],
        lambda rng: [(sorted_ints(rng, n, -40, 40), sorted_ints(rng, m, -40, 40))
                     for n, m in ((1, 1), (1, 3), (3, 1), (4, 4), (9, 6), (25, 30), (90, 70))],
        ["1 <= n, m <= 2000", "both arrays are sorted in non-decreasing order"],
        ["Merging both arrays gives an O(n+m) solution that passes here.",
         "The optimal method binary searches the split point of the smaller array in O(log min(n,m)).",
         "A valid split has equal counts on both sides and every left value <= every right value.",
         "Print exactly 6 decimal places."],
        explanations=["Merged [1,2,3] has median 2.", "Merged [1,2,3,4] averages 2 and 3."],
        brute=lambda a, b: _median_merge(a, b),
    ))

    add(P(
        "kth-element-two-sorted", "Kth Element Of Two Sorted Arrays", "hard", T + ["Arrays"], MBS,
        "Both `a` and `b` are sorted. Print the `k`-th smallest value of their combined multiset "
        "(1-based).",
        [Param("a", INT_LIST, "sorted ascending"), Param("b", INT_LIST, "sorted ascending"),
         p_int("k", "1-based rank")], OUT_INT,
        lambda a, b, k: sorted(a + b)[k - 1],
        [([2, 3, 6, 7, 9], [1, 4, 8, 10], 5), ([1], [2], 1)],
        lambda rng: [(lambda x, y: (x, y, rng.randint(1, len(x) + len(y))))(
            sorted_ints(rng, n, -40, 40), sorted_ints(rng, m, -40, 40))
            for n, m in ((1, 1), (2, 3), (5, 4), (9, 9), (25, 18), (70, 60))],
        ["1 <= n, m <= 2000", "1 <= k <= n + m", "both arrays are sorted"],
        ["Merging until you have taken k elements is O(k) and passes here.",
         "Binary searching how many elements to take from the first array gives O(log min(n,m)).",
         "The split is valid when the counts add to k and the boundary values interleave correctly."],
        explanations=["Merged, the 5th smallest is 6.", "The 1st smallest is 1."],
    ))

    add(P(
        "aggressive-cows-min-distance", "Maximum Minimum Distance", "hard", T + ["Greedy"], BS,
        "Stalls stand at the positions given in `positions`. Place `k` cows in distinct stalls so the "
        "smallest distance between any two cows is as large as possible. Print that largest possible "
        "minimum distance.",
        [Param("positions", INT_LIST, "distinct stall positions"), p_int("k", "cows to place")], OUT_INT,
        lambda positions, k: _max_min_distance(positions, k),
        [([1, 2, 4, 8, 9], 3), ([1, 5], 2)],
        lambda rng: [(lambda arr: (arr, rng.randint(2, len(arr))))(sorted(rng.sample(range(0, 400), n)))
                     for n in (2, 3, 4, 7, 15, 40, 90)],
        ["2 <= n <= 2000", "2 <= k <= n", "positions are distinct", "0 <= positions[i] <= 10^9"],
        ["Sort the positions first.",
         "Binary search the answer distance; for a candidate, greedily place cows as early as possible.",
         "If you can seat k cows the distance is feasible, so try larger.",
         "Feasibility decreases as the distance grows, giving the monotone predicate."],
        explanations=["Cows at 1, 4 and 8 keep a minimum gap of 3.", "The only choice gives 4."],
        brute=lambda positions, k: max(d for d in range(0, max(positions) - min(positions) + 1)
                                       if _can_place(sorted(positions), k, d)),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _lb(nums, target):
    low, high = 0, len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid
    return low


def _lower_bound(nums, target):
    return _lb(nums, target)


def _upper_bound(nums, target):
    low, high = 0, len(nums)
    while low < high:
        mid = (low + high) // 2
        if nums[mid] <= target:
            low = mid + 1
        else:
            high = mid
    return low


def _lower_bound_exact(nums, target):
    index = _lb(nums, target)
    if index < len(nums) and nums[index] == target:
        return index
    return -1


def _last_occurrence(nums, target):
    index = _upper_bound(nums, target) - 1
    if 0 <= index < len(nums) and nums[index] == target:
        return index
    return -1


def _rotated_distinct(rng, n):
    values = sorted(rng.sample(range(-500, 500), n))
    shift = rng.randint(0, n - 1)
    return values[shift:] + values[:shift]


def _search_rotated(nums, target):
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1


def _rotation_index(nums):
    low, high = 0, len(nums) - 1
    while low < high:
        mid = (low + high) // 2
        if nums[mid] > nums[high]:
            low = mid + 1
        else:
            high = mid
    return low


def _isqrt(n):
    low, high, best = 0, max(n, 1), 0
    while low <= high:
        mid = (low + high) // 2
        if mid * mid <= n:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best


def _integer_root(n, k):
    low, high, best = 1, n, 1
    while low <= high:
        mid = (low + high) // 2
        power = 1
        overflow = False
        for _ in range(k):
            power *= mid
            if power > n:
                overflow = True
                break
        if not overflow and power <= n:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best


def _days_needed(weights, capacity):
    days = 1
    load = 0
    for weight in weights:
        if load + weight > capacity:
            days += 1
            load = 0
        load += weight
    return days


def _min_capacity(weights, days):
    low, high = max(weights), sum(weights)
    while low < high:
        mid = (low + high) // 2
        if _days_needed(weights, mid) <= days:
            high = mid
        else:
            low = mid + 1
    return low


def _parts_needed(nums, limit):
    parts = 1
    load = 0
    for value in nums:
        if load + value > limit:
            parts += 1
            load = 0
        load += value
    return parts


def _min_largest_sum(nums, k):
    low, high = max(nums), sum(nums)
    while low < high:
        mid = (low + high) // 2
        if _parts_needed(nums, mid) <= k:
            high = mid
        else:
            low = mid + 1
    return low


def _min_speed(piles, hours):
    low, high = 1, max(piles)
    while low < high:
        mid = (low + high) // 2
        needed = sum(-(-pile // mid) for pile in piles)
        if needed <= hours:
            high = mid
        else:
            low = mid + 1
    return low


def _first_peak(nums):
    n = len(nums)
    for index in range(n):
        left_ok = index == 0 or nums[index] > nums[index - 1]
        right_ok = index == n - 1 or nums[index] > nums[index + 1]
        if left_ok and right_ok:
            return index
    return -1


def _no_adjacent_equal(rng, n):
    values = [rng.randint(-30, 30)]
    while len(values) < n:
        candidate = rng.randint(-30, 30)
        if candidate != values[-1]:
            values.append(candidate)
    return values


def _median_merge(a, b):
    merged = sorted(a + b)
    mid = len(merged) // 2
    if len(merged) % 2:
        return float(merged[mid])
    return (merged[mid - 1] + merged[mid]) / 2


def _median_two(a, b):
    return _median_merge(a, b)


def _can_place(positions, k, distance):
    placed = 1
    last = positions[0]
    for position in positions[1:]:
        if position - last >= distance:
            placed += 1
            last = position
            if placed >= k:
                return True
    return placed >= k


def _max_min_distance(positions, k):
    values = sorted(positions)
    low, high, best = 0, values[-1] - values[0], 0
    while low <= high:
        mid = (low + high) // 2
        if _can_place(values, k, mid):
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best
