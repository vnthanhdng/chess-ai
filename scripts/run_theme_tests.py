"""
Run Minimax, AlphaBeta, and Expectimax agents on puzzles by theme and output results.

Tests: mateIn1, mateIn2, mateIn3, oneMove, short, long, fork, pin, skewer
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.puzzles import PuzzleLoader, PuzzleEvaluator
from src.agents import MinimaxAgent, AlphaBetaAgent, ExpectimaxAgent
from src.evaluation import evaluate

# Themes to test
THEMES = [
    "mateIn1",
    "mateIn2", 
    "mateIn3",
    "oneMove",
    "short",
    "long",
    "fork",
    "pin",
    "skewer",
]

PUZZLES_PER_THEME = 20
DEPTH = 3
OUTPUT_FILE = "results/theme_results.txt"


def run_theme_tests():
    # Create output directory
    output_path = project_root / OUTPUT_FILE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Open output file
    with open(output_path, 'w') as f:
        # Header
        f.write("=" * 70 + "\n")
        f.write("PUZZLE EVALUATION BY THEME\n")
        f.write("Agents: Minimax, AlphaBeta, Expectimax\n")
        f.write("=" * 70 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Puzzles per theme: {PUZZLES_PER_THEME}\n")
        f.write(f"Search depth: {DEPTH}\n")
        f.write("=" * 70 + "\n\n")
        
        # Also print to console
        print("=" * 70)
        print("PUZZLE EVALUATION BY THEME")
        print("Agents: Minimax, AlphaBeta, Expectimax")
        print("=" * 70)
        
        # Load puzzle file
        loader = PuzzleLoader(str(project_root / "data" / "puzzles.csv"))
        evaluator = PuzzleEvaluator(verbose=False)
        
        # Create agents
        agents = [
            MinimaxAgent(evaluate, depth=DEPTH, name=f"Minimax-d{DEPTH}"),
            AlphaBetaAgent(evaluate, depth=DEPTH, name=f"AlphaBeta-d{DEPTH}"),
            ExpectimaxAgent(evaluate, depth=DEPTH, name=f"Expectimax-d{DEPTH}"),
        ]
        
        # Results summary - dict of agent -> list of results
        all_results = {agent.name: [] for agent in agents}
        
        # Test each theme
        for theme in THEMES:
            print(f"\nTesting theme: {theme}...")
            f.write(f"\n{'='*70}\n")
            f.write(f"THEME: {theme}\n")
            f.write(f"{'='*70}\n")
            
            # Load puzzles for this theme
            puzzles = loader.load(
                themes=[theme],
                limit=PUZZLES_PER_THEME
            )
            
            if len(puzzles) == 0:
                msg = f"  No puzzles found for theme '{theme}'"
                print(msg)
                f.write(msg + "\n")
                for agent in agents:
                    all_results[agent.name].append({
                        'theme': theme,
                        'solved': 0,
                        'total': 0,
                        'rate': 0,
                        'avg_time': 0,
                        'avg_nodes': 0,
                    })
                continue
            
            if len(puzzles) < PUZZLES_PER_THEME:
                msg = f"  Only {len(puzzles)} puzzles found (requested {PUZZLES_PER_THEME})"
                print(msg)
                f.write(msg + "\n")
            
            # Run evaluation for all agents
            reports = evaluator.compare_agents(agents, puzzles)
            
            # Write results for each agent
            f.write(f"\n{'Agent':<20} {'Solved':<12} {'Rate':<10} {'Avg Time':<12} {'Avg Nodes':<12}\n")
            f.write("-" * 65 + "\n")
            
            for agent in agents:
                report = reports[agent.name]
                
                # Store results
                result = {
                    'theme': theme,
                    'solved': report.solved,
                    'total': report.total_puzzles,
                    'rate': report.solve_rate,
                    'avg_time': report.avg_time,
                    'avg_nodes': report.avg_nodes,
                }
                all_results[agent.name].append(result)
                
                # Write results
                f.write(f"{agent.name:<20} {report.solved}/{report.total_puzzles:<8} {report.solve_rate:>6.1f}%    {report.avg_time:>8.3f}s    {report.avg_nodes:>10,}\n")
                print(f"  {agent.name}: {report.solved}/{report.total_puzzles} ({report.solve_rate:.1f}%) - {report.avg_time:.3f}s")
        
        # Summary table for each agent
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("SUMMARY BY AGENT\n")
        f.write("=" * 70 + "\n")
        
        print("\n" + "=" * 70)
        print("SUMMARY BY AGENT")
        print("=" * 70)
        
        for agent in agents:
            f.write(f"\n{agent.name}\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Theme':<15} {'Solved':<12} {'Rate':<10} {'Avg Time':<12}\n")
            f.write("-" * 50 + "\n")
            
            print(f"\n{agent.name}")
            print("-" * 50)
            print(f"{'Theme':<15} {'Solved':<12} {'Rate':<10} {'Avg Time':<12}")
            print("-" * 50)
            
            total_solved = 0
            total_puzzles = 0
            
            for r in all_results[agent.name]:
                line = f"{r['theme']:<15} {r['solved']}/{r['total']:<8} {r['rate']:>6.1f}%    {r['avg_time']:>8.3f}s"
                f.write(line + "\n")
                print(line)
                total_solved += r['solved']
                total_puzzles += r['total']
            
            # Overall for this agent
            overall_rate = (total_solved / total_puzzles * 100) if total_puzzles > 0 else 0
            f.write("-" * 50 + "\n")
            f.write(f"{'OVERALL':<15} {total_solved}/{total_puzzles:<8} {overall_rate:>6.1f}%\n")
            print("-" * 50)
            print(f"{'OVERALL':<15} {total_solved}/{total_puzzles:<8} {overall_rate:>6.1f}%")
        
        # Overall comparison
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("OVERALL COMPARISON\n")
        f.write("=" * 70 + "\n")
        f.write(f"\n{'Agent':<20} {'Total Solved':<15} {'Overall Rate':<15}\n")
        f.write("-" * 50 + "\n")
        
        print("\n" + "=" * 70)
        print("OVERALL COMPARISON")
        print("=" * 70)
        print(f"{'Agent':<20} {'Total Solved':<15} {'Overall Rate':<15}")
        print("-" * 50)
        
        for agent in agents:
            total_solved = sum(r['solved'] for r in all_results[agent.name])
            total_puzzles = sum(r['total'] for r in all_results[agent.name])
            overall_rate = (total_solved / total_puzzles * 100) if total_puzzles > 0 else 0
            
            line = f"{agent.name:<20} {total_solved}/{total_puzzles:<12} {overall_rate:>6.1f}%"
            f.write(line + "\n")
            print(line)
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("EVALUATION COMPLETE\n")
        f.write("=" * 70 + "\n")
    
    print(f"\n✓ Results saved to: {output_path}")


if __name__ == "__main__":
    run_theme_tests()
