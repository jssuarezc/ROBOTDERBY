import os
import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from maze import Maze
from participants import RacerX, RacerQ, RacerG

class GameState:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH")
        self.svm = joblib.load(model_path) if model_path else None
        self.tick_count = 0
        self.new_game()

    def new_game(self):
        self.maze = Maze()

        old_q = {a.name: a.q_table for a in self.agents 
                 if hasattr(a, 'q_table')} if hasattr(self, 'agents') else {}

        self.agents = [
            RacerQ(self.maze),
            RacerG(self.maze),
            RacerX(self.maze),
        ]

        for agent in self.agents:
            if hasattr(agent, 'q_table') and agent.name in old_q:
                agent.q_table = old_q[agent.name]

    def step_all(self):
        for agent in self.agents:
            agent.step()
        self.tick_count += 1
        if self.tick_count % 100 == 0:
            self._adjust_difficulty()
        return all(a.done for a in self.agents)
        
    def to_dict(self):
        return {
            "maze": self.maze.to_dict(),
            "agents": [a.to_dict() for a in self.agents],
            "done": all(a.done for a in self.agents),
        }
    
    def _adjust_difficulty(self):
        if self.svm is None:
            return
        for agent in self.agents:
            if agent.done:
                continue
            features = np.array([agent.get_features()])
            state_label = self.svm.predict(features)[0]
            agent.last_state = {0: "efficient", 1: "stuck", 2: "exploring"}[state_label]

            if hasattr(agent, 'epsilon'):
                if state_label == 1:
                    agent.epsilon = min(agent.epsilon + 0.15, 0.9)
                elif state_label == 2:
                    agent.epsilon = max(agent.epsilon - 0.05, 0.1)
    
game = GameState()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.get("/maze")
def get_maze():
    return game.to_dict()

@app.post("/step")
def step():
    game.step_all()
    return game.to_dict()

@app.post("/reset")
def reset():
    game.new_game()
    return game.to_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
