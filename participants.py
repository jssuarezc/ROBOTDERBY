import numpy as np
import random

class Participants:
    ACTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, maze, name, color):
        self.maze = maze
        self.name = name
        self.color = color
        self.position = list(maze.start)
        self.steps = 0
        self.wins = 0
        self.done = False

    def chose_actions(self):

        raise NotImplementedError
    
    def step(self):

        if self.done:
            return 0
        
        dr, dc = self.choose_action()
        new_pos = [self.position(0) + dr, self.position[1] + dc]

        if not self.maze.is_wall(*new_pos):
            self.position = new_pos

        self.steps += 1
        reward = self._reward()

        if self.position == list(self.maze.goal):
            self.done = True
            self.wins += 1

        return reward
    
    def _reward(self):
        
        if self.position == list(self.maze.goal):
            return 100
        return -1
    
    def reset(self):

        self.position = list(self.maze.start)
        self.steps = 0
        self.done = False

    def to_dict(self):

        return {
            "name": self.name,
            "color": self.color,
            "position": self.position,
            "steps": self.steps,
            "wins": self.wins,
            "done": self.done,
        }
    
class RacerQ(Participants):

    def __init__(self, maze, lr=0.1, gamma=0.9, epsilon=0.2):
        super().__init__(maze, name="Kweebie", color="#7F77DD")
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon

        num_states = maze.height * maze.width
        self.q_table = np.zeros((num_states, 4))

    def _state(self):

        return self.position[0] * self.maze.width + self.position[1]
    
    def chose_action(self):

        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        idx = np.argmax(self.q_table[self._state()])
        return self.Actions[idx]

    def step(self):

        if self.done:
            return 0

        state  = self._state()
        action = self.choose_action()
        dr, dc = action
        new_pos = [self.position[0] + dr, self.position[1] + dc]

        if not self.maze.is_wall(*new_pos):
            self.position = new_pos

        self.steps += 1
        reward     = self._reward()
        next_state = self._state()

        best_next  = np.max(self.q_table[next_state])
        action_idx = self.ACTIONS.index(action)
        self.q_table[state][action_idx] += self.lr * (
            reward + self.gamma * best_next - self.q_table[state][action_idx]
        )

        if self.position == list(self.maze.goal):
            self.done = True
            self.wins += 1

        return reward

    def reset(self):
        super().reset()
