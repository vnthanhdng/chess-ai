import matplotlib.pyplot as plt
from pathlib import Path
import sys
import chess

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.agent_utils import create_agent, play_game


def evaluate_agent_strength(agent, num_games=20):
    """Test agent against random opponent"""
    results = {'wins': 0, 'losses': 0, 'draws': 0}
    
    from src.agents import RandomAgent
    
    for _ in range(num_games):
        # Play as both colors
        if agent.color == chess.WHITE:
            opponent = RandomAgent(color=chess.BLACK)
            result = play_game(agent, opponent, timeout_seconds=60)
        else:
            opponent = RandomAgent(color=chess.WHITE)
            result = play_game(opponent, agent, timeout_seconds=60)
        
        if result == 'white':
            if agent.color == chess.WHITE:
                results['wins'] += 1
            else:
                results['losses'] += 1
        elif result == 'black':
            if agent.color == chess.BLACK:
                results['wins'] += 1
            else:
                results['losses'] += 1
        else:
            results['draws'] += 1
    
    win_rate = (results['wins'] + 0.5 * results['draws']) / num_games
    return win_rate


def track_qlearning_progress():
    """Track Q-Learning performance at different training levels"""
    training_levels = [0, 50, 100, 200, 500, 1000]
    win_rates = []
    
    print("Testing Q-Learning at different training levels...")
    
    for num_training in training_levels:
        print(f"\n  Training with {num_training} episodes...")
        agent = create_agent('qlearning', chess.BLACK, 
                            q_numTraining=num_training, q_epsilon=0.0)
        
        win_rate = evaluate_agent_strength(agent, num_games=20)
        win_rates.append(win_rate)
        print(f"    Win rate vs Random: {win_rate:.1%}")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(training_levels, win_rates, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Training Episodes', fontsize=12)
    plt.ylabel('Win Rate vs Random', fontsize=12)
    plt.title('Q-Learning Performance vs Training', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0.5, color='r', linestyle='--', label='Random baseline')
    plt.legend()
    
    # Annotate points
    for x, y in zip(training_levels, win_rates):
        plt.annotate(f'{y:.1%}', (x, y), textcoords="offset points",
                    xytext=(0,10), ha='center')
    
    plt.tight_layout()
    output_path = project_root / 'results' / 'qlearning_training_effect.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved to: {output_path}")
    plt.show()


if __name__ == "__main__":
    track_qlearning_progress()