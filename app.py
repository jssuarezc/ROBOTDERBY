from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from maze import Maze
from participants import RacerX, RacerQ, RacerG

class GameState:
    def __init__(self):
        self.new_game()

    def new_game(self):
        self.maze = Maze()
        self.agents = [
            RacerQ(self.maze),
            RacerG(self.maze),
            RacerX(self.maze),
        ]

    def step_all(self):
        for agent in self.agents:
            agent.step()
        return all(a.done for a in self.agents)
    
    def to_dict(self):
        return {
            "maze": self.maze.to_dict(),
            "agents": [a.to_dict() for a in self.agents],
            "done": all(a.done for a in self.agents),
        }
    
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
