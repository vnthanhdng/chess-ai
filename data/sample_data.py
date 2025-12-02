"""
Extract a manageable subset of puzzles from the full Lichess database.
"""

import csv
import random
from pathlib import Path

def create_puzzle_subset(
    input_file="\\data\\lichess_db_puzzle.csv",
    output_file="sample.csv",
    num_puzzles=2000,
    rating_min=1200,
    rating_max=2000,
    themes_filter=None  # e.g., ['mateIn2', 'mateIn3', 'fork', 'pin']
):
    """Extract random subset of puzzles matching criteria."""
    
    print(f"Reading puzzles from {input_file}...")
    matching_puzzles = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            # Progress indicator for large file
            if i % 100000 == 0:
                print(f"  Processed {i:,} puzzles, found {len(matching_puzzles):,} matches...")
            
            try:
                rating = int(row['Rating'])
                themes = row['Themes'].split()
                
                # Apply filters
                if rating < rating_min or rating > rating_max:
                    continue
                
                if themes_filter and not any(t in themes for t in themes_filter):
                    continue
                
                matching_puzzles.append(row)
                
                # Stop early if we have enough candidates
                if len(matching_puzzles) >= num_puzzles * 3:
                    break
                    
            except (ValueError, KeyError):
                continue
    
    print(f"\nFound {len(matching_puzzles):,} matching puzzles")
    
    # Randomly sample
    if len(matching_puzzles) > num_puzzles:
        selected = random.sample(matching_puzzles, num_puzzles)
    else:
        selected = matching_puzzles
    
    # Write subset to new file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', newline='') as f:
        if selected:
            writer = csv.DictWriter(f, fieldnames=selected[0].keys())
            writer.writeheader()
            writer.writerows(selected)
    
    print(f"✓ Wrote {len(selected):,} puzzles to {output_file}")
    print(f"  Rating range: {rating_min}-{rating_max}")
    if themes_filter:
        print(f"  Themes: {', '.join(themes_filter)}")
    
    # Show distribution
    ratings = [int(p['Rating']) for p in selected]
    print(f"\nRating distribution:")
    print(f"  Min: {min(ratings)}, Max: {max(ratings)}, Avg: {sum(ratings)//len(ratings)}")

if __name__ == "__main__":
    # Create a diverse test set
    create_puzzle_subset(
        input_file="data/lichess_db_puzzle.csv",  # Download from database.lichess.org
        output_file="data/puzzles.csv",
        num_puzzles=2000,
        rating_min=1200,
        rating_max=2000
    )