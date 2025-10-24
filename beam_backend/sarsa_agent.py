import numpy as np
import random

class MultiLinkSarsaAgent:
    """
    A SARSA agent designed to optimize multiple interfering links simultaneously.
    Uses on-policy learning where the agent learns the value of the action it actually takes.
    """
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # The Q-table maps a joint state to a joint action.
        state_size = self.env.state_space_size
        action_size = self.env.action_space_size
        self.q_table = np.zeros((state_size, action_size))

    def choose_action(self, state):
        """
        Chooses a joint action for all links using an epsilon-greedy strategy.
        """
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random combination of angles.
            return random.randint(0, self.env.action_space_size - 1)
        else:
            # Exploitation: choose the best known joint action for this joint state.
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state, next_action):
        """The SARSA update formula - uses the actual next action taken."""
        old_value = self.q_table[state, action]
        next_value = self.q_table[next_state, next_action]
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_value)
        self.q_table[state, action] = new_value

    def train(self, episodes=2000):
        """Runs the main training loop using SARSA (on-policy)."""
        for i in range(episodes):
            state = self.env.reset()
            action = self.choose_action(state)
            
            # SARSA: we need to choose the next action before updating
            next_state, reward, done = self.env.step(action)
            next_action = self.choose_action(next_state)
            
            # Update using the actual next action (SARSA)
            self.update_q_table(state, action, reward, next_state, next_action)

            if (i + 1) % 200 == 0:
                print(f"SARSA Episode {i + 1}/{episodes} completed.")

        # After training, find the best action from the entire Q-table.
        best_joint_action_idx = np.argmax(np.max(self.q_table, axis=0))
        
        # Convert the single best action index back to a tuple of angle indices
        best_angle_indices = self.env._to_angle_indices(best_joint_action_idx)
        
        # Get the detailed breakdown of capacities for this best action set
        individual_capacities, total_capacity = self.env.get_individual_capacities(best_angle_indices)

        # Format the results for the API response
        results = []
        for i in range(self.env.num_links):
            azimuth = self.env.azimuth_angles[best_angle_indices[i]]
            results.append({
                'capacity': individual_capacities[i],
                'tx_action': {'azimuth': azimuth, 'elevation': 'N/A'}
            })

        return results, total_capacity
