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

                          links = [
                            {"tx_pos": (0, 0), "rx_pos": (1, 0)},
                            {"tx_pos": (0, 0), "rx_pos": (0, 1)}
                        ]

            num_steps (int): The number of discrete steps for the azimuth angle.
            the 360 degrees gets sliced into num_steps equal parts
        """
        # --- State and Action Space ---
        self.num_azimuth_steps = num_steps
        # linspace(start, stop, num of angles, stop value not included) returns an nd array
        self.azimuth_angles = np.linspace(0, 360, self.num_azimuth_steps, endpoint=False)
        self.num_links = len(links)

        # The state/action space size is the number of possible angle combinations
        self.state_space_size = self.num_azimuth_steps ** self.num_links
        self.action_space_size = self.num_azimuth_steps ** self.num_links
        """so we are telling hey the steps are 20 and we have 2 links so we have 20^2 possible states
         with may be first = 0 and second = 0 or first 180 and second 0 and 
        we only care about tx angles and not rx angles (0,0) or (180,0) like this we
        will have 20^2 states"""

        # --- Physical Setup ---
        self.links = []
        for link in links:
            self.links.append({
                'tx_pos': np.array(link['tx_pos']),
                'rx_pos': np.array(link['rx_pos'])
            })

            #this is converted to array to allow easy vector math calculation
            """[
                {'tx_pos': array([0,0]), 'rx_pos': array([1,0])},
                {'tx_pos': array([0,0]), 'rx_pos': array([0,1])}
            ]"""

        # The state is a single integer representing the tuple of all beam angles
        # stroring a random angle(tuple) at starting
        self.state = np.random.randint(self.state_space_size)

    def _to_state_index(self, angle_indices):
        """Converts a tuple of angle indices (e.g., (a1, a2)) to a single integer."""
        index = 0
        for i, angle_idx in enumerate(angle_indices):
            index += angle_idx * (self.num_azimuth_steps ** i)
            #for (180,0)
            #0 = 180 * (20 ^ 0) + 0 * (20 ^ 1)
        return int(index)

    def _to_angle_indices(self, state_index):
        """Converts a single state index back to a tuple of angle indices."""
        indices = []
        for i in range(self.num_links):
            index = state_index % self.num_azimuth_steps
            #reminder will be one angle
            indices.append(int(index))
            state_index //= self.num_azimuth_steps
            #base means / by 20 will be another angle
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
        self.state = action #an integer angle is picked
        action_indices = self._to_angle_indices(action) #converted back to tuple
        reward = self._calculate_network_capacity(action_indices) #check for reward
        done = True # Episodes are single-step in this model
        return self.state, reward, done

    def _get_beam_alignment(self, tx_pos, rx_pos, tx_angle_deg):
        """
        Calculates the alignment of a beam from a TX to an RX.
        Returns a value (beam angle) between 0 and 1 (1 is perfect alignment).
        0 means perpendicular to rx
        """

        # convert angle to dir vector
        # convert deg to rad for cos and sin
        #(cos,sin) unit vector pointing in dir tita
        tx_direction = np.array([
            np.cos(np.deg2rad(tx_angle_deg)),
            np.sin(np.deg2rad(tx_angle_deg))
        ])

        # The "perfect" direction vector from the transmitter to the receiver.
        ideal_direction = rx_pos - tx_pos
        # Handle case where TX and RX are at the same position
        if np.linalg.norm(ideal_direction) == 0:
            return 1.0
        
        #normalizing  - converting arrow to unit vector
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
    










"""
TUPLE TO INT
example 1: num_steps = 4, 2 links

So base = 4.
Tuple (2, 3) means:
link 0 uses angle index 2
link 1 uses angle index 3

The formula:
index = 2 * (4^0) + 3 * (4^1)
      = 2*1 + 3*4
      = 2 + 12
      = 14

So (2,3) ↔ state index 14.

example 2: num_steps = 20, 2 links
Base = 20.
Suppose tuple = (5, 7):

index = 5 * (20^0) + 7 * (20^1)
      = 5*1 + 7*20
      = 5 + 140
      = 145

So (5,7) ↔ state index 145.

example 3: num_steps = 12, 3 links
Base = 12.
Tuple (2, 1, 4) means:

index = 2 * (12^0) + 1 * (12^1) + 4 * (12^2)
      = 2*1 + 1*12 + 4*144
      = 2 + 12 + 576
      = 590

So (2,1,4) ↔ state index 590.


INT TO TUPLE 
Say num_steps = 4 and num_links = 2.
So total states = 16.
decoding state_index = 14.

loop 1 (i=0):
index = 14 % 4 = 2 → link0 angle index = 2
indices = [2]
state_index = 14 // 4 = 3

loop 2 (i=1):
index = 3 % 4 = 3 → link1 angle index = 3
indices = [2,3]
state_index = 3 // 4 = 0

stop (2 links done).
Return (2,3) 

6. another example

num_steps = 20, num_links = 2, state_index = 145.

loop 1: 145 % 20 = 5 → link0 = 5
new state_index = 145 // 20 = 7

loop 2: 7 % 20 = 7 → link1 = 7
new state_index = 7 // 20 = 0

Result = (5,7)"""
