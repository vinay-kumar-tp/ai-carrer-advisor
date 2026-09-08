"""Interval merging and scheduling."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    OUT_BOOL,
    OUT_INT,
    OUT_MATRIX,
    P,
    PAIR_LIST,
    Param,
    p_int,
)

T = ["Intervals"]
MI = ["Merge Intervals"]
IS = ["Interval Scheduling"]


def p_intervals(name="intervals", desc="each pair is an interval start end"):
    return Param(name, PAIR_LIST, desc)


def g_intervals(sizes=(1, 2, 3, 6, 12, 35, 90, 200)):
    def gen(rng: random.Random):
        cases = []
        for m in sizes:
            items = []
            for _ in range(m):
                start = rng.randint(0, 80)
                items.append((start, start + rng.randint(0, 20)))
            cases.append((items,))
        return cases

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "merge-overlapping-intervals", "Merge Intervals", "medium", T, MI,
        "Merge every set of overlapping or touching intervals and print the result sorted by start, one "
        "interval per line as `start end`.",
        [p_intervals()], OUT_MATRIX, lambda intervals: _merge(intervals),
        [([(1, 3), (2, 6), (8, 10), (15, 18)],), ([(1, 4), (4, 5)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Sort the intervals by start.",
         "Extend the current merged interval whenever the next one starts at or before its end.",
         "Otherwise close the current interval and open a new one.",
         "Touching intervals like [1,4] and [4,5] merge because they share an endpoint."],
        explanations=["[1,6], [8,10] and [15,18].", "They touch at 4 and merge."],
        brute=lambda intervals: _merge_brute(intervals),
    ))

    add(P(
        "count-merged-intervals", "Count Merged Intervals", "medium", T, MI,
        "Print how many intervals remain after merging every overlapping or touching interval.",
        [p_intervals()], OUT_INT, lambda intervals: len(_merge(intervals)),
        [([(1, 3), (2, 6), (8, 10)],), ([(1, 2)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Sort by start, then count how many times you have to open a new group.",
         "A new group opens whenever the next start exceeds the running end.",
         "The answer is at least 1 for a non-empty input."],
        explanations=["[1,6] and [8,10].", "A single interval."],
    ))

    add(P(
        "total-covered-length", "Total Covered Length", "medium", T, MI,
        "Print the total length of the number line covered by at least one interval, counting overlaps "
        "once.",
        [p_intervals()], OUT_INT, lambda intervals: _covered_length(intervals),
        [([(1, 4), (2, 6), (8, 10)],), ([(3, 3)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Merge the intervals first, then sum each merged length as end - start.",
         "A zero-length interval contributes 0.",
         "Summing raw lengths without merging would double count overlaps."],
        explanations=["[1,6] gives 5 and [8,10] gives 2, totalling 7.", "A point has zero length."],
        brute=lambda intervals: _covered_brute(intervals),
    ))

    add(P(
        "insert-interval-merged", "Insert Interval", "medium", T, MI,
        "The `intervals` are sorted by start and pairwise non-overlapping. Insert the interval "
        "`[newStart, newEnd]`, merging where needed, and print the result one interval per line.",
        [p_intervals("intervals", "sorted, non-overlapping intervals"),
         p_int("newStart", "start of the interval to insert"),
         p_int("newEnd", "end of the interval to insert")], OUT_MATRIX,
        lambda intervals, newStart, newEnd: _merge(list(intervals) + [(newStart, newEnd)]),
        [([(1, 3), (6, 9)], 2, 5), ([(1, 2)], 5, 6)],
        lambda rng: [(lambda base: (base, rng.randint(0, 90), rng.randint(0, 90)))(_disjoint(rng, m))
                     for m in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= m <= 2000", "intervals are sorted and non-overlapping", "0 <= values <= 10^6"],
        ["Copy intervals ending before the new start, merge everything overlapping it, then copy the rest.",
         "Alternatively append the new interval and merge everything from scratch.",
         "The sorted input is what allows the single-pass version."],
        explanations=["[1,5] and [6,9].", "[1,2] and [5,6]."],
    ))

    add(P(
        "can-attend-all-meetings", "Can Attend All Meetings", "easy", T, IS,
        "Print `YES` if none of the intervals overlap (touching endpoints are fine), else `NO`.",
        [p_intervals("meetings", "each pair is a meeting start end")], OUT_BOOL,
        lambda meetings: _no_overlap(meetings),
        [([(0, 30), (5, 10)],), ([(7, 10), (2, 4)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Sort by start time.",
         "Any meeting starting strictly before the previous one ends is a conflict.",
         "Touching meetings do not conflict, so use a strict comparison."],
        explanations=["The second meeting starts inside the first.", "They do not overlap."],
    ))

    add(P(
        "min-meeting-rooms", "Minimum Meeting Rooms", "medium", T, IS,
        "Print the fewest rooms needed so every meeting can run. A meeting ending at time `t` frees its "
        "room for a meeting starting at `t`.",
        [p_intervals("meetings", "each pair is a meeting start end")], OUT_INT,
        lambda meetings: _min_rooms(meetings),
        [([(0, 30), (5, 10), (15, 20)],), ([(1, 2), (2, 3)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Sort start times and end times separately, then sweep with two pointers.",
         "A start before the earliest unfinished end needs a new room.",
         "The peak number of simultaneous meetings is the answer.",
         "A min-heap of end times is the equivalent formulation."],
        explanations=["Two rooms cover the overlap.", "The rooms can be reused."],
        brute=lambda meetings: _min_rooms_brute(meetings),
    ))

    add(P(
        "max-overlapping-intervals-point", "Maximum Simultaneous Intervals", "medium", T, IS,
        "Print the largest number of intervals that contain a common point, treating intervals as "
        "inclusive on both ends.",
        [p_intervals()], OUT_INT, lambda intervals: _max_overlap_inclusive(intervals),
        [([(1, 5), (2, 6), (7, 8)],), ([(1, 2)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Create +1 events at each start and -1 events just after each end.",
         "Sort the events and sweep, tracking the running count.",
         "Because the intervals are inclusive, an end at t must be processed after a start at t.",
         "Track the peak count."],
        explanations=["Intervals 1 and 2 share points 2 to 5.", "A single interval."],
        brute=lambda intervals: _max_overlap_brute(intervals),
    ))

    add(P(
        "remove-min-intervals-non-overlap", "Minimum Intervals To Remove", "medium", T, IS,
        "Print the fewest intervals to delete so the remaining ones do not overlap. Touching endpoints are "
        "allowed.",
        [p_intervals()], OUT_INT,
        lambda intervals: len(intervals) - _max_non_overlapping(intervals),
        [([(1, 2), (2, 3), (3, 4), (1, 3)],), ([(1, 2)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Keeping the most intervals is the same as removing the fewest.",
         "Sort by end time and greedily keep every interval starting at or after the last kept end.",
         "The answer is the total count minus the kept count."],
        explanations=["Removing [1,3] leaves three non-overlapping intervals.", "Nothing to remove."],
    ))

    add(P(
        "interval-intersection-total", "Interval List Intersections", "medium", T, MI,
        "Both lists are sorted and internally non-overlapping. Print the total length of the parts covered "
        "by both lists.",
        [p_intervals("a", "first sorted, non-overlapping list"),
         p_intervals("b", "second sorted, non-overlapping list")], OUT_INT,
        lambda a, b: _intersection_length(a, b),
        [([(0, 2), (5, 10)], [(1, 5), (8, 12)]), ([(1, 2)], [(3, 4)])],
        lambda rng: [(_disjoint(rng, n), _disjoint(rng, m))
                     for n, m in ((1, 1), (2, 3), (5, 4), (12, 9), (35, 25), (90, 70))],
        ["1 <= m <= 2000", "each list is sorted and non-overlapping", "0 <= values <= 10^6"],
        ["Walk both lists with two pointers.",
         "The overlap of two intervals is max(starts) to min(ends), counted only when it is non-negative.",
         "Advance whichever interval ends first.",
         "This is O(n + m) thanks to the sorting."],
        explanations=["Overlaps [1,2], [5,5] and [8,10] total 3.", "The lists never overlap."],
        brute=lambda a, b: _intersection_brute(a, b),
    ))

    add(P(
        "point-in-any-interval", "Point Covered By Interval", "easy", T, MI,
        "Print `YES` if the point `x` lies inside at least one inclusive interval, else `NO`.",
        [p_intervals(), p_int("x", "the point to test")], OUT_BOOL,
        lambda intervals, x: any(start <= x <= end for start, end in intervals),
        [([(1, 3), (6, 9)], 7), ([(1, 3)], 5)],
        lambda rng: [(lambda items: (items, rng.randint(0, 100)))(
            [(lambda s: (s, s + rng.randint(0, 20)))(rng.randint(0, 80)) for _ in range(m)])
            for m in (1, 2, 3, 6, 12, 35, 90)],
        ["1 <= m <= 2000", "0 <= values <= 10^6"],
        ["A linear scan testing each interval is O(m).",
         "After merging and sorting, binary search answers each query in O(log m).",
         "Both endpoints count as inside."],
        explanations=["7 lies in [6,9].", "5 lies in neither."],
    ))

    add(P(
        "longest-interval-length", "Longest Interval", "easy", T, MI,
        "Print the length of the longest single interval, measured as `end - start`.",
        [p_intervals()], OUT_INT, lambda intervals: max(end - start for start, end in intervals),
        [([(1, 4), (2, 3)],), ([(5, 5)],)],
        g_intervals(),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6"],
        ["Compute end - start for each interval and keep the maximum.",
         "No sorting is required.",
         "A zero-length interval gives 0."],
    ))

    add(P(
        "count-non-overlapping-pairs", "Count Disjoint Pairs", "medium", T, IS,
        "Count the pairs of intervals that do not overlap at all. Touching intervals count as disjoint.",
        [p_intervals()], OUT_INT, lambda intervals: _count_disjoint_pairs(intervals),
        [([(1, 2), (3, 4), (1, 5)],), ([(1, 2)],)],
        g_intervals((1, 2, 3, 6, 12, 35, 90, 150)),
        ["1 <= m <= 2000", "0 <= start <= end <= 10^6",
         "the answer fits in a 64-bit signed integer"],
        ["Two intervals are disjoint when one ends at or before the other starts.",
         "The direct double loop is O(m^2) and passes at these limits.",
         "A sorted-by-end sweep with binary search is faster, but watch out for zero-length intervals, "
         "which satisfy the disjointness test in both directions and are easy to double count."],
        explanations=["Only [1,2] and [3,4] are disjoint.", "A single interval forms no pair."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _merge(intervals):
    ordered = sorted(intervals)
    merged: list[list[int]] = []
    for start, end in ordered:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def _merge_brute(intervals):
    items = [list(pair) for pair in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a[0] <= b[1] and b[0] <= a[1]:
                    items[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    items.pop(j)
                    changed = True
                    break
            if changed:
                break
    return sorted(items)


def _covered_length(intervals):
    return sum(end - start for start, end in _merge(intervals))


def _covered_brute(intervals):
    points = set()
    for start, end in intervals:
        for value in range(start, end):
            points.add(value)
    return len(points)


def _disjoint(rng, count):
    items = []
    current = rng.randint(0, 5)
    for _ in range(count):
        start = current + rng.randint(0, 4)
        end = start + rng.randint(0, 6)
        items.append((start, end))
        current = end + rng.randint(1, 4)
    return items


def _no_overlap(meetings):
    ordered = sorted(meetings)
    for index in range(1, len(ordered)):
        if ordered[index][0] < ordered[index - 1][1]:
            return False
    return True


def _min_rooms(meetings):
    starts = sorted(start for start, _ in meetings)
    ends = sorted(end for _, end in meetings)
    i = j = 0
    current = 0
    best = 0
    while i < len(starts):
        if starts[i] < ends[j]:
            current += 1
            best = max(best, current)
            i += 1
        else:
            current -= 1
            j += 1
    return best


def _min_rooms_brute(meetings):
    moments = sorted({start for start, _ in meetings})
    best = 0
    for moment in moments:
        count = sum(1 for start, end in meetings if start <= moment < end or (start == end == moment))
        best = max(best, count)
    return best


def _max_overlap_inclusive(intervals):
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end + 1, -1))
    events.sort()
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


def _max_overlap_brute(intervals):
    points = sorted({value for pair in intervals for value in pair})
    best = 0
    for point in points:
        count = sum(1 for start, end in intervals if start <= point <= end)
        best = max(best, count)
    return best


def _max_non_overlapping(intervals):
    ordered = sorted(intervals, key=lambda pair: pair[1])
    count = 0
    last_end = None
    for start, end in ordered:
        if last_end is None or start >= last_end:
            count += 1
            last_end = end
    return count


def _intersection_length(a, b):
    i = j = 0
    total = 0
    while i < len(a) and j < len(b):
        low = max(a[i][0], b[j][0])
        high = min(a[i][1], b[j][1])
        if high > low:
            total += high - low
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return total


def _intersection_brute(a, b):
    first = set()
    for start, end in a:
        for value in range(start, end):
            first.add(value)
    second = set()
    for start, end in b:
        for value in range(start, end):
            second.add(value)
    return len(first & second)


def _count_disjoint_pairs(intervals):
    total = 0
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            a, b = intervals[i], intervals[j]
            if a[1] <= b[0] or b[1] <= a[0]:
                total += 1
    return total
