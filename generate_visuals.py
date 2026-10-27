import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns

# Create output dir
OUTPUT_DIR = "visuals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set high-DPI dark theme styling matching Power BI dashboard
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#30363d'
plt.rcParams['axes.linewidth'] = 1.0

DARK_BG = '#0d1117'
CARD_BG = '#161b22'
TEXT_COLOR = '#e6edf3'
MUTED_TEXT = '#8b949e'
ACCENT_ORANGE = '#ff7b00'
ACCENT_CYAN = '#00e5ff'
ACCENT_BLUE = '#58a6ff'
ACCENT_GREEN = '#3fb950'
ACCENT_YELLOW = '#ffb703'

# Load Cleaned Data
df_matches = pd.read_csv("data/cleaned/cleaned_matches.csv")
df_teams = pd.read_csv("data/cleaned/cleaned_teams.csv")
df_players = pd.read_csv("data/cleaned/cleaned_players.csv")

print("Loaded datasets for visual generation.")

# -------------------------------------------------------------
# 1. Team Tactical Matrix (Raid Power vs. Defensive Wall)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7), facecolor=DARK_BG)
ax.set_facecolor(CARD_BG)

team_perf = df_teams.groupby('team_name').agg({
    'raid_points_total': 'mean',
    'tackle_points_total': 'mean',
    'score': 'mean',
    'all_outs_inflicted': 'sum',
    'match_id': 'count'
}).reset_index().rename(columns={'match_id': 'matches_played'})

team_perf = team_perf[team_perf['matches_played'] >= 10]

mean_raid = team_perf['raid_points_total'].mean()
mean_tackle = team_perf['tackle_points_total'].mean()

# Quadrant dividers
ax.axvline(mean_raid, color='#30363d', linestyle='--', linewidth=1.2, zorder=1)
ax.axhline(mean_tackle, color='#30363d', linestyle='--', linewidth=1.2, zorder=1)

# Annotate quadrants
ax.text(team_perf['raid_points_total'].max() - 0.5, team_perf['tackle_points_total'].max() - 0.2,
        'ELITE ATTACK & DEFENSE', color=ACCENT_GREEN, fontsize=9, fontweight='bold', ha='right', alpha=0.8)
ax.text(team_perf['raid_points_total'].min() + 0.2, team_perf['tackle_points_total'].max() - 0.2,
        'DEFENSIVE FORTRESS', color=ACCENT_CYAN, fontsize=9, fontweight='bold', ha='left', alpha=0.8)
ax.text(team_perf['raid_points_total'].max() - 0.5, team_perf['tackle_points_total'].min() + 0.2,
        'HIGH-SCORING / VULNERABLE', color=ACCENT_ORANGE, fontsize=9, fontweight='bold', ha='right', alpha=0.8)

# Scatter points
scatter = ax.scatter(
    team_perf['raid_points_total'],
    team_perf['tackle_points_total'],
    s=team_perf['all_outs_inflicted'] * 3.5 + 100,
    c=team_perf['score'],
    cmap='viridis',
    edgecolors=ACCENT_CYAN,
    linewidth=1.5,
    alpha=0.9,
    zorder=3
)

# Text labels
for _, row in team_perf.iterrows():
    ax.annotate(
        row['team_name'],
        (row['raid_points_total'], row['tackle_points_total']),
        xytext=(0, 7),
        textcoords="offset points",
        fontsize=8.5,
        fontweight='semibold',
        color=TEXT_COLOR,
        ha='center',
        va='bottom',
        zorder=4
    )

cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('Average Match Score', color=TEXT_COLOR, fontsize=10, labelpad=8)
cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=TEXT_COLOR)

ax.set_title("Franchise Tactical Matrix: Raid Power vs. Defensive Wall", fontsize=15, fontweight='bold', color='#ffffff', pad=15)
ax.set_xlabel("Average Raid Points Scored per Match", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.set_ylabel("Average Tackle Points Scored per Match", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.tick_params(colors=TEXT_COLOR, which='both')
ax.grid(True, linestyle=':', alpha=0.15, color='#ffffff')

plt.tight_layout()
p1 = os.path.join(OUTPUT_DIR, "01_team_tactical_matrix.png")
fig.savefig(p1, facecolor=DARK_BG, bbox_inches='tight')
plt.close()
print(f"Generated {p1}")

# -------------------------------------------------------------
# 2. Top Raiders by Total Points & Strike Efficiency (PPR)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7), facecolor=DARK_BG)
ax.set_facecolor(CARD_BG)

raider_agg = df_players.groupby(['player_name', 'player_category']).agg({
    'player_raid_points_total': 'sum',
    'player_raids_total': 'sum',
    'player_raids_successful': 'sum'
}).reset_index()

raiders_q = raider_agg[raider_agg['player_raids_total'] >= 50].copy()
raiders_q['strike_rate'] = (raiders_q['player_raids_successful'] / raiders_q['player_raids_total']) * 100
raiders_q['ppr'] = raiders_q['player_raid_points_total'] / raiders_q['player_raids_total']
top12_raiders = raiders_q.sort_values(by='player_raid_points_total', ascending=True).tail(12)

norm = plt.Normalize(top12_raiders['ppr'].min(), top12_raiders['ppr'].max())
colors = plt.cm.plasma(norm(top12_raiders['ppr']))

bars = ax.barh(top12_raiders['player_name'], top12_raiders['player_raid_points_total'], color=colors, height=0.65, zorder=2)

for bar, (_, row) in zip(bars, top12_raiders.iterrows()):
    w = bar.get_width()
    ax.text(w + 12, bar.get_y() + bar.get_height()/2,
            f"{int(w):,} pts  ({row['strike_rate']:.1f}% SR | {row['ppr']:.2f} PPR)",
            ha='left', va='center', color=TEXT_COLOR, fontsize=8.5, fontweight='semibold')

ax.set_xlim(0, top12_raiders['player_raid_points_total'].max() * 1.32)
ax.set_title("Top 12 Pro Kabaddi Raiders: Career Points & Strike Efficiency", fontsize=15, fontweight='bold', color='#ffffff', pad=15)
ax.set_xlabel("Career Raid Points", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.tick_params(colors=TEXT_COLOR, which='both')
ax.grid(True, axis='x', linestyle=':', alpha=0.15, color='#ffffff')

plt.tight_layout()
p2 = os.path.join(OUTPUT_DIR, "02_top_raiders_efficiency.png")
fig.savefig(p2, facecolor=DARK_BG, bbox_inches='tight')
plt.close()
print(f"Generated {p2}")

# -------------------------------------------------------------
# 3. Top Defenders by Tackle Points & Success Rate
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7), facecolor=DARK_BG)
ax.set_facecolor(CARD_BG)

def_agg = df_players.groupby(['player_name', 'player_category']).agg({
    'player_tackle_points_total': 'sum',
    'player_tackles_total': 'sum',
    'player_tackles_successful': 'sum',
    'player_tackles_unsuccessful': 'sum'
}).reset_index()

def_q = def_agg[def_agg['player_tackles_total'] >= 30].copy()
def_q['conversion'] = (def_q['player_tackles_successful'] / def_q['player_tackles_total']) * 100
top12_def = def_q.sort_values(by='player_tackle_points_total', ascending=True).tail(12)

bars_succ = ax.barh(top12_def['player_name'], top12_def['player_tackles_successful'],
                    color=ACCENT_CYAN, label='Successful Captures', height=0.6, zorder=2)
bars_unsucc = ax.barh(top12_def['player_name'], top12_def['player_tackles_unsuccessful'],
                      left=top12_def['player_tackles_successful'], color='#f85149', alpha=0.7,
                      label='Unsuccessful Attempts', height=0.6, zorder=2)

for _, row in top12_def.iterrows():
    tot = row['player_tackles_total']
    ax.text(tot + 8, row['player_name'],
            f"{int(row['player_tackle_points_total'])} pts ({row['conversion']:.1f}% Win Rate)",
            va='center', color=TEXT_COLOR, fontsize=8.5, fontweight='semibold')

ax.set_xlim(0, top12_def['player_tackles_total'].max() * 1.35)
ax.set_title("Top 12 Defensive Fortresses: Tackle Volume & Conversion Rate", fontsize=15, fontweight='bold', color='#ffffff', pad=15)
ax.set_xlabel("Total Tackle Engagements", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.legend(facecolor=DARK_BG, edgecolor='#30363d', labelcolor=TEXT_COLOR, loc='lower right')
ax.tick_params(colors=TEXT_COLOR, which='both')
ax.grid(True, axis='x', linestyle=':', alpha=0.15, color='#ffffff')

plt.tight_layout()
p3 = os.path.join(OUTPUT_DIR, "03_top_defenders_tackles.png")
fig.savefig(p3, facecolor=DARK_BG, bbox_inches='tight')
plt.close()
print(f"Generated {p3}")

# -------------------------------------------------------------
# 4. Victory Margin Distribution (Close Match Analysis)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6), facecolor=DARK_BG)
ax.set_facecolor(CARD_BG)

team_margins = df_teams.groupby('match_id')['score'].agg(lambda s: abs(s.iloc[0] - s.iloc[1]) if len(s) == 2 else 0).reset_index()
team_margins.columns = ['match_id', 'margin']
close_count = (team_margins['margin'] <= 5).sum()
close_pct = (close_count / len(team_margins)) * 100

n, bins, patches_list = ax.hist(team_margins['margin'], bins=28, edgecolor=DARK_BG, linewidth=1.2, zorder=2)
for patch, b in zip(patches_list, bins):
    if b <= 5:
        patch.set_facecolor(ACCENT_ORANGE)
    else:
        patch.set_facecolor(ACCENT_BLUE)

ax.axvline(5.5, color='#ffffff', linestyle='--', linewidth=1.5, alpha=0.8, zorder=3)
ax.text(6.0, ax.get_ylim()[1] * 0.85, f"Clutch Margin Barrier (≤ 5 Pts)\n{close_pct:.1f}% of all matches ({close_count} games)",
        color=ACCENT_ORANGE, fontsize=10, fontweight='bold')

custom_lines = [patches.Patch(facecolor=ACCENT_ORANGE, label='Clutch Finish (≤ 5 pts)'),
                patches.Patch(facecolor=ACCENT_BLUE, label='Comfortable Margin (> 5 pts)')]
ax.legend(handles=custom_lines, facecolor=DARK_BG, edgecolor='#30363d', labelcolor=TEXT_COLOR, loc='upper right')

ax.set_title("Match Victory Margin Distribution: The Thrill of Close Finishes", fontsize=15, fontweight='bold', color='#ffffff', pad=15)
ax.set_xlabel("Final Score Difference (Points)", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.set_ylabel("Number of Matches", fontsize=11, color=TEXT_COLOR, labelpad=8)
ax.tick_params(colors=TEXT_COLOR, which='both')
ax.grid(True, axis='y', linestyle=':', alpha=0.15, color='#ffffff')

plt.tight_layout()
p4 = os.path.join(OUTPUT_DIR, "04_clutch_margins_distribution.png")
fig.savefig(p4, facecolor=DARK_BG, bbox_inches='tight')
plt.close()
print(f"Generated {p4}")

# -------------------------------------------------------------
# 5. End-to-End Analytics Workflow Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 5.5), facecolor=DARK_BG)
ax.set_facecolor(DARK_BG)
ax.axis('off')

# Stages definition
stages = [
    {"title": "1. Raw Data Ingestion", "desc": "Curated source CSVs\n• matches.csv (684 rows)\n• teams.csv (1.3k rows)\n• players.csv (16.8k rows)\n• events.csv (66.5k rows)", "color": "#1f6feb"},
    {"title": "2. Data Cleaning", "desc": "01_cleaning.ipynb\n• Purged 383 duplicates\n• Typed bool columns\n• Role imputation (391 pros)\n• Standardized names", "color": "#238636"},
    {"title": "3. Feature Pipeline", "desc": "Sports Engineering\n• Raid Strike Rate %\n• Points Per Raid (PPR)\n• Tackle Conversion %\n• Clutch Margin Flag (≤5 pts)", "color": "#d29922"},
    {"title": "4. Power BI Dashboard", "desc": "Interactive app.py\n• Real-time KPI Cards\n• Tactical Scatter Matrix\n• Custom CSV Drop-zone\n• Dynamic Chart Builder", "color": "#8957e5"}
]

box_width = 2.4
box_height = 3.2
y_start = 1.0

for i, stage in enumerate(stages):
    x = 0.5 + i * (box_width + 0.6)
    
    # Outer box
    rect = patches.FancyBboxPatch((x, y_start), box_width, box_height,
                                  boxstyle="round,pad=0.15,rounding_size=0.1",
                                  facecolor=CARD_BG, edgecolor=stage["color"], linewidth=2.0)
    ax.add_patch(rect)
    
    # Header bar
    header_rect = patches.FancyBboxPatch((x, y_start + box_height - 0.7), box_width, 0.7,
                                         boxstyle="round,pad=0.1,rounding_size=0.08",
                                         facecolor=stage["color"], edgecolor=stage["color"], linewidth=1.0)
    ax.add_patch(header_rect)
    
    # Header Text
    ax.text(x + box_width/2, y_start + box_height - 0.35, stage["title"],
            ha='center', va='center', color='#ffffff', fontsize=10.5, fontweight='bold')
    
    # Body Text
    ax.text(x + 0.15, y_start + box_height - 1.1, stage["desc"],
            ha='left', va='top', color=TEXT_COLOR, fontsize=8.5, lineheight=1.5)
    
    # Arrow to next
    if i < len(stages) - 1:
        arrow_start = x + box_width + 0.08
        arrow_end = arrow_start + 0.44
        arrow_y = y_start + box_height / 2
        ax.annotate("", xy=(arrow_end, arrow_y), xytext=(arrow_start, arrow_y),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_CYAN, lw=2.5, mutation_scale=18))

ax.set_xlim(0, 12.5)
ax.set_ylim(0.5, 5.2)
ax.text(6.25, 4.8, "🤼 Kabaddi Matches EDA: End-to-End Architectural Pipeline",
        ha='center', va='center', color='#ffffff', fontsize=15, fontweight='bold')

plt.tight_layout()
p5 = os.path.join(OUTPUT_DIR, "05_project_workflow_pipeline.png")
fig.savefig(p5, facecolor=DARK_BG, bbox_inches='tight')
plt.close()
print(f"Generated {p5}")

print("\nAll 5 visual graphics successfully generated!")
