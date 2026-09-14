"""IPIP-NEO-120 — 120-item public-domain Big Five measure (Johnson, 2014).

Six facets per trait, four items per facet (5 traits x 6 facets x 4 = 120).
Items are phrased to follow "I see myself as someone who…" and carry +/- keying
consistent with the IPIP-NEO scoring direction.
"""

from __future__ import annotations

from app.content.personality.framework import Form, I


def form() -> Form:
    items = [
        # ── NEUROTICISM ───────────────────────────────────────
        # Anxiety
        I("worries about things", "neuroticism", "+", "Anxiety"),
        I("fears for the worst", "neuroticism", "+", "Anxiety"),
        I("is afraid of many things", "neuroticism", "+", "Anxiety"),
        I("gets stressed out easily", "neuroticism", "+", "Anxiety"),
        # Anger
        I("gets angry easily", "neuroticism", "+", "Anger"),
        I("gets irritated easily", "neuroticism", "+", "Anger"),
        I("loses their temper", "neuroticism", "+", "Anger"),
        I("keeps their cool", "neuroticism", "-", "Anger"),
        # Depression
        I("often feels blue", "neuroticism", "+", "Depression"),
        I("dislikes themselves", "neuroticism", "+", "Depression"),
        I("is often down in the dumps", "neuroticism", "+", "Depression"),
        I("feels comfortable with themselves", "neuroticism", "-", "Depression"),
        # Self-Consciousness
        I("is easily intimidated", "neuroticism", "+", "Self-Consciousness"),
        I("is afraid to draw attention to themselves", "neuroticism", "+", "Self-Consciousness"),
        I("only feels comfortable with friends", "neuroticism", "+", "Self-Consciousness"),
        I("is not embarrassed easily", "neuroticism", "-", "Self-Consciousness"),
        # Immoderation
        I("goes on binges", "neuroticism", "+", "Immoderation"),
        I("rarely overindulges", "neuroticism", "-", "Immoderation"),
        I("easily resists temptations", "neuroticism", "-", "Immoderation"),
        I("is able to control cravings", "neuroticism", "-", "Immoderation"),
        # Vulnerability
        I("panics easily", "neuroticism", "+", "Vulnerability"),
        I("becomes overwhelmed by events", "neuroticism", "+", "Vulnerability"),
        I("feels that they are unable to deal with things", "neuroticism", "+", "Vulnerability"),
        I("remains calm under pressure", "neuroticism", "-", "Vulnerability"),

        # ── EXTRAVERSION ──────────────────────────────────────
        # Friendliness
        I("makes friends easily", "extraversion", "+", "Friendliness"),
        I("warms up quickly to others", "extraversion", "+", "Friendliness"),
        I("feels comfortable around people", "extraversion", "+", "Friendliness"),
        I("acts comfortably with others", "extraversion", "+", "Friendliness"),
        # Gregariousness
        I("loves large parties", "extraversion", "+", "Gregariousness"),
        I("talks to a lot of different people at parties", "extraversion", "+", "Gregariousness"),
        I("prefers to be alone", "extraversion", "-", "Gregariousness"),
        I("avoids crowds", "extraversion", "-", "Gregariousness"),
        # Assertiveness
        I("takes charge", "extraversion", "+", "Assertiveness"),
        I("tries to lead others", "extraversion", "+", "Assertiveness"),
        I("takes control of things", "extraversion", "+", "Assertiveness"),
        I("waits for others to lead the way", "extraversion", "-", "Assertiveness"),
        # Activity Level
        I("is always busy", "extraversion", "+", "Activity Level"),
        I("is always on the go", "extraversion", "+", "Activity Level"),
        I("does a lot in their spare time", "extraversion", "+", "Activity Level"),
        I("likes to take it easy", "extraversion", "-", "Activity Level"),
        # Excitement-Seeking
        I("loves excitement", "extraversion", "+", "Excitement-Seeking"),
        I("seeks adventure", "extraversion", "+", "Excitement-Seeking"),
        I("enjoys being reckless", "extraversion", "+", "Excitement-Seeking"),
        I("acts wild and crazy", "extraversion", "+", "Excitement-Seeking"),
        # Cheerfulness
        I("radiates joy", "extraversion", "+", "Cheerfulness"),
        I("has a lot of fun", "extraversion", "+", "Cheerfulness"),
        I("loves life", "extraversion", "+", "Cheerfulness"),
        I("looks at the bright side of life", "extraversion", "+", "Cheerfulness"),

        # ── OPENNESS ──────────────────────────────────────────
        # Imagination
        I("has a vivid imagination", "openness", "+", "Imagination"),
        I("enjoys wild flights of fantasy", "openness", "+", "Imagination"),
        I("loves to daydream", "openness", "+", "Imagination"),
        I("likes to get lost in thought", "openness", "+", "Imagination"),
        # Artistic Interests
        I("believes in the importance of art", "openness", "+", "Artistic Interests"),
        I("sees beauty in things that others might not notice", "openness", "+", "Artistic Interests"),
        I("does not like poetry", "openness", "-", "Artistic Interests"),
        I("does not enjoy going to art museums", "openness", "-", "Artistic Interests"),
        # Emotionality
        I("experiences their emotions intensely", "openness", "+", "Emotionality"),
        I("feels others' emotions", "openness", "+", "Emotionality"),
        I("rarely notices their emotional reactions", "openness", "-", "Emotionality"),
        I("does not understand people who get emotional", "openness", "-", "Emotionality"),
        # Adventurousness
        I("prefers variety to routine", "openness", "+", "Adventurousness"),
        I("prefers to stick with things they know", "openness", "-", "Adventurousness"),
        I("dislikes changes", "openness", "-", "Adventurousness"),
        I("is attached to conventional ways", "openness", "-", "Adventurousness"),
        # Intellect
        I("likes to solve complex problems", "openness", "+", "Intellect"),
        I("loves to read challenging material", "openness", "+", "Intellect"),
        I("avoids philosophical discussions", "openness", "-", "Intellect"),
        I("has difficulty understanding abstract ideas", "openness", "-", "Intellect"),
        # Liberalism
        I("tends to vote for liberal political candidates", "openness", "+", "Liberalism"),
        I("believes that there is no absolute right or wrong", "openness", "+", "Liberalism"),
        I("tends to vote for conservative political candidates", "openness", "-", "Liberalism"),
        I("believes laws should be strictly enforced", "openness", "-", "Liberalism"),

        # ── AGREEABLENESS ─────────────────────────────────────
        # Trust
        I("trusts others", "agreeableness", "+", "Trust"),
        I("believes that others have good intentions", "agreeableness", "+", "Trust"),
        I("trusts what people say", "agreeableness", "+", "Trust"),
        I("distrusts people", "agreeableness", "-", "Trust"),
        # Morality
        I("would never cheat on their taxes", "agreeableness", "+", "Morality"),
        I("sticks to the rules", "agreeableness", "+", "Morality"),
        I("uses others for their own ends", "agreeableness", "-", "Morality"),
        I("cheats to get ahead", "agreeableness", "-", "Morality"),
        # Altruism
        I("makes people feel welcome", "agreeableness", "+", "Altruism"),
        I("is concerned about others", "agreeableness", "+", "Altruism"),
        I("loves to help others", "agreeableness", "+", "Altruism"),
        I("is indifferent to the feelings of others", "agreeableness", "-", "Altruism"),
        # Cooperation
        I("is easy to satisfy", "agreeableness", "+", "Cooperation"),
        I("hates to seem pushy", "agreeableness", "+", "Cooperation"),
        I("loves a good fight", "agreeableness", "-", "Cooperation"),
        I("yells at people", "agreeableness", "-", "Cooperation"),
        # Modesty
        I("dislikes being the center of attention", "agreeableness", "+", "Modesty"),
        I("considers themselves an average person", "agreeableness", "+", "Modesty"),
        I("believes that they are better than others", "agreeableness", "-", "Modesty"),
        I("thinks highly of themselves", "agreeableness", "-", "Modesty"),
        # Sympathy
        I("sympathizes with the homeless", "agreeableness", "+", "Sympathy"),
        I("feels sympathy for those worse off than themselves", "agreeableness", "+", "Sympathy"),
        I("is not interested in other people's problems", "agreeableness", "-", "Sympathy"),
        I("tries not to think about the needy", "agreeableness", "-", "Sympathy"),

        # ── CONSCIENTIOUSNESS ─────────────────────────────────
        # Self-Efficacy
        I("completes tasks successfully", "conscientiousness", "+", "Self-Efficacy"),
        I("excels in what they do", "conscientiousness", "+", "Self-Efficacy"),
        I("handles tasks smoothly", "conscientiousness", "+", "Self-Efficacy"),
        I("knows how to get things done", "conscientiousness", "+", "Self-Efficacy"),
        # Orderliness
        I("likes to tidy up", "conscientiousness", "+", "Orderliness"),
        I("likes order", "conscientiousness", "+", "Orderliness"),
        I("leaves a mess in their room", "conscientiousness", "-", "Orderliness"),
        I("leaves their belongings around", "conscientiousness", "-", "Orderliness"),
        # Dutifulness
        I("keeps their promises", "conscientiousness", "+", "Dutifulness"),
        I("tells the truth", "conscientiousness", "+", "Dutifulness"),
        I("breaks rules", "conscientiousness", "-", "Dutifulness"),
        I("breaks their promises", "conscientiousness", "-", "Dutifulness"),
        # Achievement-Striving
        I("works hard", "conscientiousness", "+", "Achievement-Striving"),
        I("does more than what's expected of them", "conscientiousness", "+", "Achievement-Striving"),
        I("sets high standards for themselves and others", "conscientiousness", "+", "Achievement-Striving"),
        I("does just enough work to get by", "conscientiousness", "-", "Achievement-Striving"),
        # Self-Discipline
        I("is always prepared", "conscientiousness", "+", "Self-Discipline"),
        I("carries out their plans", "conscientiousness", "+", "Self-Discipline"),
        I("wastes their time", "conscientiousness", "-", "Self-Discipline"),
        I("has difficulty starting tasks", "conscientiousness", "-", "Self-Discipline"),
        # Cautiousness
        I("thinks things through before acting", "conscientiousness", "+", "Cautiousness"),
        I("avoids making rash decisions", "conscientiousness", "+", "Cautiousness"),
        I("makes rash decisions", "conscientiousness", "-", "Cautiousness"),
        I("acts without thinking", "conscientiousness", "-", "Cautiousness"),
    ]
    return Form(
        key="ipip120",
        name="IPIP-NEO-120 Personality Test",
        short_name="Comprehensive Assessment",
        description="IPIP-NEO-120 — measures 6 facets per trait for deep personality insight.",
        est_minutes=25,
        items=items,
    )
