# Kabaddi Matches - Exploratory Data Analysis (EDA)

## 1. Project Overview & Pitch
**Analyze event-level Kabaddi match data to uncover player and team performance trends through rigorous data cleaning, feature engineering, visualization, and exploratory data analysis.**

In modern sports analytics, Kabaddi generates hundreds of micro-events per match (raids, touches, bonus points, tackles, super tackles, do-or-die situations, all-outs). Raw event logs contain immense tactical depth, but without structured cleaning and synthesis, coaches, analysts, and fans cannot easily pinpoint what separates winning teams from losing ones, which raiders thrive under pressure, or how defensive setups adapt across match halves.

---

## 2. Core Problem Statement
Raw match feeds contain noisy event entries, duplicated rows, mixed data types, and incomplete player role labels. This project builds a reliable end-to-end analytical pipeline to transform event-level, player-level, team-level, and match-level records into actionable, data-backed insights.

---

## 3. Project Goals
1. **Standardize and Clean Raw Data**: Ensure pristine integrity across matches, teams, players, and granular raid/tackle events without modifying the source raw data.
2. **Player Performance Profiling**: Quantify raiders, defenders, and all-rounders by volume, efficiency (success rates), and pressure performance (do-or-die raids, super raids, super tackles).
3. **Team Performance Dynamics**: Unpack attack vs. defense balances, all-out conversions, consistency, and clutch execution in close finishes (margins $\le 5$ points).
4. **Contextual & Phase-Wise Analysis**: Measure performance trends across early, mid, and late match clocks, home-court advantage, and seasonal evolutions.
5. **Interactive & Publication-Grade Deliverables**: Present reproducible Jupyter notebooks, publication-ready visualizations, clear business insights, and an optional dashboard.

---

## 4. Key Analytical Questions
1. **Elite Raiders & Defenders**: Who leads in total points vs. strike rate / tackle efficiency?
2. **Team Strategy Profiles**: Which teams rely on high-octane raiding vs. brick-wall defense?
3. **Match Turnarounds**: How decisively do super raids, super tackles, and all-outs tip match win probabilities?
4. **Clutch Play**: Which teams and players maintain composure and high success rates in tight match endings?
5. **Phase Dynamics**: How do raid risk-taking and tackle aggressiveness shift between the 1st half and 2nd half?
6. **Venue & Toss Impact**: Does court selection, toss decision, or home-court advantage play a significant statistical role?
7. **Consistency vs. Volatility**: Which players deliver high floor performance match after match versus feast-or-famine scorers?
8. **Season Trajectories**: How has the league evolved over seasons in scoring rate, tackle aggressiveness, and raid duration?

---

## 5. Target Stakeholders
- **Coaches & Performance Analysts**: Tactical benchmarking, lineup decisions, matchup counter-strategies.
- **Kabaddi Fans & Media Commentators**: Storytelling metrics, momentum charts, head-to-head comparisons.
- **Sports Data Scientists & Students**: Portfolio-grade analytical workflow demonstrating robust data cleaning, feature engineering, and exploratory analytics.

---

## 6. Project Architecture
```
kabaddi-eda/
├── data/
│   ├── raw/                  # Source immutable CSVs (matches, events, players, teams, roles)
│   └── cleaned/              # Standardized, type-cast, feature-enriched datasets
├── notebooks/
│   ├── 01_cleaning.ipynb     # Data audit, anomaly detection, type casting, imputation
│   ├── 02_features.ipynb     # Metric engineering (strike rates, pressure metrics, phase tags)
│   ├── 03_eda.ipynb          # Univariate, bivariate, multivariate visualizations & statistical tests
│   └── 04_insights.ipynb     # Strategic conclusions, team/player archetypes, recommendations
├── visuals/                  # High-resolution saved plots & charts
├── docs/                     # Technical specifications & documentation
│   ├── idea.md               # Project concept & pitch
│   ├── PRD.md                # Product Requirements Document
│   ├── DATABASE.md           # Schema definitions, ERD, dictionary
│   └── AGENTS.md             # Developer & Agent execution rules
├── README.md                 # Public repository guide & executive summary
└── requirements.txt          # Python library dependencies
```
