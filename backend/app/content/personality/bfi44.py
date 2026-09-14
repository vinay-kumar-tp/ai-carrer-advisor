"""BFI-44 — the classic Big Five Inventory (John & Srivastava, 1999).

44 items, each prefixed in the UI by "I see myself as someone who…".
Keying (+/-) follows the published BFI scoring key.

Trait item counts: E=8, A=9, C=9, N=8, O=10.
"""

from __future__ import annotations

from app.content.personality.framework import Form, I


def form() -> Form:
    items = [
        # 1
        I("is talkative", "extraversion", "+"),
        I("tends to find fault with others", "agreeableness", "-"),
        I("does a thorough job", "conscientiousness", "+"),
        I("is depressed, blue", "neuroticism", "+"),
        I("is original, comes up with new ideas", "openness", "+"),
        I("is reserved", "extraversion", "-"),
        I("is helpful and unselfish with others", "agreeableness", "+"),
        I("can be somewhat careless", "conscientiousness", "-"),
        I("is relaxed, handles stress well", "neuroticism", "-"),
        I("is curious about many different things", "openness", "+"),
        # 11
        I("is full of energy", "extraversion", "+"),
        I("starts quarrels with others", "agreeableness", "-"),
        I("is a reliable worker", "conscientiousness", "+"),
        I("can be tense", "neuroticism", "+"),
        I("is ingenious, a deep thinker", "openness", "+"),
        I("generates a lot of enthusiasm", "extraversion", "+"),
        I("has a forgiving nature", "agreeableness", "+"),
        I("tends to be disorganized", "conscientiousness", "-"),
        I("worries a lot", "neuroticism", "+"),
        I("has an active imagination", "openness", "+"),
        # 21
        I("tends to be quiet", "extraversion", "-"),
        I("is generally trusting", "agreeableness", "+"),
        I("tends to be lazy", "conscientiousness", "-"),
        I("is emotionally stable, not easily upset", "neuroticism", "-"),
        I("is inventive", "openness", "+"),
        I("has an assertive personality", "extraversion", "+"),
        I("can be cold and aloof", "agreeableness", "-"),
        I("perseveres until the task is finished", "conscientiousness", "+"),
        I("can be moody", "neuroticism", "+"),
        I("values artistic, aesthetic experiences", "openness", "+"),
        # 31
        I("is sometimes shy, inhibited", "extraversion", "-"),
        I("is considerate and kind to almost everyone", "agreeableness", "+"),
        I("does things efficiently", "conscientiousness", "+"),
        I("remains calm in tense situations", "neuroticism", "-"),
        I("prefers work that is routine", "openness", "-"),
        I("is outgoing, sociable", "extraversion", "+"),
        I("is sometimes rude to others", "agreeableness", "-"),
        I("makes plans and follows through with them", "conscientiousness", "+"),
        I("gets nervous easily", "neuroticism", "+"),
        I("likes to reflect, play with ideas", "openness", "+"),
        # 41
        I("has few artistic interests", "openness", "-"),
        I("likes to cooperate with others", "agreeableness", "+"),
        I("is easily distracted", "conscientiousness", "-"),
        I("is sophisticated in art, music, or literature", "openness", "+"),
    ]
    return Form(
        key="bfi44",
        name="BFI-44 Personality Test",
        short_name="Quick Assessment",
        description="Standard BFI-44 personality test — the classic, validated short form.",
        est_minutes=10,
        items=items,
    )
