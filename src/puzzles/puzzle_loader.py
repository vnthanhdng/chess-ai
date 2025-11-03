import csv
from pathlib import Path
from typing import List, Callable, Optional
from .puzzle import Puzzle

class PuzzleLoader:
    """
    Loads and filters chess puzzles from lichess CSV database.
    
    Expected CSV format:
        PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl
        
    Example usage:
        loader = PuzzleLoader("puzzles.csv")
        puzzles = loader.load(
            min_rating=1200,
            max_rating=1800,
            themes=["mateIn2"],
            limit=10
            )
    """
    
    def __init__(self, csv_path: str):
        """Initialize the puzzle loader
        Args:
            csv_path: Path to the CSV file containing puzzles
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
    def load(
        self,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        themes: Optional[List[str]] = None,
        limit: Optional[int] = None,
        custom_filter: Optional[Callable[[Puzzle], bool]] = None
    ) -> List[Puzzle]:
        """Load and filter puzzles from the CSV file.
        
        Args:
            min_rating: Minimum puzzle rating to include
            max_rating: Maximum puzzle rating to include
            themes: List of themes that puzzles must include
            limit: Maximum number of puzzles to load
            custom_filter: Custom function to filter puzzles 
        
        Returns:
            List of Puzzle objects matching the filters
        """
        puzzles = []
        count = 0
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                if limit and count >= limit:
                    break
                puzzle = self._parse_row(row)
                
                if not self._passes_filters(puzzle, min_rating, max_rating, themes, custom_filter):
                    continue
                
                puzzles.append(puzzle)
                count += 1
                
        return puzzles
    
    def _parse_row(self, row: dict) -> Puzzle:
        """
        Parse a CSV row into a Puzzle object.
        
        Args:
            row: Dictionary representing a CSV row
        
        Returns:
            Puzzle object
        """
        return Puzzle(
            puzzle_id=row["PuzzleId"],
            fen=row["FEN"],
            moves=row["Moves"].split(" "),
            rating=int(row["Rating"]),
            rating_deviation=int(row["RatingDeviation"]),
            popularity=int(row["Popularity"]),
            nb_plays=int(row["NbPlays"]),
            themes=row["Themes"].split(" "),
            game_url=row["GameUrl"]
        )
        
    def _passes_filters(
        self,
        puzzle: Puzzle,
        min_rating: Optional[int],
        max_rating: Optional[int],
        themes: Optional[List[str]],
        custom_filter: Optional[Callable[[Puzzle], bool]]
    ) -> bool:
        """
        Check if a puzzle passes the given filters.
        
        Args:
            puzzle: Puzzle object to check
            min_rating: Minimum rating filter
            max_rating: Maximum rating filter
            themes: List of required themes
            custom_filter: Custom filter function
        
        Returns:
            True if the puzzle passes all filters, False otherwise
        """
        if min_rating and puzzle.rating < min_rating:
            return False
        if max_rating and puzzle.rating > max_rating:
            return False
        if themes:
            for theme in themes:
                if not puzzle.has_theme(theme):
                    return False
        if custom_filter and not custom_filter(puzzle):
            return False
        return True
    
    def get_stats(self) -> dict:
        """
        Get stats about the database.
        
        Returns:
            Dictionary with dtb stats
        """
        
        total_puzzles = 0
        rating_sum = 0
        rating_min = float('inf')
        rating_max = float('-inf')
        all_themes = set()
        
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                total_puzzles += 1
                rating = int(row["Rating"])
                rating_sum += rating
                rating_min = min(rating_min, rating)
                rating_max = max(rating_max, rating)
                
                themes = row["Themes"].split(",")
                all_themes.update(themes)
                
        return {
            "total_puzzles": total_puzzles,
            "average_rating": rating_sum / total_puzzles if total_puzzles > 0 else 0,
            "min_rating": rating_min if rating_min != float('inf') else 0,
            "max_rating": rating_max if rating_max != float('-inf') else 0,
            "unique_themes": list(all_themes)
        }
        
def load_sample_puzzles(csv_path: str, sample_size: int = 10) -> List[Puzzle]:
    """Load a small sample of puzzles for quick testing.
    
    Args:
        csv_path: Path to the CSV file containing puzzles
        sample_size: Number of puzzles to load
    
    Returns:
        List of Puzzle objects
    """
    loader = PuzzleLoader(csv_path)
    return loader.load(limit=sample_size) 