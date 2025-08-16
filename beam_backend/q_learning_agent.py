

import numpy as np
import random

class QLearningAgent:
    """
    The Q-Learning agent, now simplified for a 2D environment.
    """
    def __init__(self, env, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        # --- The Q-Table ---
        # The Q-table is now much smaller and simpler!
        # It's a 2D table mapping (state, action) to a Q-value.
        # Shape is (num_azimuth_steps, num_azimuth_actions).
        state_size = self.env.action_space_size
        action_size = self.env.action_space_size
        self.q_table = np.zeros((state_size, action_size))

    def choose_action(self, state):
        """Decides whether to explore or exploit."""
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random angle index.
            return random.randint(0, self.env.action_space_size - 1)
        else:
            # Exploitation: choose the best known action for this state.
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        """The Q-Learning formula, unchanged but with simpler indexing."""
        old_value = self.q_table[state, action]
        next_max = np.max(self.q_table[next_state])
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
        self.q_table[state, action] = new_value

    def train(self, episodes=1000):
        """Runs the main training loop."""
        for i in range(episodes):
            state = self.env.reset()
            # Since our episodes are only one step, we can simplify the loop.
            action = self.choose_action(state)
            next_state, reward, done = self.env.step(action)
            self.update_q_table(state, action, reward, next_state)

            if (i + 1) % 100 == 0:
                print(f"Episode {i + 1}/{episodes} completed.")

        # After training, find the best action from the entire Q-table.
        # Since state == action, the best state-action pair is on the diagonal.
        # But an easier way is to find the best reward possible.
        best_action_idx = np.argmax(np.max(self.q_table, axis=0))
        best_azimuth = self.env.azimuth_angles[best_action_idx]
        best_capacity = self.env._calculate_channel_capacity(best_action_idx)

        # Return the best azimuth, with a placeholder for elevation.
        return [(best_azimuth, 0.0)], [("N/A", "N/A")], best_capacity
