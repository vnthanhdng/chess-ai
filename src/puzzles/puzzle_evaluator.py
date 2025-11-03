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
                
class PuzzleEvaluator:
    """
    Evaluates chess agents on puzzle sets.
    
    Example usage:
        >>> evaluator = PuzzleEvaluator()
        >>> puzzles = loader.load(min_rating=1200, max_rating=1600, limit=50)
        >>> report = evaluator.evaluate(agent, puzzles, depth=4)
        >>> report.print_summary()
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the evaluator.
        
        Args:
            verbose: If True, print progress during evaluation
        """
        self.verbose = verbose
    
    def evaluate(
        self,
        agent: BaseAgent,
        puzzles: List[Puzzle],
        depth: Optional[int] = None
    ) -> EvaluationReport:
        """
        Evaluate an agent on a set of puzzles.
        
        Args:
            agent: Agent to evaluate
            puzzles: List of puzzles to solve
            depth: Optional search depth override (for SearchAgent)
            
        Returns:
            EvaluationReport with results and statistics
        """
        results = []
        solved_count = 0
        
        if self.verbose:
            print(f"\nEvaluating {agent.name} on {len(puzzles)} puzzles...")
            print("-" * 70)
        
        original_depth = None
        if depth is not None and hasattr(agent, 'depth'):
            original_depth = agent.depth
            agent.depth = depth
        
        for i, puzzle in enumerate(puzzles, 1):
            if self.verbose and i % 10 == 0:
                print(f"Progress: {i}/{len(puzzles)} ({solved_count}/{i} solved, "
                      f"{(solved_count/i)*100:.1f}%)")
            
            result = self._evaluate_puzzle(agent, puzzle, depth or getattr(agent, 'depth', 0))
            results.append(result)
            
            if result.solved:
                solved_count += 1
        
        # Restore original depth
        if original_depth is not None:
            agent.depth = original_depth
        
        report = EvaluationReport(
            agent_name=agent.name,
            total_puzzles=len(puzzles),
            solved=solved_count,
            results=results,
            depth=depth or getattr(agent, 'depth', 0)
        )
        
        if self.verbose:
            report.print_summary()
        
        return report
    
    def _evaluate_puzzle(
        self,
        agent: BaseAgent,
        puzzle: Puzzle,
        depth: int
    ) -> PuzzleResult:
        """
        Evaluate an agent on a single puzzle.
        
        Args:
            agent: Agent to evaluate
            puzzle: Puzzle to solve
            depth: Search depth
            
        Returns:
            PuzzleResult for this puzzle
        """
        # Set up the board
        board = puzzle.board
        correct_move_uci = puzzle.first_solution_move
        
        # Reset agent stats for this puzzle
        nodes_before = agent.nodes_searched
        
        # Time the move selection
        start_time = time.time()
        try:
            move = agent.choose_move(board)
            time_taken = time.time() - start_time
        except Exception as e:
            if self.verbose:
                print(f"Error solving puzzle {puzzle.puzzle_id}: {e}")
            return PuzzleResult(
                puzzle=puzzle,
                solved=False,
                agent_move=None,
                correct_move=correct_move_uci,
                time_taken=0.0,
                depth=depth
            )
        
        # Get nodes searched for this puzzle
        nodes_searched = agent.nodes_searched - nodes_before
        
        # Check if the move is correct
        agent_move_uci = move.uci() if move else None
        solved = agent_move_uci == correct_move_uci
        
        # Get evaluation score if available
        eval_score = None
        if hasattr(agent, 'search') and hasattr(agent.search, 'evaluator'):
            try:
                board.push(move)
                eval_score = agent.search.evaluator(board)
                board.pop()
            except:
                pass
        
        return PuzzleResult(
            puzzle=puzzle,
            solved=solved,
            agent_move=agent_move_uci,
            correct_move=correct_move_uci,
            eval_score=eval_score,
            nodes_searched=nodes_searched,
            time_taken=time_taken,
            depth=depth
        )
    
    def compare_agents(
        self,
        agents: List[BaseAgent],
        puzzles: List[Puzzle],
        depth: Optional[int] = None
    ) -> Dict[str, EvaluationReport]:
        """
        Compare multiple agents on the same puzzle set.
        
        Args:
            agents: List of agents to compare
            puzzles: Puzzles to solve
            depth: Optional search depth override
            
        Returns:
            Dictionary mapping agent names to their reports
        """
        reports = {}
        
        for agent in agents:
            print(f"\n{'=' * 70}")
            print(f"Testing: {agent.name}")
            print('=' * 70)
            
            report = self.evaluate(agent, puzzles, depth)
            reports[agent.name] = report
        
        # Print comparison summary
        self._print_comparison(reports)
        
        return reports
    
    def _print_comparison(self, reports: Dict[str, EvaluationReport]):
        """Print a comparison table of multiple agents."""
        print("\n" + "=" * 70)
        print("COMPARISON SUMMARY")
        print("=" * 70)
        print(f"{'Agent':<25} {'Solved':<10} {'Rate':<10} {'Avg Time':<12} {'Avg Nodes':<12}")
        print("-" * 70)
        
        for name, report in reports.items():
            print(f"{name:<25} "
                  f"{report.solved}/{report.total_puzzles:<10} "
                  f"{report.solve_rate:.1f}%{'':<6} "
                  f"{report.avg_time:.3f}s{'':<6} "
                  f"{report.avg_nodes:,.0f}")
        
        print("=" * 70 + "\n")