"""Greedy algorithms."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_STR,
    P,
    Param,
    STR,
    ints,
    p_int,
    p_nums,
    word,
)

T = ["Greedy"]
G = ["Greedy"]
SIZES = (1, 2, 3, 6, 12, 35, 110, 260)


def specs():
    out: list = []
    add = out.append

    add(P(
        "jump-game-can-reach-end", "Jump Game", "medium", T + ["Arrays"], G,
        "From index `i` you may jump to any index up to `i + nums[i]`. Print `YES` if the last index is "
        "reachable from index 0, else `NO`.",
        [Param("nums", INT_LIST, "non-negative jump lengths")], OUT_BOOL,
        lambda nums: _can_jump(nums),
        [([2, 3, 1, 1, 4],), ([3, 2, 1, 0, 4],)],
        lambda rng: [(ints(rng, n, 0, 4),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= nums[i] <= 1000"],
        ["Sweep left to right tracking the furthest index reachable so far.",
         "If the current index exceeds that reach, you are stuck.",
         "Extend the reach with i + nums[i] at every step.",
         "This is O(n) and needs no DP table."],
        explanations=["0->1->4 works.", "Index 3 holds 0 and blocks progress."],
    ))

    add(P(
        "gas-station-start-index", "Gas Station", "medium", T + ["Arrays"], G,
        "Around a circular route, station `i` provides `gas[i]` fuel and driving to the next station costs "
        "`cost[i]`. Print the smallest starting index from which you can complete the loop, or `-1` if it "
        "is impossible.",
        [Param("gas", INT_LIST, "fuel available at each station"),
         Param("cost", INT_LIST, "fuel needed to reach the next station")], OUT_INT,
        lambda gas, cost: _gas_station(gas, cost),
        [([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3])],
        lambda rng: [(lambda k: (ints(rng, k, 0, 10), ints(rng, k, 0, 10)))(k)
                     for k in (1, 2, 3, 6, 12, 35, 110)],
        ["1 <= n <= 2000", "0 <= gas[i], cost[i] <= 10^4",
         "gas and cost have the same length"],
        ["If the total gas is less than the total cost, no start works.",
         "Otherwise sweep once: when the running tank goes negative, no start up to here can work, so "
         "restart from the next index.",
         "The surviving candidate is guaranteed to complete the loop.",
         "Because we need the smallest index, verify the candidate rather than assuming."],
        explanations=["Starting at index 3 completes the loop.", "Total cost exceeds total gas."],
        brute=lambda gas, cost: _gas_brute(gas, cost),
    ))

    add(P(
        "candy-distribution-min", "Candy Distribution", "hard", T + ["Arrays"], G,
        "Each child has a rating. Every child gets at least one candy and any child with a strictly higher "
        "rating than a neighbour gets more candies than that neighbour. Print the fewest candies needed.",
        [Param("ratings", INT_LIST, "the child ratings")], OUT_INT,
        lambda ratings: _candy(ratings),
        [([1, 0, 2],), ([1, 2, 2],)],
        lambda rng: [(ints(rng, n, 0, 6),) for n in SIZES],
        ["1 <= n <= 2000", "0 <= ratings[i] <= 10^4"],
        ["Sweep left to right, giving one more candy than the left neighbour when the rating rises.",
         "Then sweep right to left doing the same for the right neighbour, taking the maximum.",
         "Two passes are needed because each child has two constraints.",
         "Equal ratings impose no requirement in either direction."],
        explanations=["2,1,2 candies total 5.", "1,2,1 candies total 4."],
    ))

    add(P(
        "min-platforms-required", "Minimum Platforms", "medium", T + ["Sorting & Searching"], G,
        "Trains arrive and depart at the given times on the same day. Print the fewest platforms needed so "
        "no train ever waits. A train departing at time `t` frees the platform only after another arriving "
        "at `t` has taken one.",
        [Param("arrivals", INT_LIST, "arrival times"), Param("departures", INT_LIST, "departure times")],
        OUT_INT, lambda arrivals, departures: _min_platforms(arrivals, departures),
        [([900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000]), ([100], [200])],
        lambda rng: [(lambda k: (lambda a: (a, [x + rng.randint(1, 50) for x in a]))(
            sorted(ints(rng, k, 0, 500)))) (k) for k in (1, 2, 3, 6, 12, 35, 110)],
        ["1 <= n <= 2000", "0 <= times <= 10^6", "arrivals[i] < departures[i]",
         "both arrays have the same length"],
        ["Sort arrivals and departures independently.",
         "Sweep both with two pointers, incrementing a counter on an arrival and decrementing on a departure.",
         "Process an arrival before a departure when the times tie.",
         "Track the peak counter value."],
        explanations=["Three platforms are needed at the busiest moment.", "One train, one platform."],
        brute=lambda arrivals, departures: _min_platforms_brute(arrivals, departures),
    ))

    add(P(
        "activity-selection-count", "Maximum Non Overlapping Activities", "medium",
        T + ["Intervals"], ["Interval Scheduling"],
        "Each activity `i` runs from `starts[i]` to `ends[i]`. Print the largest number of activities you "
        "can attend if you can only do one at a time. An activity ending exactly when another starts is "
        "compatible.",
        [Param("starts", INT_LIST, "start times"), Param("ends", INT_LIST, "end times")], OUT_INT,
        lambda starts, ends: _activity_selection(starts, ends),
        [([1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9]), ([1], [2])],
        lambda rng: [(lambda k: (lambda s: (s, [x + rng.randint(1, 20) for x in s]))(
            ints(rng, k, 0, 60)))(k) for k in (1, 2, 3, 6, 12, 35, 110)],
        ["1 <= n <= 2000", "0 <= times <= 10^6", "starts[i] < ends[i]"],
        ["Sort the activities by their end time.",
         "Greedily take an activity whenever it starts at or after the last chosen end.",
         "Finishing earliest leaves the most room for the rest — that is the exchange argument.",
         "Sorting by start time or by duration both give wrong answers."],
        explanations=["Four activities fit.", "A single activity."],
    ))

    add(P(
        "fractional-knapsack-value", "Fractional Knapsack", "medium", T, G,
        "Items may be split. Print the greatest total value that fits in capacity `capacity`, rounded to "
        "6 decimal places.",
        [Param("weights", INT_LIST, "item weights"), Param("values", INT_LIST, "item values"),
         p_int("capacity", "the weight limit")], "float",
        lambda weights, values, capacity: _fractional_knapsack(weights, values, capacity),
        [([10, 20, 30], [60, 100, 120], 50), ([5], [10], 0)],
        lambda rng: [(lambda k: (ints(rng, k, 1, 20), ints(rng, k, 1, 60), rng.randint(0, 80)))(k)
                     for k in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= n <= 2000", "1 <= weights[i] <= 10^4", "1 <= values[i] <= 10^4", "0 <= capacity <= 10^6"],
        ["Sort items by value per unit weight, highest first.",
         "Take whole items while they fit, then a fraction of the next one.",
         "Splitting is what makes greedy optimal here — 0/1 knapsack needs DP.",
         "Print exactly 6 decimal places."],
        explanations=["Both small items plus two thirds of the last gives 240.", "Capacity is 0."],
    ))

    add(P(
        "min-coins-greedy-denominations", "Minimum Notes And Coins", "easy", T, G,
        "Using unlimited notes of the canonical denominations 2000, 500, 200, 100, 50, 20, 10, 5, 2 and 1, "
        "print the fewest notes needed to make `amount`.",
        [p_int("amount", "the amount to make")], OUT_INT,
        lambda amount: _min_notes(amount),
        [(2870,), (1,)],
        lambda rng: [(rng.randint(0, 10 ** 6),) for _ in range(8)],
        ["0 <= amount <= 10^9"],
        ["Take as many of the largest denomination as possible, then move down.",
         "Greedy is optimal for this canonical system because each denomination divides into the larger "
         "ones cleanly enough.",
         "For arbitrary denominations you would need the coin-change DP instead."],
        explanations=["2000+500+200+100+50+20 uses 6 notes.", "A single 1."],
    ))

    add(P(
        "assign-cookies-count", "Assign Cookies", "easy", T + ["Two Pointers"], G,
        "Each child needs a cookie of at least their greed value. Print the greatest number of children "
        "that can be satisfied, giving each child at most one cookie.",
        [Param("greed", INT_LIST, "each child's requirement"), Param("cookies", INT_LIST, "cookie sizes")],
        OUT_INT, lambda greed, cookies: _assign_cookies(greed, cookies),
        [([1, 2, 3], [1, 1]), ([1, 2], [1, 2, 3])],
        lambda rng: [(ints(rng, n, 1, 12), ints(rng, m, 1, 12))
                     for n, m in ((1, 1), (2, 3), (5, 4), (12, 9), (35, 25), (110, 80))],
        ["1 <= n, m <= 2000", "1 <= values <= 10^4"],
        ["Sort both arrays ascending.",
         "Walk them with two pointers, giving the smallest adequate cookie to the least greedy child.",
         "Advance the cookie pointer whether or not it satisfied a child.",
         "Spending a larger cookie than necessary can only hurt."],
        explanations=["Only one child can be satisfied.", "Both children can be satisfied."],
    ))

    add(P(
        "min-operations-to-equalize", "Minimum Increments To Equalize", "easy", T + ["Arrays"], G,
        "Each operation adds 1 to a single element. Print the fewest operations needed to make every "
        "element equal to the current maximum.",
        [p_nums()], OUT_INT, lambda nums: sum(max(nums) - v for v in nums),
        [([1, 2, 3],), ([4, 4],)],
        lambda rng: [(ints(rng, n, -30, 30),) for n in SIZES],
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Find the maximum, then sum each element's shortfall.",
         "No cleverness is needed — each element needs exactly max - value increments.",
         "An already-equal array needs 0 operations."],
        explanations=["2 + 1 + 0 = 3.", "Already equal."],
    ))

    add(P(
        "largest-number-after-removing-digits", "Largest Number After Removing Digits", "medium",
        T + ["Strings", "Stack & Queue"], G,
        "Remove exactly `k` digits from the digit string `s` so the remaining digits, in order, form the "
        "largest possible number. Print the result.",
        [Param("s", STR, "digits, no leading zero"), p_int("k", "digits to remove")], OUT_STR,
        lambda s, k: _largest_after_removal(s, k),
        [("1924", 2), ("12345", 4)],
        lambda rng: [(lambda text: (text, rng.randint(0, len(text) - 1)))(
            str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(n)))
            for n in (0, 1, 2, 4, 8, 15, 40, 90)],
        ["1 <= |s| <= 2000", "0 <= k < |s|", "s has no leading zero"],
        ["Keep a decreasing stack of digits.",
         "While the incoming digit is larger than the stack top and removals remain, pop.",
         "Popping a smaller earlier digit raises a more significant position, which dominates everything "
         "after it.",
         "Trim any unused removals from the end."],
        explanations=["Removing 1 and 2 leaves 94.", "Only the 5 remains."],
    ))

    add(P(
        "smallest-number-after-removing-digits", "Smallest Number After Removing Digits", "medium",
        T + ["Strings", "Stack & Queue"], G,
        "Remove exactly `k` digits from the digit string `s` so the remaining digits, in order, form the "
        "smallest possible number. Print the result without leading zeros (print `0` if nothing remains "
        "but zeros).",
        [Param("s", STR, "digits, no leading zero"), p_int("k", "digits to remove")], OUT_STR,
        lambda s, k: _smallest_after_removal(s, k),
        [("1432219", 3), ("10200", 1)],
        lambda rng: [(lambda text: (text, rng.randint(0, len(text) - 1)))(
            str(rng.randint(1, 9)) + "".join(rng.choice("0123456789") for _ in range(n)))
            for n in (0, 1, 2, 4, 8, 15, 40, 90)],
        ["1 <= |s| <= 2000", "0 <= k < |s|", "s has no leading zero"],
        ["Keep an increasing stack, popping while the top is larger than the incoming digit.",
         "This is the mirror of the largest-number version.",
         "Strip leading zeros at the end, and print 0 if the result is empty."],
        explanations=["1219 is the smallest.", "Removing the 1 leaves 200."],
    ))

    add(P(
        "min-swaps-to-make-alternating", "Minimum Swaps For Alternating Binary", "medium",
        T + ["Strings"], G,
        "The binary string `s` has equal counts of `0` and `1`, or counts differing by one. Print the "
        "fewest character swaps needed to make it alternate, or `-1` if it is impossible.",
        [Param("s", STR, "only 0 and 1 characters")], OUT_INT,
        lambda s: _min_swaps_alternating(s),
        [("111000",), ("010",)],
        lambda rng: [("".join(rng.choice("01") for _ in range(n)),) for n in (1, 2, 4, 8, 15, 40, 110, 250)],
        ["1 <= |s| <= 2000", "s contains only 0 and 1"],
        ["Alternating strings come in two shapes: starting with 0 or starting with 1.",
         "Count mismatches against each shape; the swaps needed are the mismatches divided by two.",
         "A shape is only viable when the character counts allow it.",
         "If the counts differ by more than one, no alternating arrangement exists."],
        explanations=["Three swaps produce 101010.", "Already alternating."],
    ))

    add(P(
        "max-units-on-truck", "Maximum Units On Truck", "easy", T + ["Sorting & Searching"], G,
        "Box type `i` has `counts[i]` boxes each holding `units[i]` items. Print the greatest number of "
        "items you can load using at most `capacity` boxes.",
        [Param("counts", INT_LIST, "boxes available per type"),
         Param("units", INT_LIST, "items per box for each type"),
         p_int("capacity", "maximum boxes")], OUT_INT,
        lambda counts, units, capacity: _max_units(counts, units, capacity),
        [([1, 2, 3], [3, 2, 1], 4), ([5], [10], 0)],
        lambda rng: [(lambda k: (ints(rng, k, 1, 10), ints(rng, k, 1, 20), rng.randint(0, 40)))(k)
                     for k in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= n <= 2000", "1 <= counts[i] <= 10^4", "1 <= units[i] <= 10^4", "0 <= capacity <= 10^6"],
        ["Sort the box types by items per box, largest first.",
         "Take as many boxes of the richest type as capacity allows, then move on.",
         "Boxes are interchangeable, so the exchange argument makes greedy optimal."],
        explanations=["1 box of 3 plus 2 of 2 plus 1 of 1 gives 8.", "No capacity."],
    ))

    add(P(
        "partition-labels-sizes", "Partition Labels", "medium", T + ["Strings", "Hashing"], G,
        "Split `s` into the greatest number of parts such that each letter appears in only one part. Print "
        "the part sizes in order, space separated.",
        [Param("s", STR, "lowercase letters")], "int[]",
        lambda s: _partition_labels(s),
        [("ababcbacadefegdehijhklij",), ("abc",)],
        lambda rng: [(word(rng, n, "abcd"),) for n in (1, 2, 4, 8, 15, 40, 110, 250)],
        ["1 <= |s| <= 2000", "s contains lowercase English letters only"],
        ["Record the last index of every character first.",
         "Sweep, extending the current part's end to the furthest last-index seen.",
         "Close the part when the sweep index reaches that end.",
         "Greedily closing as early as possible maximises the number of parts."],
        explanations=["Sizes 9, 7 and 8.", "Each letter is its own part."],
    ))

    add(P(
        "min-arrows-to-burst-balloons", "Minimum Arrows To Burst Balloons", "medium",
        T + ["Intervals"], ["Interval Scheduling"],
        "Balloon `i` spans the inclusive range `[starts[i], ends[i]]`. A vertical arrow bursts every "
        "balloon whose span contains its position. Print the fewest arrows needed.",
        [Param("starts", INT_LIST, "balloon start positions"),
         Param("ends", INT_LIST, "balloon end positions")], OUT_INT,
        lambda starts, ends: _min_arrows(starts, ends),
        [([10, 16, 1, 2], [16, 17, 6, 8]), ([1], [2])],
        lambda rng: [(lambda k: (lambda s: (s, [x + rng.randint(0, 20) for x in s]))(
            ints(rng, k, 0, 60)))(k) for k in (1, 2, 3, 6, 12, 35, 110)],
        ["1 <= n <= 2000", "0 <= starts[i] <= ends[i] <= 10^6"],
        ["Sort the balloons by their end position.",
         "Fire an arrow at the first balloon's end; it bursts every balloon starting at or before it.",
         "Move to the first balloon the arrow misses and repeat.",
         "This is the interval-scheduling greedy in disguise."],
        explanations=["Two arrows suffice.", "One balloon, one arrow."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _can_jump(nums):
    reach = 0
    for index, value in enumerate(nums):
        if index > reach:
            return False
        reach = max(reach, index + value)
    return True


def _gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = 0
    tank = 0
    for index in range(len(gas)):
        tank += gas[index] - cost[index]
        if tank < 0:
            start = index + 1
            tank = 0
    return start if start < len(gas) else -1


def _gas_brute(gas, cost):
    n = len(gas)
    for start in range(n):
        tank = 0
        ok = True
        for step in range(n):
            index = (start + step) % n
            tank += gas[index] - cost[index]
            if tank < 0:
                ok = False
                break
        if ok:
            return start
    return -1


def _candy(ratings):
    n = len(ratings)
    candies = [1] * n
    for index in range(1, n):
        if ratings[index] > ratings[index - 1]:
            candies[index] = candies[index - 1] + 1
    for index in range(n - 2, -1, -1):
        if ratings[index] > ratings[index + 1]:
            candies[index] = max(candies[index], candies[index + 1] + 1)
    return sum(candies)


def _min_platforms(arrivals, departures):
    arrive = sorted(arrivals)
    depart = sorted(departures)
    i = j = 0
    current = 0
    best = 0
    while i < len(arrive):
        if arrive[i] <= depart[j]:
            current += 1
            best = max(best, current)
            i += 1
        else:
            current -= 1
            j += 1
    return best


def _min_platforms_brute(arrivals, departures):
    events = sorted(set(arrivals))
    best = 0
    for moment in events:
        count = sum(1 for a, d in zip(arrivals, departures) if a <= moment <= d)
        best = max(best, count)
    return best


def _activity_selection(starts, ends):
    activities = sorted(zip(ends, starts))
    count = 0
    last_end = None
    for end, start in activities:
        if last_end is None or start >= last_end:
            count += 1
            last_end = end
    return count


def _fractional_knapsack(weights, values, capacity):
    items = sorted(zip(weights, values), key=lambda item: item[1] / item[0], reverse=True)
    total = 0.0
    remaining = capacity
    for weight, value in items:
        if remaining <= 0:
            break
        take = min(weight, remaining)
        total += value * (take / weight)
        remaining -= take
    return total


DENOMINATIONS = [2000, 500, 200, 100, 50, 20, 10, 5, 2, 1]


def _min_notes(amount):
    count = 0
    for note in DENOMINATIONS:
        count += amount // note
        amount %= note
    return count


def _assign_cookies(greed, cookies):
    wants = sorted(greed)
    sizes = sorted(cookies)
    i = j = 0
    satisfied = 0
    while i < len(wants) and j < len(sizes):
        if sizes[j] >= wants[i]:
            satisfied += 1
            i += 1
        j += 1
    return satisfied


def _largest_after_removal(s, k):
    stack: list[str] = []
    removals = k
    for ch in s:
        while stack and removals and stack[-1] < ch:
            stack.pop()
            removals -= 1
        stack.append(ch)
    if removals:
        stack = stack[:-removals]
    return "".join(stack)


def _smallest_after_removal(s, k):
    stack: list[str] = []
    removals = k
    for ch in s:
        while stack and removals and stack[-1] > ch:
            stack.pop()
            removals -= 1
        stack.append(ch)
    if removals:
        stack = stack[:-removals]
    result = "".join(stack).lstrip("0")
    return result if result else "0"


def _min_swaps_alternating(s):
    ones = s.count("1")
    zeros = len(s) - ones
    if abs(ones - zeros) > 1:
        return -1

    def mismatches(first):
        wrong = 0
        for index, ch in enumerate(s):
            expected = first if index % 2 == 0 else ("1" if first == "0" else "0")
            if ch != expected:
                wrong += 1
        return wrong

    options = []
    if zeros >= ones:
        options.append(mismatches("0"))
    if ones >= zeros:
        options.append(mismatches("1"))
    return min(options) // 2


def _max_units(counts, units, capacity):
    types = sorted(zip(units, counts), reverse=True)
    total = 0
    remaining = capacity
    for per_box, available in types:
        if remaining <= 0:
            break
        take = min(available, remaining)
        total += take * per_box
        remaining -= take
    return total


def _partition_labels(s):
    last = {ch: index for index, ch in enumerate(s)}
    result = []
    start = 0
    end = 0
    for index, ch in enumerate(s):
        end = max(end, last[ch])
        if index == end:
            result.append(end - start + 1)
            start = index + 1
    return result


def _min_arrows(starts, ends):
    balloons = sorted(zip(ends, starts))
    arrows = 0
    last_shot = None
    for end, start in balloons:
        if last_shot is None or start > last_shot:
            arrows += 1
            last_shot = end
    return arrows
