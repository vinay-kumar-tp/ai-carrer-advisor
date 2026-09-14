"""Verbal Ability topics."""

from __future__ import annotations

from app.content.aptitude.framework import Q, S, T, Topic


def topics() -> list[Topic]:
    return [
        # ── Synonyms and Antonyms ───────────────────────────────
        T("verbal", "Vocabulary", icon="📖", blurb="Synonyms, antonyms, word meanings.", subtopics=[
            S("Synonyms", [
                Q("Choose the synonym for 'Ephemeral':",
                  ["Permanent", "Transient", "Eternal", "Substantial"], 1,
                  "Ephemeral means short-lived; transient is a synonym.", "medium"),
                Q("Synonym of 'Benevolent':",
                  ["Cruel", "Kind", "Greedy", "Rude"], 1,
                  "Benevolent means kind and generous.", "easy"),
                Q("Synonym of 'Abundant':",
                  ["Scarce", "Plentiful", "Empty", "Rare"], 1,
                  "Abundant means existing in large quantities.", "easy"),
                Q("Synonym of 'Meticulous':",
                  ["Careless", "Precise", "Lazy", "Vague"], 1,
                  "Meticulous means showing great attention to detail.", "medium"),
            ]),
            S("Antonyms", [
                Q("Antonym of 'Candid':",
                  ["Frank", "Honest", "Evasive", "Open"], 2,
                  "Candid means frank; its antonym is evasive.", "medium"),
                Q("Antonym of 'Expand':",
                  ["Grow", "Enlarge", "Contract", "Extend"], 2,
                  "Contract is the opposite of expand.", "easy"),
                Q("Antonym of 'Optimistic':",
                  ["Hopeful", "Positive", "Pessimistic", "Cheerful"], 2,
                  "Pessimistic is the opposite of optimistic.", "easy"),
            ]),
        ]),

        # ── Fill in the Blanks ──────────────────────────────────
        T("verbal", "Fill in the Blanks", icon="✏", blurb="Choose the word that best completes the sentence.", subtopics=[
            S("Grammar Fit", [
                Q("She is good ___ mathematics.", ["in", "at", "on", "with"], 1,
                  "'Good at' is the correct collocation.", "easy"),
                Q("He has been living here ___ 2010.", ["for", "since", "from", "by"], 1,
                  "'Since' is used with a point in time.", "easy"),
                Q("The results were ___ than expected.", ["good", "better", "best", "well"], 1,
                  "Comparative 'better' fits 'than'.", "easy"),
                Q("Neither of the boys ___ present.", ["are", "were", "was", "have"], 2,
                  "'Neither' takes a singular verb -> was.", "medium"),
            ]),
        ]),

        # ── Sentence Correction ─────────────────────────────────
        T("verbal", "Sentence Improvement", icon="🛠", blurb="Spot and fix grammatical errors.", subtopics=[
            S("Error Spotting", [
                Q("Choose the correct sentence:",
                  ["He don't like tea.", "He doesn't likes tea.", "He doesn't like tea.", "He not like tea."], 2,
                  "'He doesn't like tea' is grammatically correct.", "easy"),
                Q("Choose the correct sentence:",
                  ["Each of the students have a book.",
                   "Each of the students has a book.",
                   "Each of the student have a book.",
                   "Each of student has a book."], 1,
                  "'Each' is singular -> has.", "medium"),
                Q("Pick the correct form: 'The team ___ playing well.'",
                  ["are", "is", "were", "have"], 1,
                  "Collective noun 'team' takes 'is' here.", "medium"),
            ]),
        ]),

        # ── Reading Comprehension ───────────────────────────────
        T("verbal", "Reading Comprehension", icon="📰", blurb="Understand passages and infer meaning.", subtopics=[
            S("Inference", [
                Q("Passage: 'The library was silent except for turning pages.' The tone is:",
                  ["chaotic", "calm", "angry", "festive"], 1,
                  "Silence and pages suggest a calm, quiet tone.", "easy"),
                Q("'Renewable energy reduces reliance on fossil fuels.' The main idea is about:",
                  ["fossil fuels being cheap", "benefits of renewable energy", "banning cars", "coal mining"], 1,
                  "The sentence highlights a benefit of renewable energy.", "medium"),
            ]),
        ]),

        # ── Idioms and Phrases ──────────────────────────────────
        T("verbal", "Idioms and Phrases", icon="💬", blurb="Meanings of common idioms.", subtopics=[
            S("Common Idioms", [
                Q("'To bite the bullet' means:",
                  ["to eat fast", "to endure a painful situation", "to shoot", "to give up"], 1,
                  "It means to face a difficult situation bravely.", "medium"),
                Q("'Once in a blue moon' means:",
                  ["very often", "never", "rarely", "at night"], 2,
                  "It means something that happens very rarely.", "easy"),
                Q("'To spill the beans' means:",
                  ["to cook", "to reveal a secret", "to waste food", "to argue"], 1,
                  "It means to reveal secret information.", "easy"),
            ]),
        ]),
    ]
