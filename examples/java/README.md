# CS 5800 Hex Game - MVP Submission

**Group Members:**
* **Abdullah Tariq**
* **Chendong Yu**

## Overview
This is our Minimum Viable Product (MVP) submission for the Hex Game Final Project.
Our current agent (`MvpAgent.java`) is a fully playable version that utilizes a 
Time-Bounded Flat Monte Carlo Search algorithm to evaluate and select optimal moves.

## 1. How to Run Our Program

Since our agent is written in Java, you need to compile it first and then run it through the course's Python framework.

**Step 1. Compile the Agent:**
```bash
javac examples/java/MvpAgent.java
```

**Step 2. Basic Command Structure:**

```bash
python3 gui_main.py --red-subprocess "COMMAND" --blue-subprocess "COMMAND" [other flags]
```

- Replace `"COMMAND"` with your agent's execution command (e.g., `"python3 my_agent.py"`)
- Use `--red-subprocess` to make RED player a subprocess agent
- Use `--blue-subprocess` to make BLUE player a subprocess agent
- If a subprocess flag is not provided, that player will be **human** (interact with the GUI by clicking)
- Add other flags like `--board-size`, `--timeout`, `--memory-limit` as needed (see details below)

**Command-Line Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--board-size N` | Set board size (3-26) | 11 |
| `--timeout SECONDS` | Time limit per move (overrides auto-selection) | Auto (based on board size) |
| `--memory-limit MB` | Memory limit in MB | 64 |
| `--red-subprocess "CMD"` | Command to run RED agent | Human (GUI) |
| `--blue-subprocess "CMD"` | Command to run BLUE agent | Human (GUI) |
| `--red-name "NAME"` | Display name for RED | "Red Player" |
| `--blue-name "NAME"` | Display name for BLUE | "Blue Player" |

## 2. What Features Currently Work and What is still Incomplete (Next Steps)
**2.1 What features currently work**
- Protocol Communication: Parses the engine's standard input and flushes the standard output within time limits.

- Game Logic & Win Detection: Implemented an asymmetric Depth-First Search (DFS) that verifies RED's top-to-bottom connectivity.

- Flat Monte Carlo Rollouts: Implemented the agent that plays numerous random simulated games to determine the highest win-rate move.

- Zero-GC Optimization: Structured the rollout engine to pre-allocate all memory arrays and avoid the new keyword during simulations,
ensuring adherence to the 64MB memory limit.

- Swap Rule: Implemented the swap rule available when playing as BLUE if RED's opening move falls within the designated central zone.

**2.2 What is still incomplete**
- Heuristic Evaluation: Basic heuristics are to be implemented to further boost the decision-making process of the simulations.
- Greedy Intuition: A combination of heuristics+greedy approaches are to be implemented to address the inefficiency
when the agent's moves are close to the edge.