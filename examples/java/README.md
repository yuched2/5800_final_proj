# CS 5800 Hex Game - MVP Submission

**Group Members:**
* **Abdullah Tariq**
* **Chendong Yu**

## Overview
This is our Minimum Viable Product (MVP) submission for the Hex Game Final Project.
Our current agent (`MvpAgent.java`) is a fully playable version that utilizes a 
Time-Bounded Flat Monte Carlo Search algorithm to evaluate and select optimal moves.

## How to Run Our Program

Since our agent is written in Java, you need to compile it first and then run it through the course's Python framework.

**1. Compile the Agent:**
```bash
javac examples/java/MvpAgent.java
```

**2. Basic Command Structure:**

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