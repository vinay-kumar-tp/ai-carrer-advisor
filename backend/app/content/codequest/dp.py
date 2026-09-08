"""Dynamic programming."""

from __future__ import annotations

import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    P,
    Param,
    STR,
    ints,
    p_int,
    p_nums,
    word,
)

T = ["Dynamic Programming"]
LIN = ["Fibonacci / Linear DP"]
KNAP = ["0/1 Knapsack (DP)"]
GEN = ["Dynamic Programming"]
SIZES = (1, 2, 3, 5, 9, 16, 35, 80)
SMALL = "abc"

MOD = 1_000_000_007


def g_nums(lo=-30, hi=30, sizes=SIZES):
    def gen(rng: random.Random):
        return [(ints(rng, n, lo, hi),) for n in sizes]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "climbing-stairs", "Climbing Stairs", "easy", T, LIN,
        f"You climb a staircase of `n` steps taking 1 or 2 steps at a time. Print the number of distinct "
        f"ways to reach the top, modulo `{MOD}`.",
        [p_int("n", "number of steps")], OUT_INT, lambda n: _climb(n, (1, 2)),
        [(4,), (1,)],
        lambda rng: [(rng.randint(1, 200000),) for _ in range(8)],
        ["1 <= n <= 10^6"],
        ["ways(n) = ways(n-1) + ways(n-2), which is the Fibonacci recurrence.",
         "Iterate from the bottom keeping only the last two values.",
         "Take the remainder at every addition.",
         "ways(1) = 1 and ways(2) = 2."],
        explanations=["1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2 gives 5.", "One step, one way."],
    ))

    add(P(
        "climbing-stairs-three-steps", "Climbing Stairs With Three Steps", "easy", T, LIN,
        f"You climb `n` steps taking 1, 2 or 3 steps at a time. Print the number of distinct ways modulo "
        f"`{MOD}`.",
        [p_int("n", "number of steps")], OUT_INT, lambda n: _climb(n, (1, 2, 3)),
        [(4,), (1,)],
        lambda rng: [(rng.randint(1, 200000),) for _ in range(8)],
        ["1 <= n <= 10^6"],
        ["Extend the recurrence to sum the previous three values.",
         "Keep three rolling variables instead of a full table.",
         "Seed the base cases carefully for n = 1, 2 and 3."],
        explanations=["Seven ways reach step 4.", "One way."],
    ))

    add(P(
        "min-cost-climbing-stairs", "Minimum Cost Climbing Stairs", "easy", T, LIN,
        "Each `cost[i]` is the price of stepping on stair `i`. You may start at index 0 or 1 and step 1 or "
        "2 stairs at a time. Print the cheapest total cost to move past the last stair.",
        [Param("cost", INT_LIST, "non-negative step costs")], OUT_INT,
        lambda cost: _min_cost_stairs(cost),
        [([10, 15, 20],), ([5, 5],)],
        lambda rng: [(ints(rng, n, 0, 40),) for n in (1, 2, 3, 6, 12, 35, 110, 260)],
        ["1 <= n <= 2000", "0 <= cost[i] <= 10^4"],
        ["dp[i] is the cheapest cost to reach stair i.",
         "dp[i] = cost[i] + min(dp[i-1], dp[i-2]).",
         "The answer is min(dp[n-1], dp[n-2]) because you step past the end.",
         "Two rolling values are enough."],
        explanations=["Start at index 1 and pay 15.", "Start at either stair and pay 5."],
    ))

    add(P(
        "house-robber-linear", "House Robber", "medium", T, LIN,
        "Each `nums[i]` is the loot in house `i`. You cannot rob two adjacent houses. Print the maximum "
        "loot.",
        [Param("nums", INT_LIST, "non-negative loot values")], OUT_INT,
        lambda nums: _rob(nums),
        [([2, 7, 9, 3, 1],), ([5],)],
        lambda rng: [(ints(rng, n, 0, 60),) for n in (1, 2, 3, 6, 12, 35, 110, 260)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^4"],
        ["At each house choose to rob it (adding dp[i-2]) or skip it (keeping dp[i-1]).",
         "dp[i] = max(dp[i-1], dp[i-2] + nums[i]).",
         "Two rolling variables replace the whole table.",
         "Greedily taking the largest values fails on [2,1,1,2]."],
        explanations=["Robbing houses 0, 2 and 4 gives 12.", "One house."],
        brute=lambda nums: _rob_brute(nums),
    ))

    add(P(
        "house-robber-circular", "House Robber In A Circle", "medium", T, LIN,
        "The houses are arranged in a circle, so the first and last are adjacent. You cannot rob two "
        "adjacent houses. Print the maximum loot.",
        [Param("nums", INT_LIST, "non-negative loot values")], OUT_INT,
        lambda nums: nums[0] if len(nums) == 1 else max(_rob(nums[:-1]), _rob(nums[1:])),
        [([2, 3, 2],), ([1, 2, 3, 1],)],
        lambda rng: [(ints(rng, n, 0, 60),) for n in (1, 2, 3, 6, 12, 35, 110, 200)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^4"],
        ["The first and last house can never both be robbed.",
         "So solve the linear problem twice: once excluding the last house, once excluding the first.",
         "Take the larger of the two answers.",
         "A single house is its own answer."],
        explanations=["Robbing house 1 alone gives 3.", "Robbing houses 0 and 2 gives 4."],
        brute=lambda nums: _rob_circular_brute(nums),
    ))

    add(P(
        "longest-increasing-subsequence", "Longest Increasing Subsequence", "medium", T, GEN,
        "Print the length of the longest strictly increasing subsequence of `nums`.",
        [p_nums()], OUT_INT, lambda nums: _lis(nums),
        [([10, 9, 2, 5, 3, 7, 101, 18],), ([7, 7, 7],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["The O(n^2) DP sets dp[i] to the best length ending at i.",
         "The O(n log n) method keeps the smallest possible tail for each length.",
         "Binary search that tails array for the first element >= the current value and replace it.",
         "Strictly increasing means equal values cannot extend a subsequence."],
        explanations=["2,3,7,101 has length 4.", "No strict increase exists."],
        brute=lambda nums: _lis_quadratic(nums),
    ))

    add(P(
        "longest-decreasing-subsequence", "Longest Decreasing Subsequence", "medium", T, GEN,
        "Print the length of the longest strictly decreasing subsequence of `nums`.",
        [p_nums()], OUT_INT, lambda nums: _lis([-v for v in nums]),
        [([9, 4, 3, 2, 5, 4, 3, 2],), ([1, 2, 3],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Negate every element and find the longest increasing subsequence.",
         "Or mirror the DP, comparing in the opposite direction.",
         "The answer is at least 1 for a non-empty array."],
        brute=lambda nums: _lis_quadratic([-v for v in nums]),
    ))

    add(P(
        "coin-change-min-coins", "Coin Change", "medium", T, KNAP,
        "Using unlimited coins of the given denominations, print the fewest coins that sum to `amount`, or "
        "`-1` if it cannot be made.",
        [Param("coins", INT_LIST, "positive coin values"), p_int("amount", "the target sum")], OUT_INT,
        lambda coins, amount: _coin_change(coins, amount),
        [([1, 2, 5], 11), ([2], 3)],
        lambda rng: [(rng.sample(range(1, 20), rng.randint(1, 5)), rng.randint(0, 200)) for _ in range(8)],
        ["1 <= number of coins <= 20", "1 <= coins[i] <= 10^4", "0 <= amount <= 10^4"],
        ["dp[x] is the fewest coins summing to x, starting from dp[0] = 0.",
         "For each x, try every coin c and consider dp[x-c] + 1.",
         "Use a sentinel like infinity for unreachable amounts.",
         "Greedily taking the largest coin fails for coins like [1,3,4] and amount 6."],
        explanations=["5+5+1 uses 3 coins.", "3 cannot be made from 2s."],
    ))

    add(P(
        "coin-change-count-ways", "Coin Change Combinations", "medium", T, KNAP,
        f"Using unlimited coins of the given denominations, print how many distinct multisets sum to "
        f"`amount`, modulo `{MOD}`.",
        [Param("coins", INT_LIST, "positive coin values"), p_int("amount", "the target sum")], OUT_INT,
        lambda coins, amount: _coin_ways(coins, amount),
        [([1, 2, 5], 5), ([2], 3)],
        lambda rng: [(rng.sample(range(1, 15), rng.randint(1, 4)), rng.randint(0, 120)) for _ in range(8)],
        ["1 <= number of coins <= 20", "1 <= coins[i] <= 10^4", "0 <= amount <= 10^4"],
        ["Loop coins on the outside and amounts on the inside.",
         "That ordering counts combinations rather than ordered sequences.",
         "Swapping the loops would count permutations instead — a classic trap.",
         "dp[0] = 1 because there is one way to make nothing."],
        explanations=["5, 1+2+2, 1+1+1+2, 1+1+1+1+1 gives 4.", "3 cannot be made."],
    ))

    add(P(
        "subset-sum-exists", "Subset Sum", "medium", T, KNAP,
        "Print `YES` if some subset of `nums` sums to exactly `target`, else `NO`.",
        [Param("nums", INT_LIST, "non-negative integers"), p_int("target")], OUT_BOOL,
        lambda nums, target: _subset_sum(nums, target),
        [([3, 34, 4, 12, 5, 2], 9), ([1, 2], 7)],
        lambda rng: [(ints(rng, n, 0, 20), rng.randint(0, 60)) for n in (1, 2, 3, 5, 9, 16, 30)],
        ["1 <= n <= 200", "0 <= nums[i] <= 1000", "0 <= target <= 10^4"],
        ["dp[x] is true when some subset sums to x, starting from dp[0] = true.",
         "For each element, iterate the sums downwards so it is used at most once.",
         "Iterating upwards would allow reusing an element, solving a different problem.",
         "target = 0 is always achievable with the empty subset."],
        explanations=["4+5 = 9.", "The total is only 3."],
    ))

    add(P(
        "partition-equal-subset-sum", "Partition Equal Subset Sum", "medium", T, KNAP,
        "Print `YES` if `nums` can be split into two subsets with equal sums, else `NO`.",
        [Param("nums", INT_LIST, "non-negative integers")], OUT_BOOL,
        lambda nums: sum(nums) % 2 == 0 and _subset_sum(nums, sum(nums) // 2),
        [([1, 5, 11, 5],), ([1, 2, 5],)],
        lambda rng: [(ints(rng, n, 0, 20),) for n in (1, 2, 3, 5, 9, 16, 30, 60)],
        ["1 <= n <= 200", "0 <= nums[i] <= 1000"],
        ["An odd total can never split evenly, so reject it immediately.",
         "Otherwise ask whether a subset sums to half the total.",
         "That is exactly the subset-sum problem.",
         "Iterate sums downwards to keep each element single-use."],
        explanations=["{1,5,5} and {11} both sum to 11.", "The total 8 splits, but no subset makes 4."],
    ))

    add(P(
        "knapsack-max-value", "0/1 Knapsack", "medium", T, KNAP,
        "Each item `i` has weight `weights[i]` and value `values[i]`. Print the greatest total value that "
        "fits within capacity `capacity`, using each item at most once.",
        [Param("weights", INT_LIST, "item weights"), Param("values", INT_LIST, "item values"),
         p_int("capacity", "the weight limit")], OUT_INT,
        lambda weights, values, capacity: _knapsack(weights, values, capacity),
        [([1, 3, 4, 5], [1, 4, 5, 7], 7), ([5], [10], 3)],
        lambda rng: [(lambda k: (ints(rng, k, 1, 15), ints(rng, k, 1, 40), rng.randint(0, 60)))(k)
                     for k in (1, 2, 3, 5, 9, 16, 30)],
        ["1 <= n <= 200", "1 <= weights[i] <= 1000", "1 <= values[i] <= 10^4", "0 <= capacity <= 10^4",
         "weights and values have the same length"],
        ["dp[w] is the best value achievable with capacity exactly w or less.",
         "Process items one at a time, iterating capacities downwards.",
         "The downward sweep is what enforces at most one copy of each item.",
         "Fractional greedy choices are wrong for 0/1 knapsack."],
        explanations=["Items of weight 3 and 4 give value 9.", "The item does not fit."],
        brute=lambda weights, values, capacity: _knapsack_brute(weights, values, capacity),
    ))

    add(P(
        "unbounded-knapsack-max-value", "Unbounded Knapsack", "medium", T, KNAP,
        "Each item may be used any number of times. Print the greatest total value fitting within "
        "capacity `capacity`.",
        [Param("weights", INT_LIST, "item weights"), Param("values", INT_LIST, "item values"),
         p_int("capacity", "the weight limit")], OUT_INT,
        lambda weights, values, capacity: _unbounded_knapsack(weights, values, capacity),
        [([1, 3, 4, 5], [10, 40, 50, 70], 8), ([5], [10], 3)],
        lambda rng: [(lambda k: (ints(rng, k, 1, 12), ints(rng, k, 1, 40), rng.randint(0, 60)))(k)
                     for k in (1, 2, 3, 5, 9, 16, 30)],
        ["1 <= n <= 200", "1 <= weights[i] <= 1000", "1 <= values[i] <= 10^4", "0 <= capacity <= 10^4"],
        ["The recurrence is the same as 0/1 knapsack but the capacity loop runs upwards.",
         "Sweeping upwards lets an item be reused within the same iteration.",
         "That single loop-direction change is the whole difference."],
        explanations=["Two items of weight 4 give 100.", "Nothing fits."],
    ))

    add(P(
        "rod-cutting-max-value", "Rod Cutting", "medium", T, KNAP,
        "A rod of length `n` can be cut into integer pieces, where `prices[i]` is the price of a piece of "
        "length `i+1`. Print the greatest total price obtainable.",
        [Param("prices", INT_LIST, "price of each length starting at 1"), p_int("n", "rod length")],
        OUT_INT, lambda prices, n: _rod_cutting(prices, n),
        [([1, 5, 8, 9], 4), ([3], 2)],
        lambda rng: [(lambda k: (ints(rng, k, 1, 30), rng.randint(1, 40)))(rng.randint(1, 10))
                     for _ in range(8)],
        ["1 <= |prices| <= 200", "1 <= prices[i] <= 10^4", "1 <= n <= 10^4"],
        ["This is unbounded knapsack where a piece of length L has weight L and value prices[L-1].",
         "dp[len] = max over L of prices[L-1] + dp[len-L].",
         "Only lengths up to min(n, |prices|) are usable."],
        explanations=["Two pieces of length 2 give 10.", "Two pieces of length 1 give 6."],
    ))

    add(P(
        "target-sum-ways", "Target Sum Assignments", "medium", T, KNAP,
        f"Assign a `+` or `-` sign to every element of `nums` so the signed total equals `target`. Print "
        f"the number of ways, modulo `{MOD}`.",
        [Param("nums", INT_LIST, "non-negative integers"), p_int("target")], OUT_INT,
        lambda nums, target: _target_sum(nums, target),
        [([1, 1, 1, 1, 1], 3), ([1], 5)],
        lambda rng: [(ints(rng, n, 0, 10), rng.randint(-20, 20)) for n in (1, 2, 3, 5, 9, 14, 18)],
        ["1 <= n <= 20", "0 <= nums[i] <= 1000", "-10^4 <= target <= 10^4"],
        ["Let P be the positive subset and N the negative one; then sum(P) - sum(N) = target.",
         "Since sum(P) + sum(N) = total, sum(P) = (total + target) / 2.",
         "So count subsets summing to that value — an ordinary subset-sum count.",
         "If (total + target) is negative or odd, the answer is 0."],
        explanations=["Five sign assignments reach 3.", "1 cannot reach 5."],
        brute=lambda nums, target: sum(
            1 for mask in range(1 << len(nums))
            if sum(nums[i] if mask >> i & 1 else -nums[i] for i in range(len(nums))) == target
        ),
    ))

    add(P(
        "max-sum-non-adjacent", "Maximum Non Adjacent Sum", "easy", T, LIN,
        "Print the largest sum of a subset of `nums` that never uses two adjacent positions. The empty "
        "subset is allowed, so the answer is never negative.",
        [p_nums()], OUT_INT, lambda nums: _max_non_adjacent(nums),
        [([3, 2, 7, 10],), ([-1, -2],)], g_nums(),
        ["1 <= n <= 2000", "-10^6 <= nums[i] <= 10^6"],
        ["Track the best sum including and excluding the current element.",
         "including = excluding_prev + nums[i]; excluding = max(including_prev, excluding_prev).",
         "Clamp at 0 so an all-negative array answers 0.",
         "This is the house-robber recurrence with negatives allowed."],
        explanations=["3 + 10 = 13.", "Taking nothing gives 0."],
        brute=lambda nums: _max_non_adjacent_brute(nums),
    ))

    add(P(
        "count-binary-strings-no-consecutive-ones", "Binary Strings Without Consecutive Ones", "medium",
        T, LIN,
        f"Print how many binary strings of length `n` contain no two consecutive `1`s, modulo `{MOD}`.",
        [p_int("n", "string length")], OUT_INT, lambda n: _no_consecutive_ones(n),
        [(3,), (1,)],
        lambda rng: [(rng.randint(1, 200000),) for _ in range(8)],
        ["1 <= n <= 10^6"],
        ["Count strings ending in 0 and ending in 1 separately.",
         "A string ending in 1 must have had a 0 before it.",
         "The totals follow the Fibonacci recurrence.",
         "n = 1 gives 2 and n = 2 gives 3."],
        explanations=["000,001,010,100,101 gives 5.", "0 and 1."],
    ))

    add(P(
        "unique-paths-grid", "Unique Paths", "easy", T, ["Grid / 2-D DP"],
        f"Print the number of distinct paths from the top-left to the bottom-right of an `r x c` grid, "
        f"moving only right or down, modulo `{MOD}`.",
        [p_int("r", "rows"), p_int("c", "columns")], OUT_INT,
        lambda r, c: _unique_paths(r, c),
        [(3, 3), (1, 5)],
        lambda rng: [(rng.randint(1, 400), rng.randint(1, 400)) for _ in range(8)],
        ["1 <= r, c <= 500"],
        ["dp[i][j] = dp[i-1][j] + dp[i][j-1], with the first row and column all 1.",
         "A single row of DP values suffices for O(c) space.",
         "The closed form is the binomial coefficient C(r+c-2, r-1)."],
        explanations=["Six paths cross a 3x3 grid.", "One path along a single row."],
    ))

    add(P(
        "longest-common-substring-length", "Longest Common Substring", "medium", T + ["Strings"], GEN,
        "Print the length of the longest contiguous string appearing in both `a` and `b`.",
        [Param("a", STR, "first string"), Param("b", STR, "second string")], OUT_INT,
        lambda a, b: _longest_common_substring(a, b),
        [("abcde", "abfce"), ("abc", "xyz")],
        lambda rng: [(word(rng, n, SMALL), word(rng, m, SMALL))
                     for n, m in ((1, 1), (2, 3), (5, 4), (9, 9), (18, 15), (40, 35), (80, 70))],
        ["1 <= |a|, |b| <= 500", "lowercase English letters only"],
        ["dp[i][j] is the length of the common suffix of the first i and j characters.",
         "Matching characters give dp[i-1][j-1] + 1; a mismatch resets to 0.",
         "Track the maximum cell value, not the corner — substrings must be contiguous.",
         "That reset is the only difference from longest common subsequence."],
        explanations=["ab has length 2.", "Nothing is shared."],
        brute=lambda a, b: max((length for i in range(len(a)) for length in range(1, len(a) - i + 1)
                                if a[i:i + length] in b), default=0),
    ))

    add(P(
        "count-distinct-subsequences-of-target", "Count Subsequence Occurrences", "hard",
        T + ["Strings"], GEN,
        f"Print how many distinct subsequences of `a` equal `b`, modulo `{MOD}`.",
        [Param("a", STR, "the source string"), Param("b", STR, "the target string")], OUT_INT,
        lambda a, b: _count_subsequences(a, b),
        [("rabbbit", "rabbit"), ("abc", "abcd")],
        lambda rng: [(word(rng, n, "ab"), word(rng, m, "ab"))
                     for n, m in ((1, 1), (3, 2), (5, 3), (9, 4), (16, 5), (30, 6), (60, 8))],
        ["1 <= |a| <= 500", "1 <= |b| <= 500", "lowercase English letters only"],
        ["dp[i][j] counts ways to form the first j characters of b from the first i of a.",
         "Always inherit dp[i-1][j] (skip a[i]); when the characters match also add dp[i-1][j-1].",
         "dp[i][0] = 1 because the empty target is always formed one way.",
         "Positions matter, so identical subsequences from different indices count separately."],
        explanations=["Three ways drop one b.", "b is longer than a."],
    ))

    add(P(
        "max-square-of-ones", "Largest Square Of Ones", "medium", T + ["Matrix"], ["Grid / 2-D DP"],
        "The grid `g` holds `0` and `1` characters. Print the side length of the largest square made "
        "entirely of `1`s.",
        [Param("g", "grid", "rows of 0/1 characters")], OUT_INT,
        lambda g: _max_square(g),
        [(["10100", "10111", "11111", "10010"],), (["0"],)],
        lambda rng: [([("".join("1" if rng.random() < 0.65 else "0" for _ in range(c))) for _ in range(r)],)
                     for r, c in ((1, 1), (1, 4), (4, 1), (3, 3), (5, 5), (8, 7), (14, 12))],
        ["1 <= r, c <= 200", "each character is 0 or 1"],
        ["dp[i][j] is the side of the largest square whose bottom-right corner is that cell.",
         "For a 1, it equals 1 + min of the cells above, to the left, and diagonally up-left.",
         "A 0 forces dp to 0.",
         "Track the maximum dp value, then that is the answer."],
        explanations=["A 2x2 block of ones exists.", "There are no ones."],
    ))

    add(P(
        "number-of-ways-to-decode-digits", "Decode Ways", "medium", T + ["Strings"], LIN,
        f"The string `s` holds digits. Each letter A-Z maps to 1-26. Print how many ways `s` decodes into "
        f"letters, modulo `{MOD}`. A leading zero in any chunk is invalid.",
        [Param("s", STR, "digits only")], OUT_INT, lambda s: _decode_ways(s),
        [("226",), ("06",)],
        lambda rng: [("".join(rng.choice("0123") for _ in range(n)) or "1",)
                     for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= |s| <= 2000", "s contains digits only"],
        ["dp[i] counts decodings of the first i characters.",
         "Add dp[i-1] when the single digit is 1-9, and dp[i-2] when the two-digit chunk is 10-26.",
         "A '0' can only appear as part of 10 or 20.",
         "dp[0] = 1 for the empty prefix."],
        explanations=["BZ, VF and BBF give 3.", "06 has no valid decoding."],
    ))

    add(P(
        "matrix-chain-min-multiplications", "Matrix Chain Multiplication", "hard", T, GEN,
        "The array `dims` describes a chain of matrices where matrix `i` has shape "
        "`dims[i] x dims[i+1]`. Print the fewest scalar multiplications needed to multiply the whole chain.",
        [Param("dims", INT_LIST, "the chain dimensions, length n+1 for n matrices")], OUT_INT,
        lambda dims: _matrix_chain(dims),
        [([1, 2, 3, 4],), ([5, 10],)],
        lambda rng: [(ints(rng, n, 1, 20),) for n in (2, 3, 4, 6, 9, 14, 22, 40)],
        ["2 <= |dims| <= 200", "1 <= dims[i] <= 500",
         "the answer fits in a 64-bit signed integer"],
        ["dp[i][j] is the cheapest way to multiply matrices i through j.",
         "Try every split point k and combine dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1].",
         "Iterate by increasing chain length so the sub-answers are ready.",
         "A single matrix costs 0."],
        explanations=["18 multiplications suffice.", "A single matrix needs none."],
    ))

    add(P(
        "egg-drop-min-trials", "Egg Drop", "hard", T, GEN,
        "With `eggs` identical eggs and `floors` floors, print the minimum number of trials that always "
        "determines the critical floor in the worst case.",
        [p_int("eggs", "number of eggs"), p_int("floors", "number of floors")], OUT_INT,
        lambda eggs, floors: _egg_drop(eggs, floors),
        [(2, 10), (1, 5)],
        lambda rng: [(rng.randint(1, 8), rng.randint(0, 200)) for _ in range(8)],
        ["1 <= eggs <= 20", "0 <= floors <= 2000"],
        ["Flip the question: with e eggs and t trials, how many floors can you cover?",
         "cover(e, t) = cover(e-1, t-1) + cover(e, t-1) + 1.",
         "Increase t until the coverage reaches the floor count.",
         "With one egg you must test floors one by one, needing `floors` trials."],
        explanations=["Four trials suffice for 2 eggs and 10 floors.", "One egg needs 5 trials."],
    ))

    add(P(
        "word-break-possible", "Word Break", "medium", T + ["Strings"], GEN,
        "Print `YES` if `s` can be split into a sequence of words all drawn from `dictWords` (words may "
        "repeat), else `NO`.",
        [Param("s", STR, "the string to split"),
         Param("dictWords", "str[]", "the allowed words")], OUT_BOOL,
        lambda s, dictWords: _word_break(s, dictWords),
        [("leetcode", ["leet", "code"]), ("catsand", ["cats", "dog"])],
        lambda rng: [(word(rng, n, "ab"), [word(rng, rng.randint(1, 3), "ab") for _ in range(rng.randint(1, 4))])
                     for n in (1, 2, 4, 8, 15, 30, 60)],
        ["1 <= |s| <= 500", "1 <= number of words <= 100", "1 <= |word| <= 100"],
        ["dp[i] is true when the first i characters can be segmented.",
         "For each i, try every word that could end there and check dp[i - len(word)].",
         "Put the dictionary in a hash set for O(1) lookups.",
         "dp[0] = true for the empty prefix."],
        explanations=["leet + code.", "sand is not in the dictionary."],
    ))

    add(P(
        "min-jumps-to-end", "Minimum Jumps To End", "medium", T + ["Greedy", "Arrays"], GEN,
        "From index `i` you may jump to any index up to `i + nums[i]`. Print the fewest jumps to reach "
        "the last index, or `-1` if it is unreachable.",
        [Param("nums", INT_LIST, "non-negative jump lengths")], OUT_INT,
        lambda nums: _min_jumps(nums),
        [([2, 3, 1, 1, 4],), ([3, 2, 1, 0, 4],)],
        lambda rng: [(ints(rng, n, 0, 5),) for n in (1, 2, 3, 6, 12, 35, 110, 260)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 1000"],
        ["A greedy sweep tracks the current jump's reach and the best reach discovered.",
         "When you pass the current reach, take a jump and extend to the best reach.",
         "If the best reach never passes the current index, the end is unreachable.",
         "This is O(n), better than the O(n^2) DP."],
        explanations=["Jump 0->1->4.", "Index 3 holds 0 and blocks the path."],
        brute=lambda nums: _min_jumps_bfs(nums),
    ))

    add(P(
        "count-palindromic-partitions-min-cuts", "Minimum Palindrome Partitions", "hard",
        T + ["Strings"], GEN,
        "Print the minimum number of cuts needed to split `s` so every part is a palindrome.",
        [Param("s", STR, "lowercase letters")], OUT_INT,
        lambda s: _min_palindrome_cuts(s),
        [("aab",), ("aaa",)],
        lambda rng: [(word(rng, n, "ab"),) for n in (1, 2, 3, 5, 9, 18, 40, 90)],
        ["1 <= |s| <= 500", "s contains lowercase English letters only"],
        ["Precompute an is-palindrome table for every substring in O(n^2).",
         "Then dp[i] is the fewest cuts for the first i characters.",
         "dp[i] = min over j of dp[j] + 1 whenever s[j..i-1] is a palindrome.",
         "A string that is already a palindrome needs 0 cuts."],
        explanations=["aa | b needs one cut.", "aaa is already a palindrome."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _climb(n, steps):
    dp = [0] * (n + 1)
    dp[0] = 1
    for value in range(1, n + 1):
        total = 0
        for step in steps:
            if value - step >= 0:
                total += dp[value - step]
        dp[value] = total % MOD
    return dp[n]


def _min_cost_stairs(cost):
    if len(cost) == 1:
        return cost[0]
    previous, current = cost[0], cost[1]
    for index in range(2, len(cost)):
        previous, current = current, cost[index] + min(previous, current)
    return min(previous, current)


def _rob(nums):
    include = 0
    exclude = 0
    for value in nums:
        include, exclude = exclude + value, max(include, exclude)
    return max(include, exclude)


BRUTE_LIMIT = 18  # 2^n enumeration is only affordable for small n


def _rob_table(nums):
    """Independent O(n) formulation used to cross-check the rolling-variable version."""
    n = len(nums)
    dp = [0] * (n + 1)
    dp[1] = nums[0]
    for index in range(2, n + 1):
        dp[index] = max(dp[index - 1], dp[index - 2] + nums[index - 1])
    return dp[n]


def _rob_brute(nums):
    n = len(nums)
    if n > BRUTE_LIMIT:
        return _rob_table(nums)
    best = 0
    for mask in range(1 << n):
        if mask & (mask << 1):
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def _rob_circular_brute(nums):
    n = len(nums)
    if n == 1:
        return nums[0]
    if n > BRUTE_LIMIT:
        return max(_rob_table(nums[:-1]), _rob_table(nums[1:]))
    best = 0
    for mask in range(1 << n):
        if mask & (mask << 1):
            continue
        if (mask & 1) and (mask >> (n - 1)) & 1:
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def _lis(nums):
    import bisect

    tails: list[int] = []
    for value in nums:
        position = bisect.bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)


def _lis_quadratic(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def _coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value and dp[value - coin] + 1 < dp[value]:
                dp[value] = dp[value - coin] + 1
    return -1 if dp[amount] == INF else int(dp[amount])


def _coin_ways(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for value in range(coin, amount + 1):
            dp[value] = (dp[value] + dp[value - coin]) % MOD
    return dp[amount]


def _subset_sum(nums, target):
    reachable = [False] * (target + 1)
    reachable[0] = True
    for value in nums:
        if value > target:
            continue
        for total in range(target, value - 1, -1):
            if reachable[total - value]:
                reachable[total] = True
    return reachable[target]


def _knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for limit in range(capacity, weight - 1, -1):
            dp[limit] = max(dp[limit], dp[limit - weight] + value)
    return dp[capacity]


def _knapsack_brute(weights, values, capacity):
    n = len(weights)
    if n > BRUTE_LIMIT:
        # Independent 2-D table instead of the rolling 1-D version.
        table = [[0] * (capacity + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for limit in range(capacity + 1):
                table[i][limit] = table[i - 1][limit]
                if weights[i - 1] <= limit:
                    table[i][limit] = max(table[i][limit],
                                          table[i - 1][limit - weights[i - 1]] + values[i - 1])
        return table[n][capacity]
    best = 0
    for mask in range(1 << n):
        total_weight = sum(weights[i] for i in range(n) if mask >> i & 1)
        if total_weight <= capacity:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def _unbounded_knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for limit in range(1, capacity + 1):
        for weight, value in zip(weights, values):
            if weight <= limit:
                dp[limit] = max(dp[limit], dp[limit - weight] + value)
    return dp[capacity]


def _rod_cutting(prices, n):
    dp = [0] * (n + 1)
    for length in range(1, n + 1):
        for piece in range(1, min(length, len(prices)) + 1):
            dp[length] = max(dp[length], prices[piece - 1] + dp[length - piece])
    return dp[n]


def _target_sum(nums, target):
    total = sum(nums)
    needed = total + target
    if needed < 0 or needed % 2:
        return 0
    goal = needed // 2
    if goal > total:
        return 0
    dp = [0] * (goal + 1)
    dp[0] = 1
    for value in nums:
        for amount in range(goal, value - 1, -1):
            dp[amount] = (dp[amount] + dp[amount - value]) % MOD
    return dp[goal]


def _max_non_adjacent(nums):
    include = 0
    exclude = 0
    for value in nums:
        include, exclude = exclude + value, max(include, exclude)
    return max(0, include, exclude)


def _max_non_adjacent_brute(nums):
    n = len(nums)
    if n > BRUTE_LIMIT:
        dp = [0] * (n + 2)
        for index in range(n - 1, -1, -1):
            dp[index] = max(dp[index + 1], nums[index] + dp[index + 2])
        return max(0, dp[0])
    best = 0
    for mask in range(1 << n):
        if mask & (mask << 1):
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


def _no_consecutive_ones(n):
    ending_zero, ending_one = 1, 1
    for _ in range(n - 1):
        ending_zero, ending_one = (ending_zero + ending_one) % MOD, ending_zero
    return (ending_zero + ending_one) % MOD


def _unique_paths(r, c):
    row = [1] * c
    for _ in range(1, r):
        for column in range(1, c):
            row[column] = (row[column] + row[column - 1]) % MOD
    return row[c - 1]


def _longest_common_substring(a, b):
    previous = [0] * (len(b) + 1)
    best = 0
    for x in a:
        current = [0] * (len(b) + 1)
        for j, y in enumerate(b, start=1):
            if x == y:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def _count_subsequences(a, b):
    dp = [0] * (len(b) + 1)
    dp[0] = 1
    for x in a:
        for j in range(len(b), 0, -1):
            if b[j - 1] == x:
                dp[j] = (dp[j] + dp[j - 1]) % MOD
    return dp[len(b)]


def _max_square(g):
    rows, cols = len(g), len(g[0])
    dp = [[0] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == "1":
                if r == 0 or c == 0:
                    dp[r][c] = 1
                else:
                    dp[r][c] = 1 + min(dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1])
                best = max(best, dp[r][c])
    return best


def _decode_ways(s):
    previous, current = 1, 1 if s[0] != "0" else 0
    for index in range(1, len(s)):
        total = 0
        if s[index] != "0":
            total += current
        two = int(s[index - 1:index + 1])
        if 10 <= two <= 26:
            total += previous
        previous, current = current, total % MOD
    return current


def _matrix_chain(dims):
    count = len(dims) - 1
    dp = [[0] * count for _ in range(count)]
    for length in range(2, count + 1):
        for i in range(count - length + 1):
            j = i + length - 1
            best = None
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                best = cost if best is None else min(best, cost)
            dp[i][j] = best
    return dp[0][count - 1]


def _egg_drop(eggs, floors):
    if floors == 0:
        return 0
    covered = [0] * (eggs + 1)
    trials = 0
    while covered[eggs] < floors:
        trials += 1
        for count in range(eggs, 0, -1):
            covered[count] = covered[count] + covered[count - 1] + 1
    return trials


def _word_break(s, dictWords):
    allowed = set(dictWords)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for end in range(1, len(s) + 1):
        for start in range(end):
            if dp[start] and s[start:end] in allowed:
                dp[end] = True
                break
    return dp[len(s)]


def _min_jumps(nums):
    n = len(nums)
    if n == 1:
        return 0
    jumps = 0
    current_reach = 0
    best_reach = 0
    for index in range(n - 1):
        best_reach = max(best_reach, index + nums[index])
        if index == current_reach:
            if best_reach <= index:
                return -1
            jumps += 1
            current_reach = best_reach
            if current_reach >= n - 1:
                return jumps
    return jumps if current_reach >= n - 1 else -1


def _min_jumps_bfs(nums):
    from collections import deque

    n = len(nums)
    distance = [-1] * n
    distance[0] = 0
    queue = deque([0])
    while queue:
        index = queue.popleft()
        for step in range(1, nums[index] + 1):
            nxt = index + step
            if nxt < n and distance[nxt] == -1:
                distance[nxt] = distance[index] + 1
                queue.append(nxt)
    return distance[n - 1]


def _min_palindrome_cuts(s):
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for right in range(n):
        for left in range(right, -1, -1):
            if s[left] == s[right] and (right - left < 2 or is_pal[left + 1][right - 1]):
                is_pal[left][right] = True
    dp = [0] * (n + 1)
    for end in range(1, n + 1):
        if is_pal[0][end - 1]:
            dp[end] = 0
            continue
        best = None
        for start in range(1, end):
            if is_pal[start][end - 1]:
                candidate = dp[start] + 1
                best = candidate if best is None else min(best, candidate)
        dp[end] = best if best is not None else end - 1
    return dp[n]
