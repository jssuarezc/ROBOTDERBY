import numpy as np
import os
from maze import Maze
from participants import RacerQ, RacerG, RacerX
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

EPISODES = 300
MAX_STEPS = 2000


def run_episode(agent_class, maze):

    agent = agent_class(maze)
    total_reward = 0
    visited = set()

    for _ in range(MAX_STEPS):
        visited.add(tuple(agent.position))
        reward = agent.step()
        total_reward += reward
        if agent.done:
            break

    gr, gc = maze.goal
    pr, pc = agent.position
    dist = abs(pr - gr) + abs(pc - gc)

    return np.array([
        agent.steps,
        total_reward,
        len(visited),
        dist,
    ], dtype=float)


def label_episode(features):

    steps, reward, unique, dist = features

    if dist == 0 and steps < 500:
        return 0
    if unique < 20 and dist > 10:
        return 1
    if unique > 80:
        return 2

    return 0 if dist < 5 else 1


def collect_data():
    X, y = [], []
    agent_classes = [RacerQ, RacerG, RacerX]

    for ep in range(EPISODES):
        maze  = Maze()
        for cls in agent_classes:
            features = run_episode(cls, maze)
            label = label_episode(features)
            X.append(features)
            y.append(label)

        if (ep + 1) % 50 == 0:
            print(f"Simulated {ep + 1}/{EPISODES} episodes")

    return np.array(X), np.array(y)

def train(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(kernel='rbf', C=1.0, gamma='scale'))
    ])

    model.fit(X_train, y_train)

    print("\n Training report")
    print(classification_report(
        y_train, model.predict(X_train),
        target_names=['efficient', 'stuck', 'exploring']
    ))

    print(" Test report")
    print(classification_report(
        y_test, model.predict(X_test),
        target_names=['efficient', 'stuck', 'exploring']
    ))

    return model

def save(model, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"\nModel saved to {path}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    model_path = os.getenv("MODEL_PATH")

    print("Simulating episodes")
    X, y = collect_data()

    print(f"\nDataset: {len(X)} samples")
    print(f"Class distribution:")
    for label, name in enumerate(['efficient', 'stuck', 'exploring']):
        count = (y == label).sum()
        print(f"  {name}: {count} ({count/len(y)*100:.1f}%)")

    model = train(X, y)
    save(model, model_path)
