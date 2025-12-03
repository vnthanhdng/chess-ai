import matplotlib.pyplot as plt
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import chess
from src.agents import QLearningAgent, ValueIterationAgent
from src.evaluation import evaluate


def plot_qlearning_curves():
    """Plot Q-Learning training curves"""
    print("Training Q-Learning agent...")
    
    # Train with more episodes for better curves
    agent = QLearningAgent(
        numTraining=500,  # More training episodes
        epsilon=0.3,
        alpha=0.5,
        gamma=0.9,
        color=chess.BLACK,
        name="Q-Learning"
    )
    
    history = agent.get_training_history()
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Q-Learning Training Progress', fontsize=16, fontweight='bold')
    
    # Plot 1: Win Rate
    axes[0, 0].plot(history['episode'], history['win_rate'], 'b-', linewidth=2)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Win Rate (last 10 games)')
    axes[0, 0].set_title('Win Rate Over Time')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axhline(y=0.5, color='r', linestyle='--', label='Random baseline')
    axes[0, 0].legend()
    
    # Plot 2: Q-Value Table Size
    axes[0, 1].plot(history['episode'], history['q_value_size'], 'g-', linewidth=2)
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Number of State-Action Pairs')
    axes[0, 1].set_title('Q-Table Growth')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Average Game Length
    axes[1, 0].plot(history['episode'], history['avg_game_length'], 'r-', linewidth=2)
    axes[1, 0].set_xlabel('Episode')
    axes[1, 0].set_ylabel('Moves per Game')
    axes[1, 0].set_title('Game Length (Learning to Play Longer?)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Total Episode Reward
    axes[1, 1].plot(history['episode'], history['total_reward'], 'm-', linewidth=2)
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Total Reward')
    axes[1, 1].set_title('Cumulative Reward per Episode')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_path = project_root / 'results' / 'qlearning_curves.png'
    output_path.parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved learning curves to: {output_path}")
    
    plt.show()


def plot_value_iteration_convergence():
    """Plot Value Iteration state space growth"""
    print("\nTraining Value Iteration agent...")
    
    iteration_counts = [1, 2, 3, 5, 10]
    state_counts = []
    
    for iters in iteration_counts:
        agent = ValueIterationAgent(
            discount=0.9,
            iterations=iters,
            color=chess.BLACK,
            name=f"VI-{iters}"
        )
        state_counts.append(len(agent.states))
        print(f"  {iters} iterations: {len(agent.states)} states")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(iteration_counts, state_counts, 'bo-', linewidth=2, markersize=8)
    plt.xlabel('Number of Iterations', fontsize=12)
    plt.ylabel('Number of States in Value Table', fontsize=12)
    plt.title('Value Iteration: State Space Growth', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Annotate points
    for x, y in zip(iteration_counts, state_counts):
        plt.annotate(f'{y}', (x, y), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=10)
    
    plt.tight_layout()
    
    output_path = project_root / 'results' / 'value_iteration_states.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved Value Iteration plot to: {output_path}")
    
    plt.show()


def compare_agents_over_training():
    """Compare multiple training runs"""
    print("\nComparing different training configurations...")
    
    configs = [
        {'numTraining': 100, 'epsilon': 0.5, 'label': 'ε=0.5, 100 episodes'},
        {'numTraining': 100, 'epsilon': 0.3, 'label': 'ε=0.3, 100 episodes'},
        {'numTraining': 500, 'epsilon': 0.3, 'label': 'ε=0.3, 500 episodes'},
    ]
    
    plt.figure(figsize=(12, 6))
    
    for config in configs:
        agent = QLearningAgent(
            numTraining=config['numTraining'],
            epsilon=config['epsilon'],
            alpha=0.5,
            gamma=0.9,
            color=chess.BLACK
        )
        
        history = agent.get_training_history()
        plt.plot(history['episode'], history['win_rate'], 
                linewidth=2, label=config['label'], marker='o', markersize=4)
    
    plt.xlabel('Episode', fontsize=12)
    plt.ylabel('Win Rate (last 10 games)', fontsize=12)
    plt.title('Q-Learning: Effect of Hyperparameters', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Random baseline')
    
    plt.tight_layout()
    
    output_path = project_root / 'results' / 'qlearning_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved comparison plot to: {output_path}")
    
    plt.show()


def main():
    print("="*70)
    print("GENERATING LEARNING CURVES")
    print("="*70)
    
    # Create results directory
    results_dir = project_root / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Generate plots
    plot_qlearning_curves()
    plot_value_iteration_convergence()
    compare_agents_over_training()
    
    print("\n" + "="*70)
    print("COMPLETE! Check the 'results/' folder for plots")
    print("="*70)


if __name__ == "__main__":
    main()