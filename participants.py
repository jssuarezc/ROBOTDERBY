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
        self._episode_reward = 0
        self.last_state = "exploring"
        self._visited = set()
        self.done = False

    def choose_actions(self):

        raise NotImplementedError
    
    def step(self):

        if self.done:
            return 0
        
        dr, dc = self.choose_action()
        new_pos = [self.position[0] + dr, self.position[1] + dc]

        if not self.maze.is_wall(*new_pos):
            self.position = new_pos

        self.steps += 1
        reward = self._reward()

        self._episode_reward += reward
        self._visited.add(tuple(self.position))

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

    def get_features(self):
        gr, gc = self.maze.goal
        pr, pc = self.position
        dist = abs(pr - gr) + abs(pc - gc)
        return [
            self.steps,
            self._episode_reward,
            len(self._visited),
            dist,
        ]

    def to_dict(self):

        return {
            "name": self.name,
            "color": self.color,
            "position": self.position,
            "steps": self.steps,
            "wins": self.wins,
            "done": self.done,
            "last_state": self.last_state,
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
    
    def choose_action(self):

        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        idx = np.argmax(self.q_table[self._state()])
        return self.ACTIONS[idx]

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
        self._episode_reward = 0
        self._visited = set()
        super().reset()

class RacerG(Participants):

    def __init__(self, maze):
        super().__init__(maze, name="Randy", color="#D85A30")
        self.visited = set()

    def choose_action(self):

        gr, gc = self.maze.goal
        self.visited.add(tuple(self.position))
        best_action = None
        best_dist = float("inf")

        for dr,dc in self.ACTIONS:
            nr = self.position[0] + dr
            nc = self.position[1] + dc
            if not self.maze.is_wall(nr, nc) and (nr, nc) not in self.visited:
                dist = abs(nr - gr) + abs(nc - gc)
                if dist < best_dist:
                    best_dist = dist
                    best_action = (dr, dc)

        return best_action or random.choice(self.ACTIONS)
    
    def reset(self):
        super().reset()
        self.visited.clear()
    
class RacerX(Participants):

    def __init__(self, maze, epsilon=0.7):
        super().__init__(maze, name="John", color="#1D9E75")
        self.epsilon = epsilon
        self.lr = 0.1
        self.gamma = 0.9
        num_states = maze.height * maze.width
        self.q_table = np.zeros((num_states,4))

    def _state(self):
        return self.position[0] * self.maze.width + self.position[1]
    
    def choose_action(self):

        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        idx = np.argmax(self.q_table[self._state()])
        return self.ACTIONS[idx]

    def step(self):

        if self.done:
            return 0
        
        state = self._state()
        action = self.choose_action()
        dr, dc = action
        new_pos = [self.position[0] + dr, self.position[1] + dc]

        if not self.maze.is_wall(*new_pos):
            self.position = new_pos

        self.steps += 1
        reward = self._reward()
        next_state = self._state()

        best_next = np.max(self.q_table[next_state])
        action_idx = self.ACTIONS.index(action)
        self.q_table[state][action_idx] += self.lr * (
            reward + self.gamma * best_next - self.q_table[state][action_idx]
        )

        if self.position == list(self.maze.goal):
            self.done = True
            self.wins +=1

        return reward
    
   
if __name__ == "__main__":
    from maze import Maze

    m = Maze()
    agents = [RacerQ(m), RacerG(m), RacerX(m)]
    EPISODES   = 50
    STEPS_EACH = 2000
 
    for ep in range(EPISODES):
        for agent in agents:
            if not agent.done:
                for _ in range(STEPS_EACH):
                    agent.step()
                    if agent.done:
                        break
 
    print("Results after", EPISODES, "episodes:")
    for agent in agents:
        status = f"finished  — {agent.steps} total steps, {agent.wins} wins" if agent.wins else "did not finish"
        print(f"  {agent.name:20} {status}")
 
    sample = agents[0].to_dict()
    for key in ["name", "color", "position", "steps", "wins", "done"]:
        assert key in sample, f"Missing key: {key}"
    print("to_dict keys verified")