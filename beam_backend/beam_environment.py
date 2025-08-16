# c:\Users\Mallikarjuna\Desktop\beam_selection - Copy\practice\beam_backend\beam_environment.py

import numpy as np

class BeamEnvironment2D:
    """
    A 2D version of the environment
    """
    def __init__(self, tx_pos, rx_pos, num_steps=20):
        """
        The constructor for our 2D world.

        Args:
            tx_pos (tuple): The 2D coordinates (x, y) of the transmitter.
            rx_pos (tuple): The 2D coordinates (x, y) of the receiver.
            num_steps (int): The number of discrete steps for the azimuth angle.
        """
        # --- State and Action Space ---
        # We only have one dimension of action now: the horizontal angle.
        self.num_steps = num_steps
        #linspace(start, stop, num, endpoint=true)
        #so here it prints sequence of values and until stop if true stop is included 
        #nums is how much points to be printed
        self.azimuth_angles = np.linspace(0, 360, num_steps)
        self.action_space_size = num_steps  # A single number, not a tuple!

        #Physical Setup
        #converting the values and positions into array values
        self.tx_pos = np.array(tx_pos)
        self.rx_pos = np.array(rx_pos)

        #Initial State
        # The state is just the current azimuth angle index.
        #generating a random number for initial state
        self.state = np.random.randint(num_steps)

    def reset(self):
        """Resets the environment to a random starting angle."""
        self.state = np.random.randint(self.num_steps)
        return self.state

    def step(self, action):
        """
        The agent gives us an action (an azimuth index).
        We calculate the reward for that action.
        """
        # The new state is simply the action that was taken.
        self.state = action
        reward = self._calculate_channel_capacity(action)
        done = True
        return self.state, reward, done

    def _calculate_channel_capacity(self, action_idx):
        """
        The 2D physics simulation.
        """
        tx_az = self.azimuth_angles[action_idx]

        # Convert angle to a 2D direction vector (x, y).
        tx_direction = np.array([
            np.cos(np.deg2rad(tx_az)),
            np.sin(np.deg2rad(tx_az))
        ])

        # The "perfect" direction vector from transmitter to receiver.
        ideal_direction = self.rx_pos - self.tx_pos
        ideal_direction = ideal_direction / np.linalg.norm(ideal_direction)

        # Dot product measures alignment. 1 is perfect, -1 is opposite.
        alignment = np.dot(tx_direction, ideal_direction)

        # Reward function: exaggerates the peak for good alignment.
        channel_capacity = 10 * (max(0, alignment) ** 10)
        return channel_capacity
