"""Evaluate AI agents on chess puzzles."""
import time
import chess
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .puzzle import Puzzle
from ..agents import BaseAgent

@dataclass
class PuzzleResult:
    """
    Result of an agent attemping to solve a puzzle.
    
    Attributes:
        puzzle: the puzzle that was attempted
        solved: whether the agent found the correct first move
        agent_move: the move the agent selected (in UCI format)
        correct_move: the correct first move (in UCI format)
        eval_score: evaluation score returned by the agent's search
        nodes_searched: number of nodes searched by the agent
        time_taken: time taken by the agent to select the move (in seconds)
        depth: search depth used by the agent
    """
    puzzle = Puzzle
    solved: bool
    agent_move: Optional[str]
    correct_move: str
    eval_score: Optional[float]
    nodes_searched: int
    time_taken: float
    depth: Optional[int]
    
    def __str__(self) -> str:
        return (f"PuzzleResult(solved={self.solved}, agent_move={self.agent_move}, "
                f"correct_move={self.correct_move}, eval_score={self.eval_score}, "
                f"nodes_searched={self.nodes_searched}, time_taken={self.time_taken:.4f}s, "
                f"depth={self.depth})")

@dataclass
class EvaluationReport:
    """
    Summary report of puzzle evaluation.
    
    Attributes:
        agent_name: Name of the agent tested
        total_puzzles: Total number of puzzles evaluated
        solved: Number of puzzles solved correctly
        results: List of individual puzzle results
        avg_time: Average time taken per puzzle
        avg_nodes: Average nodes searched per puzzle
        solve_rate: Percentage of puzzles solved
        depth: Search depth used by the agent
    """
    agent_name: str
    total_puzzles: int
    solved: int
    results: List[PuzzleResult]
    avg_time: float
    avg_nodes: float
    solve_rate: float
    depth: Optional[int]
    
    def __post_init__(self):
        self.total_puzzles = len(self.results)
        self.solved = sum(1 for result in self.results if result.solved)
        self.avg_time = (sum(result.time_taken for result in self.results) / self.total_puzzles
                         if self.total_puzzles > 0 else 0.0)
        self.avg_nodes = (sum(result.nodes_searched for result in self.results) / self.total_puzzles
                          if self.total_puzzles > 0 else 0.0)
        self.solve_rate = (self.solved / self.total_puzzles * 100.0
                           if self.total_puzzles > 0 else 0.0)
        self.depth = (self.results[0].depth if self.results else None)
        
    def by_rating_range(self, min_rating: int, max_rating: int) -> 'EvaluationReport':
        """
        Filter results by puzzle rating range and return a new report.
        
        Args:
            min_rating: Minimum puzzle rating (inclusive)
            max_rating: Maximum puzzle rating (inclusive)
        
        Returns:
            New EvaluationReport with filtered results
        """
        filtered_results = [
            r for r in self.results
            if min_rating <= r.puzzle.rating <= max_rating
        ]
        return EvaluationReport(
            agent_name=self.agent_name,
            total_puzzles=len(filtered_results),
            solved=sum(1 for r in filtered_results if r.solved),
            results=filtered_results,
            depth=self.depth
        )
    
    def by_theme(self, theme: str) -> 'EvaluationReport':
        """
        Filter results by puzzle theme and return a new report.
        
        Args:
            theme: Theme to filter by
        """
        filtered_results = [
            r for r in self.results
            if theme in r.puzzle.themes
        ]
        return EvaluationReport(
            agent_name=self.agent_name,
            total_puzzles=len(filtered_results),
            solved=sum(1 for r in filtered_results if r.solved),
            results=filtered_results,
            depth=self.depth
        )
        
    def print_summary(self):
        """Print a formatted summary of the evaluation."""
        print("\n" + "=" * 70)
        print(f"PUZZLE EVALUATION REPORT: {self.agent_name}")
        print("=" * 70)
        print(f"Total Puzzles:    {self.total_puzzles}")
        print(f"Solved:           {self.solved} ({self.solve_rate:.1f}%)")
        print(f"Failed:           {self.total_puzzles - self.solved}")
        print(f"Search Depth:     {self.depth}")
        print(f"Avg Time/Puzzle:  {self.avg_time:.3f}s")
        print(f"Avg Nodes/Puzzle: {self.avg_nodes:,.0f}")
        print("=" * 70 + "\n")
    
    def print_detailed(self, show_failed_only: bool = False):
        """
        Print detailed results for each puzzle.
        
        Args:
            show_failed_only: If True, only show failed puzzles
        """
        print("\nDETAILED RESULTS:")
        print("-" * 70)
        
        for result in self.results:
            if show_failed_only and result.solved:
                continue
            
            print(f"\n{result}")
            print(f"  Rating: {result.puzzle.rating} | Themes: {', '.join(result.puzzle.themes[:5])}")
            print(f"  Time: {result.time_taken:.3f}s | Nodes: {result.nodes_searched:,}")
            
            if not result.solved:
                print(f"  FEN: {result.puzzle.fen}")
                
