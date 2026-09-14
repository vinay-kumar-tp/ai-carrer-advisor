"""Technical MCQ topics (CS fundamentals + core languages)."""

from __future__ import annotations

from app.content.aptitude.framework import Q, S, T, Topic


def topics() -> list[Topic]:
    return [
        # ── Data Structures ─────────────────────────────────────
        T("technical", "Data Structures", icon="🌲", blurb="Arrays, stacks, queues, trees, graphs.", subtopics=[
            S("Complexity", [
                Q("Average time complexity of binary search:",
                  ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1,
                  "Binary search halves the range each step -> O(log n).", "easy"),
                Q("Accessing an element by index in an array is:",
                  ["O(n)", "O(log n)", "O(1)", "O(n^2)"], 2,
                  "Direct indexing is constant time.", "easy"),
                Q("Worst-case time to search an unsorted array:",
                  ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2,
                  "You may have to check every element.", "easy"),
            ]),
            S("Structures", [
                Q("A stack follows which order?",
                  ["FIFO", "LIFO", "Random", "Priority"], 1,
                  "Stack is Last-In-First-Out.", "easy"),
                Q("A queue follows which order?",
                  ["LIFO", "FIFO", "Random", "Sorted"], 1,
                  "Queue is First-In-First-Out.", "easy"),
                Q("Which structure is best for implementing recursion internally?",
                  ["Queue", "Stack", "Heap", "Graph"], 1,
                  "The call stack manages recursive calls.", "medium"),
                Q("A binary heap is typically used to implement a:",
                  ["Hash map", "Priority queue", "Linked list", "Trie"], 1,
                  "Heaps back priority queues efficiently.", "medium"),
            ]),
        ]),

        # ── DBMS ────────────────────────────────────────────────
        T("technical", "DBMS", icon="🗄", blurb="SQL, normalization, transactions.", subtopics=[
            S("SQL", [
                Q("Which SQL keyword removes duplicate rows from results?",
                  ["UNIQUE", "DISTINCT", "REMOVE", "DEDUP"], 1,
                  "SELECT DISTINCT removes duplicate rows.", "easy"),
                Q("Which clause filters groups after aggregation?",
                  ["WHERE", "HAVING", "GROUP", "FILTER"], 1,
                  "HAVING filters after GROUP BY.", "medium"),
                Q("A PRIMARY KEY must be:",
                  ["nullable", "unique and non-null", "a foreign key", "indexed only"], 1,
                  "Primary keys are unique and cannot be null.", "easy"),
            ]),
            S("Design", [
                Q("Normalization primarily reduces:",
                  ["query speed", "data redundancy", "table count", "index size"], 1,
                  "Normalization reduces redundancy and anomalies.", "medium"),
                Q("ACID's 'A' stands for:",
                  ["Availability", "Atomicity", "Accuracy", "Access"], 1,
                  "Atomicity: all-or-nothing transactions.", "medium"),
            ]),
        ]),

        # ── Operating Systems ───────────────────────────────────
        T("technical", "Operating Systems", icon="🖥", blurb="Processes, scheduling, memory.", subtopics=[
            S("Processes", [
                Q("A deadlock requires all EXCEPT:",
                  ["Mutual exclusion", "Hold and wait", "Preemption", "Circular wait"], 2,
                  "No-preemption is required; preemption prevents deadlock.", "hard"),
                Q("Which is NOT a process state?",
                  ["Ready", "Running", "Waiting", "Compiling"], 3,
                  "Compiling is not a process scheduling state.", "easy"),
                Q("Round-robin scheduling uses a:",
                  ["priority", "time quantum", "random pick", "shortest job"], 1,
                  "Round-robin gives each process a time quantum.", "medium"),
            ]),
            S("Memory", [
                Q("Virtual memory uses which technique to extend RAM?",
                  ["Caching", "Paging", "Pipelining", "Hashing"], 1,
                  "Paging swaps pages between RAM and disk.", "medium"),
                Q("Thrashing occurs due to:",
                  ["too little I/O", "excessive paging", "fast CPU", "large cache"], 1,
                  "Thrashing is excessive page swapping.", "hard"),
            ]),
        ]),

        # ── Computer Networks ───────────────────────────────────
        T("technical", "Computer Networks", icon="🌐", blurb="OSI, TCP/IP, protocols.", subtopics=[
            S("Protocols", [
                Q("HTTP typically runs on port:",
                  ["21", "25", "80", "443"], 2,
                  "HTTP uses port 80 (HTTPS uses 443).", "easy"),
                Q("Which protocol is connection-oriented?",
                  ["UDP", "TCP", "IP", "ICMP"], 1,
                  "TCP is reliable and connection-oriented.", "easy"),
                Q("DNS translates:",
                  ["IP to MAC", "domain names to IP", "IP to domain", "ports to services"], 1,
                  "DNS resolves domain names to IP addresses.", "easy"),
            ]),
            S("OSI Model", [
                Q("Which OSI layer handles routing?",
                  ["Data link", "Network", "Transport", "Session"], 1,
                  "The Network layer (L3) handles routing.", "medium"),
                Q("How many layers in the OSI model?",
                  ["5", "6", "7", "4"], 2,
                  "OSI has 7 layers.", "easy"),
            ]),
        ]),

        # ── Python ──────────────────────────────────────────────
        T("technical", "Python", icon="🐍", blurb="Syntax, data types, semantics.", subtopics=[
            S("Basics", [
                Q("Output of len('hello')?", ["4", "5", "6", "error"], 1,
                  "'hello' has 5 characters.", "easy"),
                Q("Which is an immutable type in Python?",
                  ["list", "dict", "tuple", "set"], 2,
                  "Tuples are immutable.", "easy"),
                Q("What does the '//' operator do?",
                  ["float division", "floor division", "modulus", "power"], 1,
                  "'//' is floor (integer) division.", "easy"),
                Q("Output of bool([])?", ["True", "False", "None", "error"], 1,
                  "An empty list is falsy.", "medium"),
            ]),
            S("Semantics", [
                Q("Python passes arguments by:",
                  ["value", "reference", "object reference (assignment)", "pointer"], 2,
                  "Python uses call-by-object-reference.", "hard"),
                Q("Which manages memory automatically in Python?",
                  ["manual free()", "garbage collector", "compiler", "linker"], 1,
                  "CPython uses reference counting + a garbage collector.", "medium"),
            ]),
        ]),

        # ── JavaScript ──────────────────────────────────────────
        T("technical", "JavaScript", icon="🟨", blurb="Types, scope, async.", subtopics=[
            S("Fundamentals", [
                Q("typeof null returns:", ["'null'", "'object'", "'undefined'", "'number'"], 1,
                  "A historical quirk: typeof null === 'object'.", "medium"),
                Q("Which keyword declares a block-scoped variable?",
                  ["var", "let", "function", "global"], 1,
                  "'let' (and 'const') are block-scoped.", "easy"),
                Q("'===' differs from '==' by:",
                  ["nothing", "checking type too", "being slower", "ignoring case"], 1,
                  "'===' checks value and type (no coercion).", "easy"),
            ]),
            S("Async", [
                Q("A Promise can be in states EXCEPT:",
                  ["pending", "fulfilled", "rejected", "cancelled"], 3,
                  "There is no native 'cancelled' state.", "medium"),
                Q("'await' can only be used inside:",
                  ["any function", "an async function", "a loop", "the global scope only"], 1,
                  "'await' requires an async function (or top-level module).", "medium"),
            ]),
        ]),
    ]
