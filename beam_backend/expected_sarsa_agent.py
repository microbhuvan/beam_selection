import numpy as np
import random

class MultiLinkExpectedSarsaAgent:
    """
    An Expected SARSA agent designed to optimize multiple interfering links simultaneously.
    Uses the expected value of the next action instead of the maximum value.
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

    def get_expected_value(self, state):
        """
        Calculate the expected value of the next state using epsilon-greedy policy.
        """
        q_values = self.q_table[state]
        max_q = np.max(q_values)
        
        # Calculate expected value considering epsilon-greedy policy
        num_actions = len(q_values)
        greedy_prob = 1 - self.epsilon + self.epsilon / num_actions
        random_prob = self.epsilon / num_actions
        
        expected_value = greedy_prob * max_q + random_prob * np.sum(q_values)
        return expected_value

    def update_q_table(self, state, action, reward, next_state):
        """Expected SARSA update formula."""
        old_value = self.q_table[state, action]
        expected_next_value = self.get_expected_value(next_state)
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * expected_next_value)
        self.q_table[state, action] = new_value

    def train(self, episodes=2000):
        """Runs the main training loop using Expected SARSA."""
        for i in range(episodes):
            state = self.env.reset()
            action = self.choose_action(state)
            next_state, reward, done = self.env.step(action)
            
            # Expected SARSA update
            self.update_q_table(state, action, reward, next_state)

            if (i + 1) % 200 == 0:
                print(f"Expected SARSA Episode {i + 1}/{episodes} completed.")

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
