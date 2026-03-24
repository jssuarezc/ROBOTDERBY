import numpy as np
import random
import os
from dotenv import load_dotenv

load_dotenv()

class Maze:
    def __init__(self, width=None, height=None):
        self.width = width or int(os.getenv("MAZE_WIDTH"))
        self.height = height or int(os.getenv("MAZE_HEIGHT"))
        self.grid = np.ones((self.height, self.width), dtype=int)
        self.start = (1,1)
        self.goal = (self.height - 2, self.width - 2)
        self._generate()

    def _generate(self):
        stack = [self.start]
        visited = {self.start}
        self.grid[self.start[0]][self.start[1]] = 0

        while stack:
            row, col = stack[-1]

            neighbors = [
                (row - 2, col),
                (row + 2, col),
                (row, col - 2),
                (row, col + 2)
            ]
            random.shuffle(neighbors)

            moved = False
            for nr, nc in neighbors:
                if (0 < nr < self.height -1 and 
                    0 < nc < self.width - 1 and 
                    (nr, nc) not in visited):

                    self.grid[nr][nc] = 0
                    self.grid[(row + nr) // 2][(col + nc) // 2] = 0

                    visited.add((nr, nc))
                    stack.append((nr, nc))
                    moved = True
                    break
            if not moved:
                stack.pop()

    def is_wall(self, row, col):
        if row < 0 or col < 0 or row >= self.height or col >= self.width:
            return True
        return self.grid[row][col] == 1
    
    def get_valid_moves(self, row, col):
        candidates = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1)
        ]
        return [(r, c) for r, c in candidates if not self.is_wall(r, c)]
    
    def to_dict(self):
        return {
            "grid": self.grid.tolist(),
            "width": self.width,
            "height": self.height,
            "start": list(self.start),
            "goal": list(self.goal),
        }
    
    def reset(self):
        self.grid = np.ones((self.height, self.width), dtype=int)
        self._generate()

## Double checking if it produces different maze before moving with the next step:

if __name__ == "__main__":
    m = Maze()

    for row in m.grid:
        print("".join("█" if cell == 1 else "·" for cell in row))
    
    print()
    print(f"Start: {m.start} -> Goal: {m.goal}")
    print(f"Valid moves from start: {m.get_valid_moves(*m.start)}")

    assert m.grid[m.start[0]][m.start[1]] == 0, "Start should be open"
    assert m.grid[m.goal[0]][m.goal[1]]  == 0, "Goal should be open"
    assert len(m.get_valid_moves(*m.start)) > 0, "Start needs at least one exit"
    print("All checks passed")

    first_grid = m.grid.copy()
    m.reset()
    assert not np.array_equal(first_grid, m.grid), "Reset should give a new maze"
    print("Reset produces a different maze")
