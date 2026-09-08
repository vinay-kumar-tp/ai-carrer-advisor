"""Mathematics and number theory."""

from __future__ import annotations

import math
import random

from app.content.codequest.framework import (
    INT_LIST,
    OUT_BOOL,
    OUT_INT,
    OUT_INT_LIST,
    OUT_STR,
    P,
    Param,
    ints,
    p_int,
    p_nums,
)

T = ["Math"]
MNT = ["Math & Number Theory"]
MOD = 1_000_000_007


def g_int(lo, hi, count=8):
    def gen(rng: random.Random):
        return [(rng.randint(lo, hi),) for _ in range(count)]

    return gen


def g_two(lo, hi, count=8):
    def gen(rng: random.Random):
        return [(rng.randint(lo, hi), rng.randint(lo, hi)) for _ in range(count)]

    return gen


def specs():
    out: list = []
    add = out.append

    add(P(
        "sum-of-digits", "Sum Of Digits", "easy", T, MNT,
        "Given a non-negative integer `n`, print the sum of its decimal digits.",
        [p_int("n")], OUT_INT, lambda n: sum(int(d) for d in str(n)),
        [(1234,), (0,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Peel off the last digit with n % 10, then divide n by 10.",
         "Repeat until n becomes 0.",
         "n = 0 must print 0, so make sure the loop or the initial value handles it."],
        explanations=["1+2+3+4 = 10.", "Zero has digit sum 0."],
    ))

    add(P(
        "product-of-digits", "Product Of Digits", "easy", T, MNT,
        "Given a non-negative integer `n`, print the product of its decimal digits.",
        [p_int("n")], OUT_INT, lambda n: math.prod(int(d) for d in str(n)),
        [(234,), (105,)], g_int(0, 10 ** 8),
        ["0 <= n <= 10^9"],
        ["Start the product at 1, not 0.",
         "Extract digits with repeated remainder and division.",
         "Any digit 0 makes the whole product 0."],
        explanations=["2*3*4 = 24.", "The digit 0 zeroes the product."],
    ))

    add(P(
        "count-digits", "Count Digits", "easy", T, MNT,
        "Given a non-negative integer `n`, print how many decimal digits it has.",
        [p_int("n")], OUT_INT, lambda n: len(str(n)),
        [(9,), (10000,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Divide by 10 repeatedly and count the steps.",
         "Zero has exactly one digit, which the naive loop would report as 0.",
         "floor(log10(n)) + 1 also works for n > 0."],
    ))

    add(P(
        "reverse-number", "Reverse Number", "easy", T, MNT,
        "Given a non-negative integer `n`, print the number formed by reversing its digits. Leading "
        "zeros in the result are dropped.",
        [p_int("n")], OUT_INT, lambda n: int(str(n)[::-1]),
        [(1234,), (1200,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Build the answer as result = result * 10 + (n % 10).",
         "Divide n by 10 each step.",
         "Trailing zeros of the input naturally disappear from the result."],
        explanations=["1234 reversed is 4321.", "1200 reversed is 21."],
    ))

    add(P(
        "digital-root", "Digital Root", "easy", T, MNT,
        "Repeatedly replace `n` by the sum of its digits until a single digit remains. Print that digit.",
        [p_int("n")], OUT_INT, lambda n: 0 if n == 0 else 1 + (n - 1) % 9,
        [(38,), (0,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Looping the digit sum until n < 10 is the direct approach.",
         "There is a closed form: for n > 0 the answer is 1 + (n-1) % 9.",
         "That works because a number is congruent to its digit sum modulo 9."],
        explanations=["3+8=11, then 1+1=2.", "Zero is already a single digit."],
        brute=lambda n: _digital_root_loop(n),
    ))

    add(P(
        "is-palindrome-number", "Palindrome Number", "easy", T, MNT,
        "Given a non-negative integer `n`, print `YES` if it reads the same forwards and backwards, "
        "else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: str(n) == str(n)[::-1],
        [(121,), (123,)],
        lambda rng: [(rng.choice([rng.randint(0, 10 ** 6), _palindrome_number(rng)]),) for _ in range(9)],
        ["0 <= n <= 10^9"],
        ["Reverse the number arithmetically and compare with the original.",
         "Converting to a string and comparing with its reverse also works.",
         "Single-digit numbers are always palindromes."],
    ))

    add(P(
        "is-armstrong-number", "Armstrong Number", "easy", T, MNT,
        "An Armstrong number equals the sum of its digits each raised to the power of the digit count. "
        "Print `YES` if `n` is an Armstrong number, else `NO`.",
        [p_int("n")], OUT_BOOL,
        lambda n: n == sum(int(d) ** len(str(n)) for d in str(n)),
        [(153,), (154,)],
        lambda rng: [(rng.choice([rng.randint(0, 10000), rng.choice([0, 1, 153, 370, 371, 407, 1634, 8208])]),)
                     for _ in range(9)],
        ["0 <= n <= 10^9"],
        ["Count the digits first — the exponent depends on it.",
         "Then sum each digit raised to that power.",
         "153 = 1^3 + 5^3 + 3^3 is the classic example."],
        explanations=["1+125+27 = 153.", "1+125+64 = 190, not 154."],
    ))

    add(P(
        "is-perfect-number", "Perfect Number", "easy", T, MNT,
        "A perfect number equals the sum of its proper divisors (divisors excluding itself). Print "
        "`YES` if `n` is perfect, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: n > 1 and _divisor_sum_impl(n) - n == n,
        [(28,), (12,)],
        lambda rng: [(rng.choice([rng.randint(1, 20000), rng.choice([6, 28, 496, 8128])]),) for _ in range(9)],
        ["1 <= n <= 10^9"],
        ["Only check divisors up to sqrt(n) and add both d and n/d.",
         "Exclude n itself from the sum.",
         "1 is not perfect because its only proper divisor sum is 0."],
        explanations=["1+2+4+7+14 = 28.", "1+2+3+4+6 = 16, not 12."],
        brute=lambda n: n > 1 and sum(d for d in range(1, n) if n % d == 0) == n,
    ))

    add(P(
        "count-divisors", "Count Divisors", "easy", T, MNT,
        "Given a positive integer `n`, print how many positive divisors it has.",
        [p_int("n")], OUT_INT, lambda n: _count_divisors(n),
        [(12,), (7,)], g_int(1, 10 ** 9),
        ["1 <= n <= 10^9"],
        ["Divisors pair up around sqrt(n).",
         "For each d dividing n with d*d < n, count both d and n/d.",
         "When d*d == n, count that divisor only once."],
        explanations=["1,2,3,4,6,12 gives 6.", "A prime has exactly 2 divisors."],
        brute=lambda n: sum(1 for d in range(1, n + 1) if n % d == 0) if n <= 100000 else _count_divisors(n),
    ))

    add(P(
        "sum-of-divisors", "Sum Of Divisors", "easy", T, MNT,
        "Given a positive integer `n`, print the sum of all its positive divisors.",
        [p_int("n")], OUT_INT, _divisor_sum_impl,
        [(12,), (7,)], g_int(1, 10 ** 5),
        ["1 <= n <= 10^9"],
        ["Iterate d from 1 while d*d <= n.",
         "Add d and n/d whenever d divides n, avoiding a double count when d*d == n.",
         "This is O(sqrt(n))."],
        explanations=["1+2+3+4+6+12 = 28.", "1+7 = 8."],
        brute=lambda n: sum(d for d in range(1, n + 1) if n % d == 0),
    ))

    add(P(
        "largest-divisor-excluding-self", "Largest Proper Divisor", "easy", T, MNT,
        "Given an integer `n >= 2`, print its largest divisor other than `n` itself.",
        [p_int("n")], OUT_INT, lambda n: n // _smallest_prime_factor(n),
        [(12,), (13,)], g_int(2, 10 ** 8),
        ["2 <= n <= 10^9"],
        ["The largest proper divisor is n divided by its smallest prime factor.",
         "Find that factor by trial division up to sqrt(n).",
         "For a prime, the smallest factor is n itself, so the answer is 1."],
        explanations=["12/2 = 6.", "13 is prime, so the answer is 1."],
        brute=lambda n: max(d for d in range(1, n) if n % d == 0) if n <= 100000 else n // _smallest_prime_factor(n),
    ))

    add(P(
        "is-prime", "Prime Check", "easy", T, MNT,
        "Given an integer `n`, print `YES` if it is prime, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: _is_prime(n),
        [(17,), (1,)], g_int(1, 10 ** 9),
        ["1 <= n <= 10^9"],
        ["Numbers below 2 are not prime.",
         "Test divisors only up to sqrt(n).",
         "After checking 2, you can step through odd numbers only."],
        explanations=["17 has no divisor besides 1 and itself.", "1 is not prime by definition."],
        brute=lambda n: (n >= 2 and all(n % d for d in range(2, n))) if n <= 20000 else _is_prime(n),
    ))

    add(P(
        "count-primes-upto", "Count Primes Up To N", "medium", T, MNT,
        "Given an integer `n`, print how many primes are less than or equal to `n`.",
        [p_int("n")], OUT_INT, lambda n: _prime_count(n),
        [(10,), (1,)],
        lambda rng: [(rng.randint(1, 200000),) for _ in range(7)] + [(1,), (2,)],
        ["1 <= n <= 10^6"],
        ["The Sieve of Eratosthenes marks composites in O(n log log n).",
         "Start crossing off multiples of p from p*p.",
         "Only iterate p while p*p <= n.",
         "Testing each number individually would be far too slow at the upper limit."],
        explanations=["2,3,5,7 gives 4.", "There are no primes at or below 1."],
    ))

    add(P(
        "nth-prime", "Nth Prime", "medium", T, MNT,
        "Print the `n`-th prime number (the 1st prime is 2).",
        [p_int("n", "1-based index")], OUT_INT, lambda n: _nth_prime(n),
        [(5,), (1,)],
        lambda rng: [(rng.randint(1, 5000),) for _ in range(8)],
        ["1 <= n <= 10^4"],
        ["Sieve up to a generous bound and collect the primes.",
         "The n-th prime is roughly n * ln(n) for large n, useful for choosing the bound.",
         "Or test candidates one by one, which is fine at these limits."],
        explanations=["2,3,5,7,11 makes 11 the 5th prime.", "The first prime is 2."],
    ))

    add(P(
        "prime-factors-distinct", "Distinct Prime Factors", "easy", T, MNT,
        "Given an integer `n >= 2`, print its distinct prime factors in ascending order.",
        [p_int("n")], OUT_INT_LIST, lambda n: sorted(_prime_factor_set(n)),
        [(60,), (97,)], g_int(2, 10 ** 8),
        ["2 <= n <= 10^9"],
        ["Trial divide by 2, then by odd numbers up to sqrt(n).",
         "Each time a divisor works, divide it out completely before moving on.",
         "Whatever remains above 1 at the end is itself a prime factor."],
        explanations=["60 = 2^2 * 3 * 5.", "97 is prime."],
    ))

    add(P(
        "prime-factorization-count", "Total Prime Factors", "easy", T, MNT,
        "Given an integer `n >= 2`, print the number of prime factors of `n` counted with multiplicity.",
        [p_int("n")], OUT_INT, lambda n: _prime_factor_count(n),
        [(60,), (8,)], g_int(2, 10 ** 8),
        ["2 <= n <= 10^9"],
        ["Divide out each prime factor as many times as it divides n.",
         "Count every division, not every distinct prime.",
         "60 = 2*2*3*5 contributes 4."],
        explanations=["2,2,3,5 gives 4.", "8 = 2*2*2 gives 3."],
    ))

    add(P(
        "largest-prime-factor", "Largest Prime Factor", "easy", T, MNT,
        "Given an integer `n >= 2`, print its largest prime factor.",
        [p_int("n")], OUT_INT, lambda n: max(_prime_factor_set(n)),
        [(60,), (13,)], g_int(2, 10 ** 8),
        ["2 <= n <= 10^9"],
        ["Divide out small factors as you find them.",
         "Track the largest factor removed.",
         "If a value greater than 1 remains after trial division to sqrt(n), it is the largest prime factor."],
    ))

    add(P(
        "smallest-prime-factor", "Smallest Prime Factor", "easy", T, MNT,
        "Given an integer `n >= 2`, print its smallest prime factor.",
        [p_int("n")], OUT_INT, lambda n: _smallest_prime_factor(n),
        [(60,), (13,)], g_int(2, 10 ** 8),
        ["2 <= n <= 10^9"],
        ["Check 2 first, then odd candidates up to sqrt(n).",
         "The first divisor found is automatically prime.",
         "A prime n is its own smallest prime factor."],
    ))

    add(P(
        "gcd-two-numbers", "GCD Of Two Numbers", "easy", T, MNT,
        "Print the greatest common divisor of the positive integers `a` and `b`.",
        [p_int("a"), p_int("b")], OUT_INT, lambda a, b: math.gcd(a, b),
        [(12, 18), (7, 13)], g_two(1, 10 ** 9),
        ["1 <= a, b <= 10^9"],
        ["Euclid's algorithm: gcd(a, b) = gcd(b, a % b).",
         "Recurse or loop until the second value becomes 0.",
         "It runs in O(log min(a,b))."],
        explanations=["Common divisors of 12 and 18 peak at 6.", "They are coprime."],
    ))

    add(P(
        "lcm-two-numbers", "LCM Of Two Numbers", "easy", T, MNT,
        "Print the least common multiple of the positive integers `a` and `b`.",
        [p_int("a"), p_int("b")], OUT_INT, lambda a, b: a * b // math.gcd(a, b),
        [(4, 6), (5, 5)], g_two(1, 10 ** 6),
        ["1 <= a, b <= 10^6"],
        ["lcm(a,b) = a / gcd(a,b) * b.",
         "Divide before multiplying to limit overflow in fixed-width languages.",
         "The result can be much larger than either input."],
        explanations=["12 is the smallest common multiple.", "Equal values give themselves."],
    ))

    add(P(
        "gcd-of-array", "GCD Of Array", "easy", T + ["Arrays"], MNT,
        "Print the greatest common divisor of all elements of the positive array `nums`.",
        [Param("nums", INT_LIST, "positive integers")], OUT_INT, lambda nums: math.gcd(*nums) if len(nums) > 1 else nums[0],
        [([12, 18, 24],), ([7],)],
        lambda rng: [(ints(rng, n, 1, 1000),) for n in (1, 2, 3, 6, 12, 40, 120)],
        ["1 <= n <= 2000", "1 <= nums[i] <= 10^9"],
        ["gcd is associative, so fold it across the array.",
         "Start from nums[0] and combine with each later element.",
         "You can stop early once the running gcd reaches 1."],
    ))

    add(P(
        "lcm-of-array", "LCM Of Array", "medium", T + ["Arrays"], MNT,
        "Print the least common multiple of all elements of the positive array `nums`.",
        [Param("nums", INT_LIST, "positive integers")], OUT_INT, lambda nums: _lcm_all(nums),
        [([4, 6, 8],), ([3],)],
        lambda rng: [(ints(rng, n, 1, 30),) for n in (1, 2, 3, 5, 8, 12)],
        ["1 <= n <= 100", "1 <= nums[i] <= 100", "the answer fits in a 64-bit signed integer"],
        ["Fold lcm across the array like gcd.",
         "Use lcm(a,b) = a / gcd(a,b) * b at each step.",
         "The value grows quickly, so watch for overflow in fixed-width languages."],
        explanations=["lcm(4,6)=12, lcm(12,8)=24.", "A single value is its own lcm."],
    ))

    add(P(
        "are-coprime", "Coprime Check", "easy", T, MNT,
        "Print `YES` if `a` and `b` share no common factor greater than 1, else `NO`.",
        [p_int("a"), p_int("b")], OUT_BOOL, lambda a, b: math.gcd(a, b) == 1,
        [(9, 28), (12, 18)], g_two(1, 10 ** 6),
        ["1 <= a, b <= 10^9"],
        ["Two numbers are coprime exactly when their gcd is 1.",
         "Compute the gcd with Euclid's algorithm.",
         "1 is coprime with everything."],
    ))

    add(P(
        "factorial-modulo", "Factorial Modulo", "easy", T, MNT,
        f"Print the factorial of `n` — the product `1 * 2 * ... * n` — modulo `{MOD}`.",
        [p_int("n")], OUT_INT, lambda n: _factorial_mod(n),
        [(5,), (0,)],
        lambda rng: [(rng.randint(0, 200000),) for _ in range(7)] + [(0,), (1,)],
        ["0 <= n <= 10^6"],
        ["Multiply iteratively, taking the remainder after each step.",
         "0! is 1.",
         "Never compute the full factorial first — it has millions of digits."],
        explanations=["5! = 120.", "0! = 1 by definition."],
    ))

    add(P(
        "power-modulo", "Modular Exponentiation", "medium", T, MNT,
        "Given `base`, `exponent` and `modulus`, print `base^exponent mod modulus`.",
        [p_int("base"), p_int("exponent"), p_int("modulus")], OUT_INT,
        lambda base, exponent, modulus: pow(base, exponent, modulus),
        [(2, 10, 1000), (3, 0, 7)],
        lambda rng: [(rng.randint(0, 10 ** 6), rng.randint(0, 10 ** 9), rng.randint(1, 10 ** 9))
                     for _ in range(8)],
        ["0 <= base <= 10^9", "0 <= exponent <= 10^9", "1 <= modulus <= 10^9"],
        ["Square-and-multiply halves the exponent each step, giving O(log exponent).",
         "Reduce modulo the modulus after every multiplication.",
         "Anything to the power 0 is 1 mod m (and 0 when m = 1)."],
        explanations=["2^10 = 1024, and 1024 mod 1000 = 24.", "Any base to the 0 is 1."],
    ))

    add(P(
        "nth-fibonacci", "Nth Fibonacci", "easy", T + ["Dynamic Programming"], ["Fibonacci / Linear DP"],
        f"With `F(0) = 0` and `F(1) = 1`, print `F(n)` modulo `{MOD}`.",
        [p_int("n")], OUT_INT, lambda n: _fib_mod(n),
        [(10,), (0,)],
        lambda rng: [(rng.randint(0, 500000),) for _ in range(7)] + [(1,), (2,)],
        ["0 <= n <= 10^6"],
        ["Iterating with two running values is O(n) and O(1) space.",
         "Naive recursion without memoisation is exponential — avoid it.",
         "Take the remainder at every addition to keep numbers small."],
        explanations=["F(10) = 55.", "F(0) = 0."],
    ))

    add(P(
        "fibonacci-sequence-list", "Fibonacci Sequence", "easy", T + ["Dynamic Programming"],
        ["Fibonacci / Linear DP"],
        "Print the first `n` Fibonacci numbers starting from `F(0) = 0`, space separated.",
        [p_int("n", "how many terms")], OUT_INT_LIST, lambda n: _fib_list(n),
        [(7,), (1,)],
        lambda rng: [(rng.randint(1, 60),) for _ in range(8)],
        ["1 <= n <= 80", "the values fit in a 64-bit signed integer"],
        ["Keep the two previous terms and append their sum.",
         "The first two terms are 0 and 1.",
         "For n = 1 print only 0."],
    ))

    add(P(
        "catalan-number", "Catalan Number", "medium", T + ["Dynamic Programming"], MNT,
        f"Print the `n`-th Catalan number modulo `{MOD}`, where `C(0) = 1` and "
        "`C(n+1) = sum of C(i)*C(n-i)`.",
        [p_int("n")], OUT_INT, lambda n: _catalan(n),
        [(4,), (0,)],
        lambda rng: [(rng.randint(0, 600),) for _ in range(8)],
        ["0 <= n <= 1000"],
        ["Build the sequence bottom-up with the convolution recurrence.",
         "That costs O(n^2), which is fine here.",
         "Reduce modulo the given prime at each step."],
        explanations=["C(4) = 14.", "C(0) = 1."],
    ))

    add(P(
        "binomial-coefficient-mod", "Binomial Coefficient", "medium", T, MNT,
        f"Print `C(n, r)` — the number of ways to choose `r` items from `n` — modulo `{MOD}`.",
        [p_int("n"), p_int("r")], OUT_INT, lambda n, r: _binomial(n, r),
        [(5, 2), (6, 0)],
        lambda rng: [(lambda n: (n, rng.randint(0, n)))(rng.randint(0, 2000)) for _ in range(8)],
        ["0 <= r <= n <= 3000"],
        ["Pascal's triangle gives an O(n*r) DP with only additions.",
         "Alternatively use factorials with a modular inverse via Fermat's little theorem.",
         "C(n, 0) and C(n, n) are both 1."],
        explanations=["C(5,2) = 10.", "There is one way to choose nothing."],
    ))

    add(P(
        "is-power-of-two", "Power Of Two", "easy", T + ["Bit Manipulation"], ["Bit Manipulation"],
        "Print `YES` if the integer `n` is a positive power of two, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: n > 0 and n & (n - 1) == 0,
        [(16,), (18,)],
        lambda rng: [(rng.choice([rng.randint(-5, 5000), 1 << rng.randint(0, 20)]),) for _ in range(9)],
        ["-10^9 <= n <= 10^9"],
        ["A positive power of two has exactly one bit set.",
         "n & (n-1) clears the lowest set bit, so it becomes 0 only for a single-bit value.",
         "Guard against n <= 0 before using the bit trick."],
    ))

    add(P(
        "is-power-of-three", "Power Of Three", "easy", T, MNT,
        "Print `YES` if the integer `n` is a positive power of three, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: _is_power_of(n, 3),
        [(27,), (10,)],
        lambda rng: [(rng.choice([rng.randint(-5, 100000), 3 ** rng.randint(0, 12)]),) for _ in range(9)],
        ["-10^9 <= n <= 10^9"],
        ["Divide by 3 while the remainder is 0.",
         "The answer is YES exactly when you reach 1.",
         "Reject values that are zero or negative up front."],
    ))

    add(P(
        "square-root-integer", "Integer Square Root", "easy", T + ["Binary Search"], ["Binary Search"],
        "Given a non-negative integer `n`, print the largest integer `r` with `r*r <= n`.",
        [p_int("n")], OUT_INT, lambda n: math.isqrt(n),
        [(8,), (16,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Binary search r over the range 0..n.",
         "Compare r*r with n, being careful about overflow in fixed-width languages.",
         "Floating-point sqrt can be off by one at large values, so verify the result."],
        explanations=["2*2=4 <= 8 but 3*3=9 > 8.", "16 is a perfect square."],
    ))

    add(P(
        "is-perfect-square", "Perfect Square", "easy", T + ["Binary Search"], ["Binary Search"],
        "Print `YES` if the non-negative integer `n` is a perfect square, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: math.isqrt(n) ** 2 == n,
        [(16,), (14,)],
        lambda rng: [(rng.choice([rng.randint(0, 10 ** 6), rng.randint(0, 1000) ** 2]),) for _ in range(9)],
        ["0 <= n <= 10^9"],
        ["Take the integer square root and square it again.",
         "Binary search avoids any floating-point rounding worries.",
         "0 and 1 are perfect squares."],
    ))

    add(P(
        "is-perfect-cube", "Perfect Cube", "easy", T, MNT,
        "Print `YES` if the non-negative integer `n` is a perfect cube, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: _is_perfect_cube(n),
        [(27,), (26,)],
        lambda rng: [(rng.choice([rng.randint(0, 10 ** 6), rng.randint(0, 100) ** 3]),) for _ in range(9)],
        ["0 <= n <= 10^9"],
        ["Binary search r in 0..1000 for the smallest r with r^3 >= n.",
         "Then check whether r^3 equals n exactly.",
         "Cube roots via floating point can be inaccurate, so verify with integers."],
    ))

    add(P(
        "sum-first-n-naturals", "Sum Of First N Naturals", "easy", T, MNT,
        "Print the sum of the first `n` natural numbers, that is `1 + 2 + ... + n`.",
        [p_int("n")], OUT_INT, lambda n: n * (n + 1) // 2,
        [(10,), (1,)], g_int(1, 10 ** 6),
        ["1 <= n <= 10^6"],
        ["The closed form is n(n+1)/2.",
         "Use integer arithmetic — one of n or n+1 is always even.",
         "A loop works too but the formula is O(1)."],
    ))

    add(P(
        "sum-of-squares-first-n", "Sum Of Squares", "easy", T, MNT,
        "Print the sum of the squares of the first `n` natural numbers: `1^2 + 2^2 + ... + n^2`.",
        [p_int("n")], OUT_INT, lambda n: n * (n + 1) * (2 * n + 1) // 6,
        [(3,), (1,)], g_int(1, 10 ** 5),
        ["1 <= n <= 10^5"],
        ["The closed form is n(n+1)(2n+1)/6.",
         "Multiply before dividing so the division stays exact.",
         "A simple loop also passes at this limit."],
        explanations=["1+4+9 = 14.", "Just 1."],
    ))

    add(P(
        "sum-of-cubes-first-n", "Sum Of Cubes", "easy", T, MNT,
        "Print the sum of the cubes of the first `n` natural numbers: `1^3 + 2^3 + ... + n^3`.",
        [p_int("n")], OUT_INT, lambda n: (n * (n + 1) // 2) ** 2,
        [(3,), (1,)], g_int(1, 10 ** 4),
        ["1 <= n <= 10^4"],
        ["The sum of cubes equals the square of the sum of naturals.",
         "So compute n(n+1)/2 and square it.",
         "Watch the magnitude — it grows like n^4."],
        explanations=["1+8+27 = 36 = 6^2.", "Just 1."],
    ))

    add(P(
        "count-trailing-zeros-factorial", "Trailing Zeros In Factorial", "medium", T, MNT,
        "Print the number of trailing zeros in `n!`.",
        [p_int("n")], OUT_INT, lambda n: _trailing_zeros_factorial(n),
        [(25,), (3,)],
        lambda rng: [(rng.randint(0, 10 ** 9),) for _ in range(8)],
        ["0 <= n <= 10^9"],
        ["Each trailing zero comes from a factor of 10 = 2 * 5.",
         "Factors of 5 are always scarcer than factors of 2, so count only the 5s.",
         "The count is n/5 + n/25 + n/125 + ... using integer division.",
         "Never compute n! itself."],
        explanations=["25! ends in six zeros.", "3! = 6 has none."],
    ))

    add(P(
        "euler-totient", "Euler Totient", "medium", T, MNT,
        "Print the count of integers in `1..n` that are coprime with `n`.",
        [p_int("n")], OUT_INT, lambda n: _totient(n),
        [(9,), (1,)], g_int(1, 10 ** 7),
        ["1 <= n <= 10^9"],
        ["Start from n and, for each distinct prime factor p, multiply by (1 - 1/p).",
         "Implement that as result -= result / p after dividing p out.",
         "Trial division to sqrt(n) finds all the prime factors you need.",
         "phi(1) is 1."],
        explanations=["1,2,4,5,7,8 are coprime with 9.", "phi(1) = 1."],
        brute=lambda n: sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1) if n <= 20000 else _totient(n),
    ))

    add(P(
        "decimal-to-binary", "Decimal To Binary", "easy", T + ["Bit Manipulation"], ["Bit Manipulation"],
        "Given a non-negative integer `n`, print its binary representation without leading zeros.",
        [p_int("n")], OUT_STR, lambda n: bin(n)[2:],
        [(10,), (0,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Collect n % 2 repeatedly and divide by 2.",
         "The bits come out least significant first, so reverse them.",
         "n = 0 should print 0."],
        explanations=["10 in binary is 1010.", "Zero prints 0."],
    ))

    add(P(
        "binary-to-decimal", "Binary To Decimal", "easy", T + ["Bit Manipulation"], ["Bit Manipulation"],
        "The array `bits` holds the binary digits of a number, most significant first. Print its "
        "decimal value.",
        [Param("bits", INT_LIST, "each value is 0 or 1")], OUT_INT,
        lambda bits: int("".join(map(str, bits)), 2),
        [([1, 0, 1, 0],), ([0],)],
        lambda rng: [([rng.randint(0, 1) for _ in range(n)],) for n in (1, 2, 4, 8, 16, 30, 50)],
        ["1 <= n <= 60", "bits[i] is 0 or 1", "the value fits in a 64-bit signed integer"],
        ["Process bits left to right: value = value * 2 + bit.",
         "That is the same shape as decimal parsing with base 2.",
         "Shifting left by one is equivalent to multiplying by two."],
    ))

    add(P(
        "convert-to-base", "Convert To Base", "medium", T, MNT,
        "Print the representation of the non-negative integer `n` in base `b`, using digits `0-9` then "
        "lowercase letters for values 10 and above.",
        [p_int("n"), p_int("b", "the target base")], OUT_STR, _to_base,
        [(255, 16), (0, 7)],
        lambda rng: [(rng.randint(0, 10 ** 9), rng.randint(2, 36)) for _ in range(8)],
        ["0 <= n <= 10^9", "2 <= b <= 36"],
        ["Repeatedly take n % b as the next digit and divide n by b.",
         "Map values 0-9 to digits and 10-35 to a-z.",
         "Reverse the collected digits, and print 0 when n is 0."],
        explanations=["255 in hex is ff.", "Zero is 0 in any base."],
    ))

    add(P(
        "count-set-bits-number", "Count Set Bits", "easy", T + ["Bit Manipulation"], ["Bit Manipulation"],
        "Print how many `1` bits the non-negative integer `n` has in binary.",
        [p_int("n")], OUT_INT, lambda n: bin(n).count("1"),
        [(13,), (0,)], g_int(0, 10 ** 9),
        ["0 <= n <= 10^9"],
        ["Check the lowest bit with n & 1, then shift right.",
         "Brian Kernighan's trick, n &= n - 1, removes one set bit per iteration.",
         "That makes the loop run only as many times as there are set bits."],
        explanations=["13 is 1101, which has three ones.", "Zero has none."],
    ))

    add(P(
        "sum-of-array-modulo", "Array Sum Modulo", "easy", T + ["Arrays"], MNT,
        f"Print the sum of `nums` modulo `{MOD}`.",
        [p_nums()], OUT_INT, lambda nums: sum(nums) % MOD,
        [([1, 2, 3],), ([1000000006, 5],)],
        lambda rng: [(ints(rng, n, 0, 10 ** 9),) for n in (1, 2, 5, 12, 40, 120, 300)],
        ["1 <= n <= 2000", "0 <= nums[i] <= 10^9"],
        ["Add elements one at a time, taking the remainder as you go.",
         "That keeps every intermediate value small.",
         "Summing first can overflow fixed-width integer types."],
        explanations=["6 mod 1000000007 = 6.", "1000000011 mod 1000000007 = 4."],
    ))

    add(P(
        "happy-number", "Happy Number", "easy", T + ["Hashing"], ["Fast & Slow Pointers"],
        "Repeatedly replace `n` with the sum of the squares of its digits. Print `YES` if this reaches "
        "`1`, else `NO` (it will otherwise cycle forever).",
        [p_int("n")], OUT_BOOL, lambda n: _is_happy(n),
        [(19,), (2,)], g_int(1, 10 ** 6),
        ["1 <= n <= 10^9"],
        ["The process either reaches 1 or enters a cycle.",
         "Track values you have already seen in a set to detect the cycle.",
         "Floyd's fast-and-slow pointer trick detects it in O(1) space."],
        explanations=["19 -> 82 -> 68 -> 100 -> 1.", "2 falls into a cycle that never hits 1."],
    ))

    add(P(
        "ugly-number-check", "Ugly Number", "easy", T, MNT,
        "An ugly number is a positive integer whose only prime factors are 2, 3 and 5. Print `YES` if "
        "`n` is ugly, else `NO`.",
        [p_int("n")], OUT_BOOL, lambda n: _is_ugly(n),
        [(6,), (14,)], g_int(1, 10 ** 6),
        ["1 <= n <= 10^9"],
        ["Divide out every factor of 2, then 3, then 5.",
         "The number is ugly exactly when 1 remains.",
         "1 counts as ugly since it has no prime factors."],
        explanations=["6 = 2*3.", "14 has the prime factor 7."],
    ))

    add(P(
        "count-numbers-divisible", "Count Divisible In Range", "easy", T, MNT,
        "Print how many integers in the inclusive range `[a, b]` are divisible by `d`.",
        [p_int("a"), p_int("b"), p_int("d")], OUT_INT,
        lambda a, b, d: b // d - (a - 1) // d,
        [(1, 10, 3), (5, 5, 5)],
        lambda rng: [(lambda a: (a, rng.randint(a, a + rng.randint(0, 10 ** 6)), rng.randint(1, 1000)))(rng.randint(1, 10 ** 6))
                     for _ in range(8)],
        ["1 <= a <= b <= 10^9", "1 <= d <= 10^9"],
        ["Count multiples up to b, then subtract those below a.",
         "That is b/d - (a-1)/d with integer division.",
         "Looping over the range would be far too slow at the upper limit."],
        explanations=["3, 6 and 9 are divisible by 3.", "5 divides itself."],
    ))

    add(P(
        "sum-of-multiples", "Sum Of Multiples", "easy", T, MNT,
        "Print the sum of all multiples of `d` in the inclusive range `[1, n]`.",
        [p_int("n"), p_int("d")], OUT_INT,
        lambda n, d: d * (n // d) * (n // d + 1) // 2,
        [(10, 3), (5, 7)],
        lambda rng: [(rng.randint(1, 10 ** 6), rng.randint(1, 1000)) for _ in range(8)],
        ["1 <= n <= 10^9", "1 <= d <= 10^9"],
        ["There are k = n/d multiples: d, 2d, ..., kd.",
         "Their sum is d * (1 + 2 + ... + k) = d * k(k+1)/2.",
         "Print 0 when d exceeds n."],
        explanations=["3+6+9 = 18.", "There is no multiple of 7 up to 5."],
    ))

    add(P(
        "abs-difference-sum-product", "Digit Sum Times Product", "easy", T, MNT,
        "For a non-negative integer `n`, print the absolute difference between the product of its "
        "digits and the sum of its digits.",
        [p_int("n")], OUT_INT,
        lambda n: abs(math.prod(int(d) for d in str(n)) - sum(int(d) for d in str(n))),
        [(234,), (5,)], g_int(0, 10 ** 8),
        ["0 <= n <= 10^9"],
        ["Compute both aggregates in the same digit loop.",
         "Start the product at 1 and the sum at 0.",
         "Take the absolute value at the end."],
        explanations=["Product 24 minus sum 9 gives 15.", "5 - 5 = 0."],
    ))

    add(P(
        "min-steps-to-one", "Minimum Steps To One", "medium", T + ["Dynamic Programming"],
        ["Fibonacci / Linear DP"],
        "From `n` you may subtract 1, divide by 2 (if divisible) or divide by 3 (if divisible). Print "
        "the fewest steps to reach 1.",
        [p_int("n")], OUT_INT, lambda n: _min_steps_to_one(n),
        [(10,), (1,)],
        lambda rng: [(rng.randint(1, 100000),) for _ in range(8)],
        ["1 <= n <= 10^6"],
        ["Build a DP table from 1 up to n.",
         "dp[i] = 1 + min(dp[i-1], dp[i/2] if divisible, dp[i/3] if divisible).",
         "Greedily dividing whenever possible is not always optimal, so use the DP.",
         "dp[1] is 0."],
        explanations=["10 -> 9 -> 3 -> 1 takes 3 steps.", "Already at 1."],
    ))

    return out


# ─── Reference helpers ───────────────────────────────────────────

def _digital_root_loop(n):
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


def _palindrome_number(rng):
    half = str(rng.randint(1, 9999))
    return int(half + half[::-1][rng.randint(0, 1):])


def _divisor_sum_impl(n):
    total = 0
    d = 1
    while d * d <= n:
        if n % d == 0:
            total += d
            other = n // d
            if other != d:
                total += other
        d += 1
    return total


def _count_divisors(n):
    count = 0
    d = 1
    while d * d <= n:
        if n % d == 0:
            count += 2 if d != n // d else 1
        d += 1
    return count


def _smallest_prime_factor(n):
    if n % 2 == 0:
        return 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return d
        d += 2
    return n


def _is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _prime_count(n):
    if n < 2:
        return 0
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    p = 2
    while p * p <= n:
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
        p += 1
    return sum(sieve)


def _nth_prime(n):
    limit = max(20, int(n * (math.log(n) + math.log(math.log(n))) * 1.3) + 10) if n >= 6 else 20
    while True:
        sieve = bytearray([1]) * (limit + 1)
        sieve[0] = sieve[1] = 0
        p = 2
        while p * p <= limit:
            if sieve[p]:
                sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
            p += 1
        primes = [i for i, flag in enumerate(sieve) if flag]
        if len(primes) >= n:
            return primes[n - 1]
        limit *= 2


def _prime_factor_set(n):
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n //= 2
    d = 3
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 2
    if n > 1:
        factors.add(n)
    return factors


def _prime_factor_count(n):
    count = 0
    while n % 2 == 0:
        count += 1
        n //= 2
    d = 3
    while d * d <= n:
        while n % d == 0:
            count += 1
            n //= d
        d += 2
    if n > 1:
        count += 1
    return count


def _lcm_all(nums):
    result = 1
    for value in nums:
        result = result * value // math.gcd(result, value)
    return result


def _factorial_mod(n):
    result = 1
    for value in range(2, n + 1):
        result = result * value % MOD
    return result


def _fib_mod(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % MOD
    return a


def _fib_list(n):
    values = [0, 1]
    while len(values) < n:
        values.append(values[-1] + values[-2])
    return values[:n]


def _catalan(n):
    table = [0] * (n + 1)
    table[0] = 1
    for i in range(1, n + 1):
        total = 0
        for j in range(i):
            total += table[j] * table[i - 1 - j]
        table[i] = total % MOD
    return table[n]


def _binomial(n, r):
    if r < 0 or r > n:
        return 0
    r = min(r, n - r)
    numerator = 1
    denominator = 1
    for i in range(r):
        numerator = numerator * (n - i) % MOD
        denominator = denominator * (i + 1) % MOD
    return numerator * pow(denominator, MOD - 2, MOD) % MOD


def _is_power_of(n, base):
    if n < 1:
        return False
    while n % base == 0:
        n //= base
    return n == 1


def _is_perfect_cube(n):
    root = round(n ** (1 / 3)) if n > 0 else 0
    for candidate in (root - 1, root, root + 1):
        if candidate >= 0 and candidate ** 3 == n:
            return True
    return False


def _trailing_zeros_factorial(n):
    count = 0
    power = 5
    while power <= n:
        count += n // power
        power *= 5
    return count


def _totient(n):
    result = n
    value = n
    if value % 2 == 0:
        result -= result // 2
        while value % 2 == 0:
            value //= 2
    d = 3
    while d * d <= value:
        if value % d == 0:
            result -= result // d
            while value % d == 0:
                value //= d
        d += 2
    if value > 1:
        result -= result // value
    return result


DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def _to_base(n, b):
    if n == 0:
        return "0"
    out = []
    while n:
        out.append(DIGITS[n % b])
        n //= b
    return "".join(reversed(out))


def _is_happy(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1


def _is_ugly(n):
    if n < 1:
        return False
    for factor in (2, 3, 5):
        while n % factor == 0:
            n //= factor
    return n == 1


def _min_steps_to_one(n):
    dp = [0] * (n + 1)
    for value in range(2, n + 1):
        best = dp[value - 1] + 1
        if value % 2 == 0:
            best = min(best, dp[value // 2] + 1)
        if value % 3 == 0:
            best = min(best, dp[value // 3] + 1)
        dp[value] = best
    return dp[n]
