"""Bit manipulation."""

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
)

T = ["Bit Manipulation"]
B = ["Bit Manipulation"]


def g_int(lo, hi, count=8):
    def gen(rng: random.Random):
        return [(rng.randint(lo, hi),) for _ in range(count)]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "get-ith-bit", "Get Bit", "easy", T, B,
        "Print the value (`0` or `1`) of bit `i` of the non-negative integer `n`, counting from bit 0 "
        "as the least significant.",
        [p_int("n"), p_int("i", "bit position")], OUT_INT,
        lambda n, i: (n >> i) & 1,
        [(13, 2), (8, 0)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 30)) for _ in range(8)],
        ["0 <= n <= 10^9", "0 <= i <= 30"],
        ["Shift n right by i so the target bit reaches position 0.",
         "Then mask with 1 to isolate it.",
         "Equivalently test whether n & (1 << i) is non-zero."],
        explanations=["13 is 1101; bit 2 is 1.", "8 is 1000; bit 0 is 0."],
    ))

    add(P(
        "set-ith-bit", "Set Bit", "easy", T, B,
        "Print the value of `n` after setting bit `i` to 1.",
        [p_int("n"), p_int("i")], OUT_INT, lambda n, i: n | (1 << i),
        [(8, 1), (13, 2)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 30)) for _ in range(8)],
        ["0 <= n <= 10^9", "0 <= i <= 30"],
        ["Build a mask with a single 1 at position i using 1 << i.",
         "OR the mask with n.",
         "Setting an already-set bit changes nothing."],
        explanations=["1000 becomes 1010, which is 10.", "Bit 2 of 1101 is already set."],
    ))

    add(P(
        "clear-ith-bit", "Clear Bit", "easy", T, B,
        "Print the value of `n` after clearing bit `i` to 0.",
        [p_int("n"), p_int("i")], OUT_INT, lambda n, i: n & ~(1 << i),
        [(13, 2), (8, 1)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 30)) for _ in range(8)],
        ["0 <= n <= 10^9", "0 <= i <= 30"],
        ["Make the mask 1 << i, then invert it.",
         "AND the inverted mask with n.",
         "Clearing an already-clear bit changes nothing."],
        explanations=["1101 becomes 1001, which is 9.", "Bit 1 of 1000 is already 0."],
    ))

    add(P(
        "toggle-ith-bit", "Toggle Bit", "easy", T, B,
        "Print the value of `n` after flipping bit `i`.",
        [p_int("n"), p_int("i")], OUT_INT, lambda n, i: n ^ (1 << i),
        [(13, 1), (13, 0)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 30)) for _ in range(8)],
        ["0 <= n <= 10^9", "0 <= i <= 30"],
        ["XOR with a single-bit mask flips exactly that bit.",
         "XOR is its own inverse, so toggling twice restores the value.",
         "Build the mask with 1 << i."],
    ))

    add(P(
        "lowest-set-bit-value", "Lowest Set Bit", "easy", T, B,
        "Print the value of the lowest set bit of the positive integer `n` (for example 12 gives 4). "
        "Print `0` if `n` is 0.",
        [p_int("n")], OUT_INT, lambda n: n & -n if n else 0,
        [(12,), (0,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["n & -n isolates the lowest set bit thanks to two's complement.",
         "Equivalently n & ~(n-1).",
         "Handle n = 0 separately since it has no set bits."],
        explanations=["12 is 1100; the lowest set bit is 100 = 4.", "Zero has no set bits."],
    ))

    add(P(
        "highest-set-bit-position", "Highest Set Bit Position", "easy", T, B,
        "Print the 0-based position of the highest set bit of the positive integer `n`. Print `-1` if "
        "`n` is 0.",
        [p_int("n")], OUT_INT, lambda n: n.bit_length() - 1 if n else -1,
        [(12,), (1,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Shift right until the value becomes 0, counting the shifts.",
         "The answer is floor(log2(n)) for n > 0.",
         "Zero has no set bit, so report -1."],
        explanations=["12 is 1100; the top bit sits at position 3.", "1 has its bit at position 0."],
    ))

    add(P(
        "clear-lowest-set-bit", "Clear Lowest Set Bit", "easy", T, B,
        "Print the value of `n` after removing its lowest set bit.",
        [p_int("n")], OUT_INT, lambda n: n & (n - 1) if n else 0,
        [(12,), (7,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["n & (n-1) clears exactly the lowest set bit.",
         "Subtracting 1 flips the lowest set bit and everything below it.",
         "This trick powers Brian Kernighan's popcount loop."],
        explanations=["1100 becomes 1000 = 8.", "111 becomes 110 = 6."],
    ))

    add(P(
        "count-bits-to-flip", "Bits To Flip", "easy", T, B,
        "Print how many bit positions differ between the non-negative integers `a` and `b` (their "
        "Hamming distance).",
        [p_int("a"), p_int("b")], OUT_INT, lambda a, b: bin(a ^ b).count("1"),
        [(10, 20), (7, 7)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 10 ** 9)) for _ in range(8)],
        ["0 <= a, b <= 10^9"],
        ["XOR keeps a 1 exactly where the two numbers differ.",
         "So the answer is the popcount of a ^ b.",
         "Identical numbers give 0."],
        explanations=["10^20 = 30, which has four set bits.", "Equal numbers differ nowhere."],
    ))

    add(P(
        "swap-two-numbers-xor", "Swap Without Temp", "easy", T, B,
        "Swap `a` and `b` without using a third variable, then print the two values in their new order.",
        [p_int("a"), p_int("b")], OUT_INT_LIST, lambda a, b: [b, a],
        [(3, 7), (5, 5)],
        lambda rng: [(rng.randint(-10 ** 6, 10 ** 6), rng.randint(-10 ** 6, 10 ** 6)) for _ in range(8)],
        ["-10^9 <= a, b <= 10^9"],
        ["a ^= b; b ^= a; a ^= b performs the swap with XOR.",
         "Addition and subtraction also work but can overflow.",
         "Swapping equal values is a no-op."],
        out_desc="Print the swapped values as `a b`.",
    ))

    add(P(
        "count-set-bits-range", "Set Bits Up To N", "medium", T + ["Dynamic Programming"], B,
        "Print the total number of set bits across all integers from `0` to `n` inclusive.",
        [p_int("n")], OUT_INT, lambda n: sum(bin(v).count("1") for v in range(n + 1)),
        [(5,), (0,)],
        lambda rng: [(rng.randint(0, 40000),) for _ in range(8)],
        ["0 <= n <= 10^5"],
        ["A direct loop with a popcount per value is O(n log n) and passes here.",
         "A DP is faster: bits(i) = bits(i >> 1) + (i & 1).",
         "That reuses the answer for a smaller number in O(1) per value."],
        explanations=["0,1,10,11,100,101 have 0+1+1+2+1+2 = 7 set bits.", "Zero contributes nothing."],
    ))

    add(P(
        "single-number-appears-once-thrice", "Single Number Among Triples", "medium", T + ["Arrays"], B,
        "Every value in `nums` appears exactly three times except one, which appears once. Print that "
        "value.",
        [Param("nums", INT_LIST, "all values tripled except one")], OUT_INT,
        lambda nums: _single_among_triples(nums),
        [([2, 2, 3, 2],), ([5],)],
        lambda rng: [(_triple_case(rng, k),) for k in (0, 1, 2, 4, 8, 20, 50)],
        ["n = 3k + 1 and 1 <= n <= 2000", "1 <= nums[i] <= 10^6"],
        ["Plain XOR fails because three copies do not cancel.",
         "Count each bit position modulo 3 across all numbers.",
         "Positions whose count is not divisible by 3 belong to the lone value.",
         "A hash map of counts is the simpler alternative."],
        brute=lambda nums: next(x for x in nums if nums.count(x) == 1),
    ))

    add(P(
        "two-single-numbers", "Two Single Numbers", "medium", T + ["Arrays"], B,
        "Every value in `nums` appears exactly twice except two values that appear once. Print those "
        "two values in ascending order.",
        [Param("nums", INT_LIST, "all values paired except two")], OUT_INT_LIST,
        lambda nums: _two_singles(nums),
        [([1, 2, 1, 3, 2, 5],), ([4, 7],)],
        lambda rng: [(_two_single_case(rng, k),) for k in (0, 1, 2, 5, 10, 30, 60)],
        ["n is even and 2 <= n <= 2000", "1 <= nums[i] <= 10^6", "exactly two values appear once"],
        ["XOR everything to get x ^ y, where x and y are the two lone values.",
         "Any set bit of that XOR distinguishes them.",
         "Split the array by that bit and XOR each half separately.",
         "Sort the two results before printing."],
        explanations=["3 and 5 appear once.", "Both values appear once."],
        brute=lambda nums: sorted(x for x in set(nums) if nums.count(x) == 1),
    ))

    add(P(
        "subset-count-bitmask", "Count Subsets With Sum", "medium",
        T + ["Dynamic Programming", "Arrays"], ["Subsets / Backtracking"],
        "Count the subsets of `nums` (including the empty subset) whose elements sum to `target`.",
        [p_nums(), p_int("target", "required subset sum")], OUT_INT,
        lambda nums, target: _count_subsets_with_sum(nums, target),
        [([1, 2, 3], 3), ([1, 1], 1)],
        lambda rng: [(ints(rng, n, 0, 8), rng.randint(0, 20)) for n in (1, 2, 3, 5, 8, 12, 16)],
        ["1 <= n <= 20", "0 <= nums[i] <= 100", "0 <= target <= 2000"],
        ["With n <= 20 you can enumerate all 2^n masks and sum the chosen elements.",
         "A subset-sum DP counts them in O(n * target) instead.",
         "The empty subset sums to 0, so target = 0 always has at least one subset.",
         "Duplicated values create distinct subsets at distinct index sets."],
        explanations=["{3} and {1,2} both sum to 3.", "Either 1 alone works, giving 2 subsets."],
        brute=lambda nums, target: sum(
            1 for mask in range(1 << len(nums))
            if sum(nums[i] for i in range(len(nums)) if mask >> i & 1) == target
        ),
    ))

    add(P(
        "generate-all-subsets-count", "Count Distinct Subset Sums", "medium",
        T + ["Arrays"], ["Subsets / Backtracking"],
        "Print how many distinct sums can be formed by subsets of `nums`, including the empty subset "
        "(which sums to 0).",
        [p_nums()], OUT_INT, lambda nums: len(_subset_sums(nums)),
        [([1, 2, 3],), ([2, 2],)],
        lambda rng: [(ints(rng, n, 0, 10),) for n in (1, 2, 3, 5, 8, 12, 16)],
        ["1 <= n <= 20", "0 <= nums[i] <= 100"],
        ["Maintain a set of reachable sums and extend it with each element.",
         "For each existing sum s, add s + nums[i].",
         "This is the classic subset-sum reachability idea.",
         "Do not forget 0, which the empty subset provides."],
        explanations=["Sums 0,1,2,3,4,5,6 give 7 distinct values.", "Sums are 0,2,4 giving 3."],
        brute=lambda nums: len({sum(nums[i] for i in range(len(nums)) if mask >> i & 1)
                                for mask in range(1 << len(nums))}),
    ))

    add(P(
        "xor-of-range", "XOR From 1 To N", "easy", T, B,
        "Print the XOR of all integers from `1` to `n`.",
        [p_int("n")], OUT_INT, lambda n: _xor_upto(n),
        [(5,), (1,)],
        lambda rng: [(rng.randint(1, 10 ** 9),) for _ in range(8)],
        ["1 <= n <= 10^9"],
        ["The result follows a period-4 pattern in n.",
         "n % 4 == 0 gives n, 1 gives 1, 2 gives n+1, 3 gives 0.",
         "A loop would be far too slow at the upper limit."],
        explanations=["1^2^3^4^5 = 1.", "Just 1."],
        brute=lambda n: _xor_upto_loop(n) if n <= 100000 else _xor_upto(n),
    ))

    add(P(
        "xor-of-array-elements", "XOR Of Array", "easy", T + ["Arrays"], B,
        "Print the XOR of every element of `nums`.",
        [p_nums()], OUT_INT, lambda nums: _xor_list(nums),
        [([1, 2, 3],), ([7],)],
        lambda rng: [(ints(rng, n, 0, 10 ** 6),) for n in (1, 2, 5, 12, 40, 120, 300)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^9"],
        ["Fold XOR across the array starting from 0.",
         "XOR is associative and commutative, so order does not matter.",
         "Equal values cancel in pairs."],
    ))

    add(P(
        "reverse-bits-32", "Reverse Bits", "easy", T, B,
        "Treat `n` as a 32-bit unsigned integer, reverse its bits and print the resulting value.",
        [p_int("n")], OUT_INT, lambda n: int(format(n, "032b")[::-1], 2),
        [(1,), (0,)],
        lambda rng: [(rng.randint(0, 2 ** 31 - 1),) for _ in range(8)],
        ["0 <= n < 2^31"],
        ["Pull bits off the bottom of n and push them onto the bottom of the result, shifting left.",
         "Run the loop exactly 32 times so leading zeros are reversed too.",
         "Bit 0 must end up at position 31."],
        explanations=["Bit 0 moves to bit 31, giving 2147483648.", "Zero stays zero."],
    ))

    add(P(
        "count-different-bits-pairs", "Total Pairwise Bit Differences", "medium", T + ["Arrays"], B,
        "For every ordered pair of indices `(i, j)`, sum the number of differing bits between "
        "`nums[i]` and `nums[j]`. Print the total.",
        [p_nums()], OUT_INT, lambda nums: _sum_bit_differences(nums),
        [([1, 3, 5],), ([2, 2],)],
        lambda rng: [(ints(rng, n, 0, 1000),) for n in (1, 2, 3, 6, 12, 40, 100)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^9", "the answer fits in a 64-bit signed integer"],
        ["Handle each bit position independently.",
         "If k numbers have that bit set, the position contributes 2 * k * (n - k) ordered pairs.",
         "Sum over all 31 positions for O(31n).",
         "Ordered pairs count (i,j) and (j,i) separately."],
        brute=lambda nums: sum(bin(a ^ b).count("1") for a in nums for b in nums),
    ))

    add(P(
        "add-without-plus", "Add Without Plus", "medium", T, B,
        "Print the sum of the non-negative integers `a` and `b` computed using only bitwise operations.",
        [p_int("a"), p_int("b")], OUT_INT, lambda a, b: a + b,
        [(3, 5), (0, 0)],
        lambda rng: [(rng.randint(0, 10 ** 6), rng.randint(0, 10 ** 6)) for _ in range(8)],
        ["0 <= a, b <= 10^9"],
        ["a ^ b gives the sum ignoring carries; (a & b) << 1 gives the carries.",
         "Loop, feeding the carry back in, until the carry becomes 0.",
         "The loop terminates because the carry shifts left each round."],
        explanations=["3 + 5 = 8.", "0 + 0 = 0."],
    ))

    add(P(
        "multiply-by-power-of-two", "Multiply By Power Of Two", "easy", T, B,
        "Print `n` multiplied by `2^k` using a bit shift.",
        [p_int("n"), p_int("k")], OUT_INT, lambda n, k: n << k,
        [(5, 3), (1, 0)],
        lambda rng: [(rng.randint(-10 ** 6, 10 ** 6), rng.randint(0, 20)) for _ in range(8)],
        ["-10^9 <= n <= 10^9", "0 <= k <= 30", "the answer fits in a 64-bit signed integer"],
        ["Shifting left by k multiplies by 2^k.",
         "A shift of 0 leaves the value unchanged.",
         "Use a 64-bit type so large shifts do not overflow."],
        explanations=["5 << 3 = 40.", "Shifting by 0 changes nothing."],
    ))

    add(P(
        "divide-by-power-of-two", "Floor Divide By Power Of Two", "easy", T, B,
        "Print the floor of `n / 2^k` for a non-negative `n`, using a bit shift.",
        [p_int("n"), p_int("k")], OUT_INT, lambda n, k: n >> k,
        [(40, 3), (7, 1)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(0, 25)) for _ in range(8)],
        ["0 <= n <= 10^9", "0 <= k <= 30"],
        ["Shifting right by k divides by 2^k and floors the result.",
         "For non-negative values this matches integer division.",
         "Shifting a negative number right is implementation-defined in some languages."],
        explanations=["40 >> 3 = 5.", "7 >> 1 = 3."],
    ))

    add(P(
        "is-even-using-bits", "Even Check With Bits", "easy", T, B,
        "Print `YES` if `n` is even, else `NO`, deciding it from the lowest bit.",
        [p_int("n")], OUT_BOOL, lambda n: n & 1 == 0,
        [(10,), (7,)],
        lambda rng: [(rng.randint(-10 ** 6, 10 ** 6),) for _ in range(8)],
        ["-10^9 <= n <= 10^9"],
        ["The lowest bit is 1 exactly for odd numbers.",
         "So n & 1 == 0 identifies evens.",
         "This also works for negative values in two's complement."],
    ))

    add(P(
        "next-power-of-two", "Next Power Of Two", "easy", T, B,
        "Print the smallest power of two that is greater than or equal to the positive integer `n`.",
        [p_int("n")], OUT_INT, lambda n: 1 << (n - 1).bit_length() if n > 1 else 1,
        [(5,), (8,)],
        lambda rng: [(rng.randint(1, 10 ** 9),) for _ in range(8)],
        ["1 <= n <= 10^9"],
        ["Double a value starting from 1 until it reaches n.",
         "Or take the bit length of n-1 and shift 1 by it.",
         "An exact power of two must return itself."],
        explanations=["8 is the smallest power of two at or above 5.", "8 is already a power of two."],
        brute=lambda n: next(1 << k for k in range(40) if (1 << k) >= n),
    ))

    add(P(
        "count-bits-in-range-array", "Set Bits Of Each Element", "easy", T + ["Arrays"], B,
        "For each element of `nums`, print how many set bits it has, space separated.",
        [p_nums()], OUT_INT_LIST, lambda nums: [bin(v).count("1") for v in nums],
        [([0, 1, 2, 3],), ([255],)],
        lambda rng: [(ints(rng, n, 0, 10 ** 6),) for n in (1, 2, 5, 12, 40, 120)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^9"],
        ["Popcount each element independently.",
         "Brian Kernighan's loop is O(number of set bits) per value.",
         "Many languages expose a builtin popcount."],
    ))

    add(P(
        "gray-code-sequence", "Gray Code Sequence", "medium", T, B,
        "Print the standard `n`-bit reflected Gray code sequence as decimal values, space separated. "
        "Consecutive entries must differ in exactly one bit.",
        [p_int("n", "number of bits")], OUT_INT_LIST,
        lambda n: [i ^ (i >> 1) for i in range(1 << n)],
        [(2,), (1,)],
        lambda rng: [(rng.randint(1, 12),) for _ in range(8)],
        ["1 <= n <= 16"],
        ["The i-th standard Gray code is i XOR (i >> 1).",
         "That produces 2^n values, each differing from the last in one bit.",
         "The reflect-and-prefix construction gives the same sequence."],
        explanations=["0,1,3,2 differ by one bit at each step.", "0 then 1."],
    ))

    add(P(
        "bitwise-and-of-range", "Bitwise AND Of Range", "medium", T, B,
        "Print the bitwise AND of every integer in the inclusive range `[a, b]`.",
        [p_int("a"), p_int("b")], OUT_INT, lambda a, b: _range_and(a, b),
        [(5, 7), (9, 9)],
        lambda rng: [(lambda a: (a, a + rng.randint(0, 5000)))(rng.randint(0, 10 ** 6)) for _ in range(8)],
        ["0 <= a <= b <= 10^9"],
        ["The answer is the common binary prefix of a and b, padded with zeros.",
         "Shift both right until they match, counting the shifts, then shift back.",
         "Any bit that changes anywhere in the range becomes 0."],
        explanations=["101 & 110 & 111 = 100 = 4.", "A single value ANDs to itself."],
        brute=lambda a, b: _range_and_loop(a, b) if b - a <= 200000 else _range_and(a, b),
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _single_among_triples(nums):
    result = 0
    for bit in range(32):
        total = sum((v >> bit) & 1 for v in nums)
        if total % 3:
            result |= 1 << bit
    return result


def _triple_case(rng, k):
    values = []
    used = set()
    for _ in range(k):
        value = rng.randint(1, 400)
        while value in used:
            value = rng.randint(1, 400)
        used.add(value)
        values.extend([value] * 3)
    lone = rng.randint(401, 900)
    values.append(lone)
    rng.shuffle(values)
    return values


def _two_singles(nums):
    combined = 0
    for value in nums:
        combined ^= value
    bit = combined & -combined
    first = second = 0
    for value in nums:
        if value & bit:
            first ^= value
        else:
            second ^= value
    return sorted([first, second])


def _two_single_case(rng, k):
    values = []
    used = set()
    for _ in range(k):
        value = rng.randint(1, 400)
        while value in used:
            value = rng.randint(1, 400)
        used.add(value)
        values.extend([value, value])
    first = rng.randint(401, 700)
    second = rng.randint(701, 900)
    values.extend([first, second])
    rng.shuffle(values)
    return values


def _count_subsets_with_sum(nums, target):
    counts = {0: 1}
    for value in nums:
        updated = dict(counts)
        for total, ways in counts.items():
            new_total = total + value
            if new_total <= target:
                updated[new_total] = updated.get(new_total, 0) + ways
        counts = updated
    return counts.get(target, 0)


def _subset_sums(nums):
    sums = {0}
    for value in nums:
        sums |= {s + value for s in sums}
    return sums


def _xor_upto(n):
    remainder = n % 4
    if remainder == 0:
        return n
    if remainder == 1:
        return 1
    if remainder == 2:
        return n + 1
    return 0


def _xor_upto_loop(n):
    result = 0
    for value in range(1, n + 1):
        result ^= value
    return result


def _xor_list(nums):
    result = 0
    for value in nums:
        result ^= value
    return result


def _sum_bit_differences(nums):
    n = len(nums)
    total = 0
    for bit in range(31):
        ones = sum((v >> bit) & 1 for v in nums)
        total += 2 * ones * (n - ones)
    return total


def _range_and(a, b):
    shifts = 0
    while a != b:
        a >>= 1
        b >>= 1
        shifts += 1
    return a << shifts


def _range_and_loop(a, b):
    result = a
    for value in range(a + 1, b + 1):
        result &= value
    return result
