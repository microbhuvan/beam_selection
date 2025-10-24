import numpy as np
import random

class MultiLinkDoubleQLearningAgent:
    """
    A Double Q-Learning agent designed to optimize multiple interfering links simultaneously.
    Uses two Q-tables to reduce overestimation bias in Q-learning.
    """
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # Two Q-tables for Double Q-Learning
        state_size = self.env.state_space_size
        action_size = self.env.action_space_size
        self.q1 = np.zeros((state_size, action_size))
        self.q2 = np.zeros((state_size, action_size))

    def choose_action(self, state):
        """
        Chooses a joint action for all links using an epsilon-greedy strategy.
        Uses the sum of both Q-tables for action selection.
        """
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random combination of angles.
            return random.randint(0, self.env.action_space_size - 1)
        else:
            # Exploitation: choose the best known joint action using both Q-tables
            q_sum = self.q1[state] + self.q2[state]
            return np.argmax(q_sum)

    def update_q_table(self, state, action, reward, next_state):
        """Double Q-Learning update - randomly update one of the two Q-tables."""
        if random.random() < 0.5:
            # Update Q1 using Q2 to select the action
            best_action_q2 = np.argmax(self.q2[next_state])
            old_value = self.q1[state, action]
            new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * self.q2[next_state, best_action_q2])
            self.q1[state, action] = new_value
        else:
            # Update Q2 using Q1 to select the action
            best_action_q1 = np.argmax(self.q1[next_state])
            old_value = self.q2[state, action]
            new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * self.q1[next_state, best_action_q1])
            self.q2[state, action] = new_value

    def train(self, episodes=2000):
        """Runs the main training loop using Double Q-Learning."""
        for i in range(episodes):
            state = self.env.reset()
            action = self.choose_action(state)
            next_state, reward, done = self.env.step(action)
            
            # Double Q-Learning update
            self.update_q_table(state, action, reward, next_state)

            if (i + 1) % 200 == 0:
                print(f"Double Q-Learning Episode {i + 1}/{episodes} completed.")

        # After training, find the best action using the sum of both Q-tables
        q_sum = self.q1 + self.q2
        best_joint_action_idx = np.argmax(np.max(q_sum, axis=0))
        
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
