import numpy as np

class MultiBeamEnvironment2D:
    """
    A 2D environment that simulates multiple transmitter/receiver links
    that can interfere with each other.
    """
    def __init__(self, links, num_steps=20):
        """
        The constructor for our multi-link 2D world.

        Args:
            links (list): A list of dictionaries, where each dict contains
                          'tx_pos' and 'rx_pos' tuples.
            num_steps (int): The number of discrete steps for the azimuth angle.
        """
        # --- State and Action Space ---
        self.num_azimuth_steps = num_steps
        self.azimuth_angles = np.linspace(0, 360, self.num_azimuth_steps, endpoint=False)
        self.num_links = len(links)

        # The state/action space size is the number of possible angle combinations
        self.state_space_size = self.num_azimuth_steps ** self.num_links
        self.action_space_size = self.num_azimuth_steps ** self.num_links

        # --- Physical Setup ---
        self.links = []
        for link in links:
            self.links.append({
                'tx_pos': np.array(link['tx_pos']),
                'rx_pos': np.array(link['rx_pos'])
            })

        # The state is a single integer representing the tuple of all beam angles
        self.state = np.random.randint(self.state_space_size)

    def _to_state_index(self, angle_indices):
        """Converts a tuple of angle indices (e.g., (a1, a2)) to a single integer."""
        index = 0
        for i, angle_idx in enumerate(angle_indices):
            index += angle_idx * (self.num_azimuth_steps ** i)
        return int(index)

    def _to_angle_indices(self, state_index):
        """Converts a single state index back to a tuple of angle indices."""
        indices = []
        for i in range(self.num_links):
            index = state_index % self.num_azimuth_steps
            indices.append(int(index))
            state_index //= self.num_azimuth_steps
        return tuple(indices)

    def reset(self):
        """Resets the environment to a random starting state (combination of angles)."""
        self.state = np.random.randint(self.state_space_size)
        return self.state

    def step(self, action):
        """
        The agent gives us a joint action (an index representing a tuple of angles).
        We calculate the total network capacity as the reward.
        """
        # The new state is the action that was taken.
        self.state = action
        action_indices = self._to_angle_indices(action)
        reward = self._calculate_network_capacity(action_indices)
        done = True # Episodes are single-step in this model
        return self.state, reward, done

    def _get_beam_alignment(self, tx_pos, rx_pos, tx_angle_deg):
        """
        Calculates the alignment of a beam from a TX to an RX.
        Returns a value between 0 and 1 (1 is perfect alignment).
        """
        tx_direction = np.array([
            np.cos(np.deg2rad(tx_angle_deg)),
            np.sin(np.deg2rad(tx_angle_deg))
        ])

        # The "perfect" direction vector from the transmitter to the receiver.
        ideal_direction = rx_pos - tx_pos
        # Handle case where TX and RX are at the same position
        if np.linalg.norm(ideal_direction) == 0:
            return 1.0
        ideal_direction = ideal_direction / np.linalg.norm(ideal_direction)

        # Dot product measures alignment. 1 is perfect, -1 is opposite.
        alignment = np.dot(tx_direction, ideal_direction)
        return max(0, alignment)

    def _calculate_network_capacity(self, action_indices):
        """
        Calculates the total capacity of the network for a given set of beam angles.
        This is the core of the reward function.
        """
        capacities, _ = self.get_individual_capacities(action_indices)
        return sum(capacities)

    def get_individual_capacities(self, action_indices):
        """
        Calculates the individual capacity of each link, considering interference.
        This is useful for breaking down the final results.
        """
        individual_capacities = []
        total_capacity = 0
        noise = 0.1  # Base noise floor to prevent division by zero

        for i in range(self.num_links):
            # --- Calculate Signal for link i ---
            link_i = self.links[i]
            tx_i_angle = self.azimuth_angles[action_indices[i]]
            signal_alignment = self._get_beam_alignment(link_i['tx_pos'], link_i['rx_pos'], tx_i_angle)
            # Power is proportional to alignment squared (or a higher power)
            signal_power = 10 * (signal_alignment ** 10)

            # --- Calculate Interference on link i from all other links ---
            interference_power = 0
            for j in range(self.num_links):
                if i == j:
                    continue # A link doesn't interfere with itself

                # How much power from TX_j is hitting RX_i?
                link_j = self.links[j]
                tx_j_angle = self.azimuth_angles[action_indices[j]]
                interference_alignment = self._get_beam_alignment(link_j['tx_pos'], link_i['rx_pos'], tx_j_angle)
                interference_power += 10 * (interference_alignment ** 10)

            # --- Calculate SINR and Capacity for link i ---
            sinr = signal_power / (interference_power + noise)
            # Shannon-Hartley theorem (simplified)
            capacity = np.log2(1 + sinr)
            individual_capacities.append(capacity)
            total_capacity += capacity

        return individual_capacities, total_capacity
