"""Quantitative Aptitude topics."""

from __future__ import annotations

from app.content.aptitude.framework import Q, S, T, Topic


def topics() -> list[Topic]:
    return [
        # ── Percentage ──────────────────────────────────────────
        T("quant", "Percentage", icon="%", blurb="Conversions, increase/decrease, and applications.", subtopics=[
            S("Basics", [
                Q("What is 25% of 240?", ["48", "50", "60", "64"], 2,
                  "25% = 1/4, so 240 / 4 = 60.", "easy"),
                Q("Convert 0.35 to a percentage.", ["3.5%", "35%", "0.35%", "350%"], 1,
                  "Multiply by 100: 0.35 x 100 = 35%.", "easy"),
                Q("What percent of 80 is 20?", ["20%", "25%", "40%", "15%"], 1,
                  "(20/80) x 100 = 25%.", "easy"),
                Q("If a number is increased by 20% to become 360, the original number is:",
                  ["280", "300", "320", "340"], 1,
                  "x * 1.2 = 360 -> x = 300.", "medium"),
                Q("60% of a class of 50 students passed. How many failed?",
                  ["20", "25", "30", "15"], 0,
                  "60% passed -> 40% failed = 0.4 x 50 = 20.", "easy"),
            ]),
            S("Successive Change", [
                Q("A price rises 10% then falls 10%. Net change is:",
                  ["0%", "-1%", "+1%", "-2%"], 1,
                  "Net = 10 - 10 - (10x10)/100 = -1%.", "medium"),
                Q("A salary increases 20% then 25%. Overall increase is:",
                  ["45%", "50%", "40%", "55%"], 1,
                  "1.2 x 1.25 = 1.5 -> 50% increase.", "medium"),
                Q("Length +20% and breadth -20%: area changes by:",
                  ["0%", "-4%", "+4%", "-2%"], 1,
                  "1.2 x 0.8 = 0.96 -> -4%.", "medium"),
                Q("A quantity is reduced 25% twice. Final fraction of original:",
                  ["1/2", "9/16", "3/4", "7/16"], 1,
                  "0.75 x 0.75 = 0.5625 = 9/16.", "hard"),
            ]),
            S("Word Problems", [
                Q("In an election of two candidates, the winner got 60% and won by 400 votes. Total votes:",
                  ["1600", "2000", "2400", "1800"], 1,
                  "Margin 60-40 = 20% = 400 -> total = 2000.", "medium"),
                Q("A student scored 45% and failed by 15 marks; pass mark is 40% of... no, pass is 150. Max marks if 45% = 180:",
                  ["360", "400", "420", "450"], 1,
                  "45% = 180 -> max = 180/0.45 = 400.", "medium"),
                Q("Water is 90% of a 50 kg melon. After drying, water is 80%. New weight:",
                  ["25 kg", "45 kg", "40 kg", "30 kg"], 0,
                  "Pulp 5 kg is now 20% -> total = 25 kg.", "hard"),
            ]),
        ]),

        # ── Profit, Loss and Discount ───────────────────────────
        T("quant", "Profit Loss and Discount", icon="₹", blurb="CP, SP, markup, and discounts.", subtopics=[
            S("Profit and Loss", [
                Q("CP = 400, SP = 500. Profit % is:", ["20%", "25%", "10%", "15%"], 1,
                  "Profit = 100, % = 100/400 = 25%.", "easy"),
                Q("An item sold at 480 for a 20% profit. Cost price:",
                  ["360", "384", "400", "420"], 2,
                  "480/1.2 = 400.", "easy"),
                Q("Selling at 270 gives 10% loss. Cost price:",
                  ["300", "290", "310", "297"], 0,
                  "270/0.9 = 300.", "medium"),
                Q("Buying 3 for 10 and selling 4 for 15 gives profit %:",
                  ["12.5%", "10%", "12%", "15%"], 0,
                  "CP/unit=3.33, SP/unit=3.75 -> 12.5%.", "hard"),
            ]),
            S("Discount", [
                Q("Marked price 800, discount 25%. Selling price:",
                  ["550", "600", "620", "640"], 1,
                  "800 x 0.75 = 600.", "easy"),
                Q("After two successive discounts of 10% and 20%, MP 1000 becomes:",
                  ["700", "720", "740", "680"], 1,
                  "1000 x 0.9 x 0.8 = 720.", "medium"),
                Q("A shopkeeper marks 40% above cost, gives 25% discount. Profit %:",
                  ["5%", "10%", "15%", "8%"], 0,
                  "1.4 x 0.75 = 1.05 -> 5%.", "hard"),
            ]),
        ]),

        # ── Time and Work ───────────────────────────────────────
        T("quant", "Time and Work", icon="⏱", blurb="Work rates, pipes and cisterns, efficiency.", subtopics=[
            S("Basic Work", [
                Q("A does a job in 10 days, B in 15 days. Together they finish in:",
                  ["5 days", "6 days", "7 days", "8 days"], 1,
                  "1/10 + 1/15 = 1/6 -> 6 days.", "easy"),
                Q("If 5 workers finish in 12 days, 10 workers finish in:",
                  ["4", "6", "8", "10"], 1,
                  "Work = 60 worker-days; 60/10 = 6 days.", "easy"),
                Q("A is twice as efficient as B and finishes in 6 days. B alone takes:",
                  ["9", "12", "10", "8"], 1,
                  "A takes 6, B (half efficient) takes 12 days.", "medium"),
                Q("A and B finish in 12 days; A alone in 20 days. B alone:",
                  ["30", "25", "28", "24"], 0,
                  "1/12 - 1/20 = 1/30 -> 30 days.", "medium"),
            ]),
            S("Pipes and Cisterns", [
                Q("A pipe fills a tank in 6 hours, another empties it in 8 hours. Together fill in:",
                  ["24 h", "20 h", "26 h", "22 h"], 0,
                  "1/6 - 1/8 = 1/24 -> 24 hours.", "medium"),
                Q("Two pipes fill in 12 and 18 minutes. Together they take:",
                  ["7.2 min", "8 min", "6 min", "9 min"], 0,
                  "1/12 + 1/18 = 5/36 -> 36/5 = 7.2 min.", "medium"),
                Q("A tank filled by A in 4 h; a leak empties full tank in 12 h. With leak, fills in:",
                  ["6 h", "5 h", "8 h", "7 h"], 0,
                  "1/4 - 1/12 = 1/6 -> 6 hours.", "hard"),
            ]),
        ]),

        # ── Time Speed and Distance ─────────────────────────────
        T("quant", "Time Speed and Distance", icon="🚗", blurb="Average speed, relative speed, trains, boats.", subtopics=[
            S("Speed Basics", [
                Q("A car covers 150 km in 3 hours. Its speed is:",
                  ["45 km/h", "50 km/h", "55 km/h", "60 km/h"], 1,
                  "150/3 = 50 km/h.", "easy"),
                Q("Convert 72 km/h to m/s.", ["18", "20", "25", "15"], 1,
                  "72 x 5/18 = 20 m/s.", "easy"),
                Q("A man walks 6 km at 3 km/h and returns at 6 km/h. Average speed:",
                  ["4", "4.5", "5", "3.5"], 0,
                  "Harmonic mean = 2*3*6/(3+6) = 4 km/h.", "medium"),
            ]),
            S("Trains", [
                Q("A 120 m train at 36 km/h crosses a pole in:",
                  ["10 s", "12 s", "15 s", "8 s"], 1,
                  "36 km/h = 10 m/s; 120/10 = 12 s.", "medium"),
                Q("A 150 m train crosses a 350 m bridge in 25 s. Its speed (km/h):",
                  ["72", "60", "80", "66"], 0,
                  "Distance 500 m / 25 s = 20 m/s = 72 km/h.", "hard"),
            ]),
        ]),

        # ── Ratio and Averages ──────────────────────────────────
        T("quant", "Ratio Proportion and Mixtures", icon="⚖", blurb="Ratios, proportions, alligation.", subtopics=[
            S("Ratios", [
                Q("Divide 600 in the ratio 2:3. The larger part is:",
                  ["240", "300", "360", "400"], 2,
                  "Parts 240 and 360; larger = 360.", "easy"),
                Q("If a:b = 2:3 and b:c = 4:5, then a:c is:",
                  ["8:15", "2:5", "8:5", "3:5"], 0,
                  "a:b:c = 8:12:15 -> a:c = 8:15.", "medium"),
            ]),
            S("Mixtures", [
                Q("In what ratio mix rice at 20 and 30 to get 24?",
                  ["3:2", "2:3", "1:1", "3:1"], 0,
                  "Alligation: (30-24):(24-20) = 6:4 = 3:2.", "hard"),
                Q("A 40 L mix is 3:1 milk:water. Water to add for 1:1 ratio:",
                  ["20 L", "10 L", "15 L", "25 L"], 0,
                  "Milk 30, water 10; need water 30 -> add 20 L.", "hard"),
            ]),
        ]),

        # ── Simple and Compound Interest ────────────────────────
        T("quant", "Simple and Compound Interest", icon="🏦", blurb="SI, CI, and their comparison.", subtopics=[
            S("Simple Interest", [
                Q("SI on 2000 at 5% for 3 years:", ["250", "300", "350", "400"], 1,
                  "2000 x 5 x 3 / 100 = 300.", "easy"),
                Q("A sum doubles in 8 years at simple interest. The rate is:",
                  ["10%", "12.5%", "8%", "15%"], 1,
                  "SI = P in 8 yrs -> rate = 100/8 = 12.5%.", "medium"),
            ]),
            S("Compound Interest", [
                Q("CI on 1000 at 10% for 2 years:", ["200", "210", "220", "215"], 1,
                  "1000 x 1.1^2 = 1210 -> CI = 210.", "medium"),
                Q("Difference between CI and SI on 5000 at 10% for 2 years:",
                  ["50", "60", "45", "55"], 0,
                  "Diff = P(r/100)^2 = 5000 x 0.01 = 50.", "hard"),
            ]),
        ]),

        # ── Number System ───────────────────────────────────────
        T("quant", "Number System", icon="🔢", blurb="Divisibility, HCF/LCM, remainders.", subtopics=[
            S("Divisibility", [
                Q("Which is divisible by 9?", ["1234", "5081", "6714", "2358"], 3,
                  "2+3+5+8 = 18, divisible by 9.", "easy"),
                Q("The LCM of 12 and 18 is:", ["36", "24", "72", "54"], 0,
                  "LCM(12,18) = 36.", "easy"),
                Q("The HCF of 24 and 36 is:", ["6", "12", "8", "18"], 1,
                  "HCF = 12.", "easy"),
            ]),
            S("Remainders", [
                Q("Remainder when 17^2 is divided by 5:", ["1", "2", "3", "4"], 3,
                  "289 mod 5 = 4.", "medium"),
                Q("The unit digit of 7^4 is:", ["1", "3", "7", "9"], 0,
                  "7 cycle 7,9,3,1 -> 7^4 ends in 1.", "medium"),
            ]),
        ]),
    ]
