"""
Extract a manageable subset of puzzles from the full Lichess database.

Supports:
- Stratified sampling by rating bracket
- Theme-based sampling
- Random sampling within criteria
"""

import csv
import random
from pathlib import Path
from collections import defaultdict

# Rating brackets for stratified sampling
RATING_BRACKETS = [
    (400, 1000, "Beginner"),
    (1000, 1400, "Intermediate"),
    (1400, 1800, "Advanced"),
    (1800, 2200, "Expert"),
    (2200, 3200, "Master"),
]

# All Lichess tactical themes
ALL_THEMES = [
    # Checkmate patterns
    "mate", "mateIn1", "mateIn2", "mateIn3", "mateIn4", "mateIn5",
    "anapiesis", "arabianMate", "backRankMate", "bodenMate",
    "doubleBishopMate", "dovetailMate", "hookMate", "schlechterMate", "smotheredMate",
    
    # Tactics
    "fork", "pin", "skewer", "discoveredAttack", "doubleCheck",
    "attraction", "clearance", "deflection", "interference", "intermezzo",
    "sacrifice", "xRayAttack", "zugzwang",
    
    # Piece situations
    "hangingPiece", "trappedPiece", "capturingDefender", "exposedKing",
    
    # Pawn tactics
    "advancedPawn", "promotion", "underPromotion",
    
    # Attack types
    "attackingF2F7", "kingsideAttack", "queensideAttack",
    
    # Game phases
    "opening", "middlegame", "endgame",
    
    # Endgame types
    "bishopEndgame", "knightEndgame", "pawnEndgame",
    "queenEndgame", "queenRookEndgame", "rookEndgame",
    
    # Puzzle characteristics
    "short", "long", "veryLong", "oneMove",
    "crushing", "advantage", "equality",
    "defensiveMove", "quietMove", "simplification",
    
    # Player level
    "master", "masterVsMaster", "superGM",
]

# Subset of key tactical themes for balanced sampling
KEY_THEMES = [
    "mateIn1", "mateIn2", "mateIn3",
    "fork", "pin", "skewer",
    "discoveredAttack", "doubleCheck",
    "hangingPiece", "trappedPiece",
    "sacrifice", "deflection", "attraction",
    "backRankMate", "smotheredMate",
    "promotion", "xRayAttack",
]


def create_puzzle_subset(
    input_file="data/lichess_db_puzzle.csv",
    output_file="data/puzzles.csv",
    num_puzzles=2000,
    rating_min=400,
    rating_max=3200,
    themes_filter=None,
    stratified=True,
    seed=42
):
    """Extract puzzles with good distribution across ratings and themes."""
    
    random.seed(seed)
    
    print(f"Reading puzzles from {input_file}...")
    
    # Organize puzzles by rating bracket
    puzzles_by_bracket = defaultdict(list)
    puzzles_by_theme = defaultdict(list)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            if i % 500000 == 0 and i > 0:
                print(f"  Processed {i:,} puzzles...")
            
            try:
                rating = int(row['Rating'])
                themes = row['Themes'].split() if row.get('Themes') else []
                
                if rating < rating_min or rating > rating_max:
                    continue
                
                if themes_filter and not any(t in themes for t in themes_filter):
                    continue
                
                for min_r, max_r, name in RATING_BRACKETS:
                    if min_r <= rating < max_r:
                        puzzles_by_bracket[name].append(row)
                        break
                
                for theme in themes:
                    if theme in KEY_THEMES:
                        puzzles_by_theme[theme].append(row)
                        
            except (ValueError, KeyError):
                continue
    
    # Sample puzzles
    if stratified:
        selected = sample_stratified(puzzles_by_bracket, puzzles_by_theme, num_puzzles)
    else:
        all_puzzles = []
        for puzzles in puzzles_by_bracket.values():
            all_puzzles.extend(puzzles)
        selected = random.sample(all_puzzles, min(num_puzzles, len(all_puzzles)))
    
    # Write to output file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if selected:
            writer = csv.DictWriter(f, fieldnames=selected[0].keys())
            writer.writeheader()
            writer.writerows(sorted(selected, key=lambda p: int(p['Rating'])))
    
    print(f"✓ Wrote {len(selected):,} puzzles to {output_file}")
    
    return selected


def sample_stratified(puzzles_by_bracket, puzzles_by_theme, total_puzzles):
    """Sample with equal distribution across ratings, ensuring theme coverage."""
    
    selected = {}
    
    # 60% from rating brackets
    rating_budget = int(total_puzzles * 0.6)
    per_bracket = rating_budget // len(RATING_BRACKETS)
    
    for min_r, max_r, name in RATING_BRACKETS:
        available = puzzles_by_bracket[name]
        sample_size = min(per_bracket, len(available))
        
        if sample_size > 0:
            sample = random.sample(available, sample_size)
            for p in sample:
                selected[p['PuzzleId']] = p
    
    # 40% from themes
    theme_budget = int(total_puzzles * 0.4)
    per_theme = theme_budget // len(KEY_THEMES)
    
    for theme in KEY_THEMES:
        available = [p for p in puzzles_by_theme[theme] if p['PuzzleId'] not in selected]
        sample_size = min(per_theme, len(available))
        
        if sample_size > 0:
            sample = random.sample(available, sample_size)
            for p in sample:
                selected[p['PuzzleId']] = p
    
    return list(selected.values())


if __name__ == "__main__":
    create_puzzle_subset(
        input_file="data/lichess_db_puzzle.csv",
        output_file="data/puzzles.csv",
        num_puzzles=2000,
        stratified=True,
        seed=42
    )