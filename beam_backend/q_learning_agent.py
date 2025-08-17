

import numpy as np
import random

class MultiLinkQLearningAgent:
    """
    A Q-Learning agent designed to optimize multiple interfering links simultaneously.
    """
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # The Q-table maps a joint state to a joint action.
        # State: An integer representing the tuple of all transmitter angles.
        # Action: An integer representing the next tuple of all transmitter angles.
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

    def update_q_table(self, state, action, reward, next_state):
        """The Q-Learning formula, updated for the joint state-action space."""
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

    def train(self, episodes=2000):
        """Runs the main training loop."""
        for i in range(episodes):
            state = self.env.reset()
            # In our model, an "episode" is just one step: choosing a set of angles
            # and getting the reward.
            action = self.choose_action(state)
            next_state, reward, done = self.env.step(action)
            self.update_q_table(state, action, reward, next_state)

            if (i + 1) % 200 == 0:
                print(f"Episode {i + 1}/{episodes} completed.")

        # After training, find the best action from the entire Q-table.
        # This is the action (a combination of angles) that leads to the highest Q-value.
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
