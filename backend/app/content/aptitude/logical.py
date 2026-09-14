"""Logical Reasoning topics."""

from __future__ import annotations

from app.content.aptitude.framework import Q, S, T, Topic


def topics() -> list[Topic]:
    return [
        # ── Number Series ───────────────────────────────────────
        T("logical", "Number Series", icon="🔗", blurb="Find the pattern and the missing term.", subtopics=[
            S("Arithmetic Patterns", [
                Q("2, 6, 12, 20, 30, ?", ["36", "40", "42", "48"], 2,
                  "Differences 4,6,8,10,12 -> 30+12 = 42.", "easy"),
                Q("3, 6, 11, 18, 27, ?", ["36", "38", "40", "42"], 1,
                  "Differences 3,5,7,9,11 -> 27+11 = 38.", "medium"),
                Q("1, 4, 9, 16, 25, ?", ["30", "36", "49", "35"], 1,
                  "Perfect squares -> 6^2 = 36.", "easy"),
            ]),
            S("Multiplicative Patterns", [
                Q("2, 6, 18, 54, ?", ["108", "162", "144", "216"], 1,
                  "Multiply by 3 -> 54 x 3 = 162.", "easy"),
                Q("5, 10, 20, 40, ?", ["60", "80", "70", "100"], 1,
                  "Double each time -> 80.", "easy"),
                Q("1, 2, 6, 24, 120, ?", ["600", "720", "480", "840"], 1,
                  "Factorials / multiply by n -> 120 x 6 = 720.", "hard"),
            ]),
        ]),

        # ── Coding Decoding ─────────────────────────────────────
        T("logical", "Coding Decoding", icon="🔐", blurb="Letter and number coding logic.", subtopics=[
            S("Letter Coding", [
                Q("If CAT is coded as DBU, then DOG is:", ["EPH", "EPG", "FPH", "EOG"], 0,
                  "Each letter +1 -> D->E, O->P, G->H = EPH.", "easy"),
                Q("If A=1, B=2, ..., then the code for 'BAD' summed is:",
                  ["7", "8", "9", "6"], 0,
                  "2+1+4 = 7.", "easy"),
                Q("If RED is 27 (18+5+4), then BLUE is:",
                  ["40", "37", "42", "45"], 0,
                  "2+12+21+5 = 40.", "medium"),
            ]),
            S("Substitution", [
                Q("If 'pen' means 'book', 'book' means 'pencil', what do you write with?",
                  ["pen", "book", "pencil", "paper"], 1,
                  "You write with a pen, which is called 'book' here.", "medium"),
            ]),
        ]),

        # ── Blood Relations ─────────────────────────────────────
        T("logical", "Blood Relations", icon="👪", blurb="Family relationship puzzles.", subtopics=[
            S("Direct Relations", [
                Q("A is B's brother, B is C's mother. A is C's:",
                  ["father", "uncle", "brother", "grandfather"], 1,
                  "A (brother of the mother) is C's uncle.", "medium"),
                Q("Pointing to a man, a woman said 'His mother is the only daughter of my mother.' The woman is the man's:",
                  ["mother", "sister", "aunt", "grandmother"], 0,
                  "Only daughter of her mother is herself -> she is his mother.", "hard"),
                Q("X is the son of Y. Y is the sister of Z. Z is the son of W. W is X's:",
                  ["father", "grandfather", "uncle", "brother"], 1,
                  "W is parent of Y and Z, so W is X's grandfather.", "hard"),
            ]),
        ]),

        # ── Direction Sense ─────────────────────────────────────
        T("logical", "Direction Sense", icon="🧭", blurb="Track movements and net displacement.", subtopics=[
            S("Basic Directions", [
                Q("A man walks 3 km north, then 4 km east. Distance from start:",
                  ["5 km", "7 km", "6 km", "4 km"], 0,
                  "sqrt(3^2 + 4^2) = 5 km.", "easy"),
                Q("Facing east, you turn right, then right again. You now face:",
                  ["North", "South", "West", "East"], 2,
                  "East -> South -> West.", "easy"),
                Q("Walk 10 m south, 10 m west, 10 m north. You are ___ from start:",
                  ["10 m west", "10 m east", "20 m west", "0 m"], 0,
                  "Net displacement is 10 m to the west.", "medium"),
            ]),
        ]),

        # ── Syllogism ───────────────────────────────────────────
        T("logical", "Syllogism", icon="🔎", blurb="Deduce valid conclusions from statements.", subtopics=[
            S("Basics", [
                Q("All cats are animals. All animals are living. So all cats are:",
                  ["living", "dogs", "plants", "none"], 0,
                  "Transitive: cats -> animals -> living.", "easy"),
                Q("Some pens are red. All red things are bright. Which follows?",
                  ["Some pens are bright", "All pens are bright", "No pens are bright", "All bright are pens"], 0,
                  "Some pens (the red ones) are bright.", "medium"),
                Q("No A is B. All B are C. Valid conclusion:",
                  ["Some C are not A", "All C are A", "No C is A", "All A are C"], 0,
                  "The B's are C but not A, so some C are not A.", "hard"),
            ]),
        ]),

        # ── Seating Arrangement ─────────────────────────────────
        T("logical", "Seating Arrangement", icon="🪑", blurb="Linear and circular seating logic.", subtopics=[
            S("Linear", [
                Q("Five people A-E sit in a row. A is at an end, B next to A. B can be at position:",
                  ["1", "2", "3", "any"], 1,
                  "If A is at end position 1, B (adjacent) is at 2.", "medium"),
                Q("In a row of 20, a person is 7th from left. Their position from right:",
                  ["13th", "14th", "12th", "15th"], 1,
                  "20 - 7 + 1 = 14th from right.", "easy"),
            ]),
        ]),
    ]
