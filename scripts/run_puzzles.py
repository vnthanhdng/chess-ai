"""
Evaluate chess AI agents on Lichess puzzles.

This script tests Minimax, Alpha-Beta, and Expectimax agents on a set of 
chess puzzles to measure their tactical strength, search efficiency, and 
performance across different difficulty levels.

Usage:
    python scripts/evaluate_puzzles.py
    python scripts/evaluate_puzzles.py --depth 4 --num-puzzles 200
    python scripts/evaluate_puzzles.py --rating-min 1400 --rating-max 1800
    python scripts/evaluate_puzzles.py --theme mateIn2 --depth 3
"""

import argparse
import sys
from pathlib import Path
import chess

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.puzzles import PuzzleLoader, PuzzleEvaluator
from src.agents import MinimaxAgent, AlphaBetaAgent, ExpectimaxAgent, QLearningAgent, ValueIterationAgent
from src.evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate chess agents on Lichess puzzles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate all agents on 100 medium difficulty puzzles at depth 3
  python scripts/run_puzzles.py
  
  # Test with deeper search
  python scripts/run_puzzles.py --depth 4 --num-puzzles 50
  
  # Focus on mate-in-2 puzzles
  python scripts/run_puzzles.py --theme mateIn2 --depth 3
  
  # Test on harder puzzles
  python scripts/run_puzzles.py --rating-min 1600 --rating-max 2000
        """
    )
    
    # Puzzle selection arguments
    parser.add_argument(
        "--puzzle-file",
        default="data/puzzles.csv",
        help="Path to puzzle CSV file (default: data/puzzles.csv)"
    )
    parser.add_argument(
        "--num-puzzles",
        type=int,
        default=100,
        help="Number of puzzles to evaluate (default: 100)"
    )
    parser.add_argument(
        "--rating-min",
        type=int,
        default=1200,
        help="Minimum puzzle rating (default: 1200)"
    )
    parser.add_argument(
        "--rating-max",
        type=int,
        default=1800,
        help="Maximum puzzle rating (default: 1800)"
    )
    parser.add_argument(
        "--theme",
        type=str,
        help="Filter by theme (e.g., 'mateIn2', 'fork', 'pin')"
    )
    
    # Agent configuration
    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        choices=[2, 3, 4, 5],
        help="Search depth for agents (default: 3)"
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=["minimax", "alphabeta", "expectimax", "qlearning", "valueiteration", "random", "all"],
        default=["alphabeta", "expectimax"],
        help="Agents to evaluate (default: alphabeta expectimax)"
    )

    # Output options
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed progress during evaluation"
    )
    parser.add_argument(
        "--show-failures",
        action="store_true",
        help="Print detailed info for failed puzzles"
    )
    parser.add_argument(
        "--by-rating",
        action="store_true",
        help="Break down results by rating ranges"
    )
    
    args = parser.parse_args()
    
    # Load puzzles from csv w puzzle loader from Van
    print("\n" + "=" * 70)
    print("CHESS PUZZLE EVALUATION")
    print("=" * 70)
    print(f"Puzzle file: {args.puzzle_file}")
    print(f"Puzzle count: {args.num_puzzles}")
    print(f"Rating range: {args.rating_min} - {args.rating_max}")
    if args.theme:
        print(f"Theme filter: {args.theme}")
    print(f"Search depth: {args.depth}")
    print("=" * 70)
    
    try:
        loader = PuzzleLoader(args.puzzle_file)
    except FileNotFoundError:
        print(f"\nERROR: Puzzle file not found: {args.puzzle_file}")
        print("\nPlease download the Lichess puzzle database and save it to:")
        print(f"  {args.puzzle_file}")
        print("\nDownload from: https://database.lichess.org/#puzzles")
        sys.exit(1)
    
    # Load puzzles with filters
    print(f"\nLoading {args.num_puzzles} puzzles...")
    themes = [args.theme] if args.theme else None
    puzzles = loader.load(
        min_rating=args.rating_min,
        max_rating=args.rating_max,
        themes=themes,
        limit=args.num_puzzles
    )
    
    if not puzzles:
        print("\nERROR: No puzzles found matching criteria!")
        print("Try adjusting --rating-min, --rating-max, or --theme")
        sys.exit(1)
    
    print(f"✓ Loaded {len(puzzles)} puzzles")
    
    # Show sample puzzle info
    sample = puzzles[0]
    print(f"\nSample puzzle: {sample.puzzle_id}")
    print(f"  Rating: {sample.rating}")
    print(f"  Themes: {', '.join(sample.themes[:5])}")
    print(f"  Moves: {' '.join(sample.moves)}")
    
    # Load in the agents
    agent_types = args.agents
    if "all" in agent_types:
        agent_types = ["minimax", "alphabeta", "expectimax", "qlearning", "valueiteration", "random"]
    
    agents = []
    for agent_type in agent_types:
        if agent_type == "minimax":
            agents.append(MinimaxAgent(
                evaluate, 
                depth=args.depth, 
                name=f"Minimax-d{args.depth}",
            ))
        elif agent_type == "alphabeta":
            agents.append(AlphaBetaAgent(
                evaluate,
                depth=args.depth,
                name=f"AlphaBeta-d{args.depth}",
            ))
        elif agent_type == "expectimax":
            agents.append(ExpectimaxAgent(
                evaluate,
                depth=args.depth,
                name=f"Expectimax-d{args.depth}"
            ))
        elif agent_type == "qlearning":
            agents.append(QLearningAgent(
                name="QLearning",
                color=chess.BLACK
            ))
        elif agent_type == "valueiteration":
            agents.append(ValueIterationAgent(
                discount=0.9,
                iterations=3,
                name="ValueIteration",
                color=chess.BLACK
            ))
        
    print(f"\nAgents to test: {', '.join(a.name for a in agents)}")
    

    # evaluate w puzzle evaluator from Van
    evaluator = PuzzleEvaluator(verbose=args.verbose)
    reports = evaluator.compare_agents(agents, puzzles, depth=args.depth)
    

    # Some analysis for the report 
    # Show failed puzzles if requested
    if args.show_failures:
        for agent_name, report in reports.items():
            failed = [r for r in report.results if not r.solved]
            if failed:
                print(f"\n{'=' * 70}")
                print(f"FAILED PUZZLES: {agent_name}")
                print('=' * 70)
                for result in failed[:10]:  # Show first 10 failures
                    print(f"\nPuzzle {result.puzzle.puzzle_id} (Rating: {result.puzzle.rating})")
                    print(f"  Themes: {', '.join(result.puzzle.themes)}")
                    print(f"  FEN: {result.puzzle.fen}")
                    print(f"  Correct move: {result.correct_move}")
                    print(f"  Agent chose: {result.agent_move}")
                    print(f"  Time: {result.time_taken:.3f}s | Nodes: {result.nodes_searched:,}")
    
    # Break down by rating ranges if requested
    if args.by_rating:
        rating_ranges = [
            (args.rating_min, args.rating_min + 200),
            (args.rating_min + 200, args.rating_min + 400),
            (args.rating_min + 400, args.rating_max)
        ]
        
        print("\n" + "=" * 70)
        print("PERFORMANCE BY RATING RANGE")
        print("=" * 70)
        
        for agent_name, report in reports.items():
            print(f"\n{agent_name}:")
            for min_r, max_r in rating_ranges:
                subset = report.by_rating_range(min_r, max_r)
                if subset.total_puzzles > 0:
                    print(f"  {min_r}-{max_r}: "
                          f"{subset.solved}/{subset.total_puzzles} solved "
                          f"({subset.solve_rate:.1f}%)")
    
  
    # Summary

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)
    
    # Find best performer
    best_agent = max(reports.items(), key=lambda x: x[1].solve_rate)
    print(f"\n✓ Best solver: {best_agent[0]} ({best_agent[1].solve_rate:.1f}%)")
    
    # Find fastest agent
    fastest_agent = min(reports.items(), key=lambda x: x[1].avg_time)
    print(f"✓ Fastest: {fastest_agent[0]} ({fastest_agent[1].avg_time:.3f}s avg)")
    
    # Find most efficient (nodes)
    efficient_agent = min(reports.items(), key=lambda x: x[1].avg_nodes)
    print(f"✓ Most efficient: {efficient_agent[0]} ({efficient_agent[1].avg_nodes:,.0f} nodes avg)")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
