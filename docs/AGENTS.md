# AGENTS.md - Developer & Agentic Workflow Guide

## 1. Core Operating Principles
When developing or extending the **Kabaddi Matches EDA** project, human developers and AI agents must adhere to the following principles:

1. **Source Immutability**:
   - The contents of `data/raw/` must NEVER be altered, overwritten, or mutated.
   - All cleaning and transformation logic must output exclusively to `data/cleaned/`.

2. **Deterministic & Reproducible Workflows**:
   - Every Jupyter notebook must execute sequentially from top to bottom (`Kernel -> Restart & Run All`) without throwing errors.
   - All random samplings, train-test splits, or clustering algorithms must specify `random_state=42`.

3. **Defensive Validation & Assertions**:
   - Every transformation must include assertions or validation checks (e.g., verifying row count integrity, asserting that points $\ge 0$, and confirming no unexpected NaNs in primary keys).

4. **Visual & Analytical Excellence**:
   - Visualizations must look publication-ready: custom color palettes (e.g., `#FF6F00`, `#1E88E5`, `#2E7D32`), clear figure titles, bold axis labels with units, and removed chart clutter.
   - All plots must be saved with high resolution (300 DPI) into `visuals/`.

---

## 2. Notebook Execution Responsibilities

### `notebooks/01_cleaning.ipynb` (Data Auditing & Cleaning)
- **Objective:** Ingest raw CSVs from `data/raw/`, audit missing data, remove duplicates, resolve data type issues, standardize entity names, and output validated clean CSVs into `data/cleaned/`.
- **Key Assertions:**
  - Check that all primary keys are unique.
  - Assert that all point metrics are non-negative.
  - Verify that boolean columns are strictly typed as `bool` or `int8`.
- **Target Deliverables:**
  - `data/cleaned/cleaned_matches.csv`
  - `data/cleaned/cleaned_teams.csv`
  - `data/cleaned/cleaned_players.csv`
  - `data/cleaned/cleaned_events.csv`

### `notebooks/02_features.ipynb` (Feature Engineering)
- **Objective:** Enrich cleaned data with advanced Kabaddi metrics:
  - Raid Strike Rate, Tackle Conversion Rate, Points Per Raid.
  - Player role classification (Raider, Defender, All-Rounder).
  - Match phase partitioning (Early, Mid, Late) and score differentials.
  - Clutch and pressure performance indicators (Do-or-die success, close match margin $\le 5$).
- **Target Deliverables:**
  - `data/cleaned/features_players.csv`
  - `data/cleaned/features_teams.csv`
  - `data/cleaned/features_events.csv`

### `notebooks/03_eda.ipynb` (Exploratory Data Analysis)
- **Objective:** Conduct rigorous statistical and visual analysis:
  - Univariate distribution of raid and tackle points.
  - Bivariate correlation between game elements (All-outs, Super Raids, Super Tackles) and winning probability.
  - Home advantage analysis and toss decision impact.
- **Target Deliverables:**
  - High-res charts exported to `visuals/*.png`.

### `notebooks/04_insights.ipynb` (Strategic Conclusions & Player Archetypes)
- **Objective:** Answer the 8 key analytical questions, formulate coach playbooks, and outline predictive modeling extensions.
- **Target Deliverables:**
  - Actionable summaries, statistical significance tables, and tactical insights.

---

## 3. Pre-Flight Verification Checklist
Before committing any changes or closing an analytical milestone, verify:
- [ ] Virtual environment `.venv` is active and `requirements.txt` is up-to-date.
- [ ] Source files in `data/raw/` match original checksums.
- [ ] Cleaned CSVs in `data/cleaned/` have zero unexpected nulls in primary identifiers.
- [ ] All charts exported to `visuals/` are readable with proper axes and legends.
- [ ] `README.md` documents steps to replicate the entire pipeline.
