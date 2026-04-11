import java.util.*;

/**
 * Hex Game Agent utilizing a time-bounded Flat Monte Carlo simulation engine.
 * Optimized with 1D array representations and lightweight DFS for zero-GC rollouts.
 */
public class MyAgentAttemptThree {

    /**
     * Parse the board state from input line.
     * Return Object array: [size(int), myColor(String), board(Map)]
     */
    private static final int EMPTY = 0;
    private static final int RED = 1;
    private static final int BLUE = 2;
    private static final int[][] DIRECTIONS = {
        {-1, 1}, {1, -1}, {0, 1}, {1, 0}, {0, -1}, {-1, 0}
    };
    private static final Random RAND = new Random();

    /**
     * Parses the standard input stream to reconstruct the 2D board state.
     * * @param line Raw input string from the game engine.
     * @return Object array containing: [size(int), myColor(int), board(int[][]), pieceCount(int)]
     */
    private static Object[] parseBoard(String line) {
        String[] parts = line.split(" ", 3);

        int size = Integer.parseInt(parts[0]);
        int myColor = parts[1].equals("RED") ? RED : BLUE;

        int [][]board = new int[size][size];
        int pieceCount = 0;

        // Parse existing moves
        if (parts.length == 3 && !parts[2].isEmpty()) {
            String[] movesStr = parts[2].split(",");
            for (String move : movesStr) {
                String[] moveParts = move.split(":");
                int r = Integer.parseInt(moveParts[0]);
                int c = Integer.parseInt(moveParts[1]);
                board[r][c] = moveParts[2].equals("R") ? RED : BLUE;
                pieceCount++;
            }
        }

        return new Object[] { size, myColor, board, pieceCount };
    }

    /**
     * Evaluates terminal state via Depth-First Search using a Zero-GC version.
     */
    private static boolean checkWin(int size, int[][] board, boolean[][] visited) {
        // Reset visited array
        for (int i = 0; i < size; i++) {
            Arrays.fill(visited[i], false);
        }
        // Check if Red wins
        for (int c = 0; c < size; c++) {
            if (board[0][c] == RED && !visited[0][c]) {
                if (dfs(0, c, RED, size, board, visited)) return true;
            }
        }
        return false;
    }

    private static boolean dfs(int r, int c, int color, int size, int[][] board, boolean[][] visited) {
        if (r == size - 1) return true;
        visited[r][c] = true;
        for (int[] d : DIRECTIONS) {
            int nr = r + d[0], nc = c + d[1];
            if (nr >= 0 && nr < size && nc >= 0 && nc < size && board[nr][nc] == color && !visited[nr][nc]) {
                if (dfs(nr, nc, color, size, board, visited)) return true;
            }
        }
        return false;
    }

    /**
     * Executes a fast random rollout from the given board state.
     * Utilizes an in-place Fisher-Yates shuffle to minimize memory allocation.
     */
    private static boolean simulateRandomGame(int size, int[][] tempBoard, int currentTurn, int[] emptySpots, boolean[][] visited) {
        int emptyCount = 0;

        for (int r = 0; r < size; r++) {
            for (int c = 0; c < size; c++) {
                if (tempBoard[r][c] == EMPTY) {
                    emptySpots[emptyCount++] = r * size + c;
                }
            }
        }

        // In-place Fisher-Yates shuffle
        for (int i = emptyCount - 1; i > 0; i--) {
            int j = RAND.nextInt(i + 1);
            int temp = emptySpots[i];
            emptySpots[i] = emptySpots[j];
            emptySpots[j] = temp;
        }

        int turn = currentTurn;
        for (int i = 0; i < emptyCount; i++) {
            int spot = emptySpots[i];
            tempBoard[spot / size][spot % size] = turn;
            turn = (turn == RED) ? BLUE : RED;
        }
        return checkWin(size, tempBoard, visited);
    }

    /**
     * Determines the optimal move using a time-bounded Flat Monte Carlo search.
     */
    private static int[] chooseMove(int size, int myColor, int[][] board, int pieceCount) {
        // Center opening for RED
        if (myColor == RED && pieceCount == 0) {
            return new int[] { size / 2, size / 2 };
        }
        int[] emptySpots = new int[size * size];
        int emptyCount = 0;
        for (int r = 0; r < size; r++) {
            for (int c = 0; c < size; c++) {
                if (board[r][c] == EMPTY) {
                    emptySpots[emptyCount++] = r * size + c;
                }
            }
        }

        long startTime = System.currentTimeMillis();
        long timeLimit = 900;
        if(size <= 11) {
            timeLimit = 135;
        } else if(size <= 15) {
            timeLimit = 185;
        } else if(size <= 19) {
            timeLimit = 230;
        } else if(size <= 21) {
            timeLimit = 280;
        }

        int[] wins = new int[emptyCount];
        int[] visits = new int[emptyCount];

        int[][] tempBoard = new int[size][size];
        int[] rolloutEmptySpots = new int[size * size];
        boolean[][] visited = new boolean[size][size];

        while (System.currentTimeMillis() - startTime < timeLimit) {
            for (int i = 0; i < emptyCount; i++) {
                int spot = emptySpots[i];
                int r = spot / size;
                int c = spot % size;

                board[r][c] = myColor;
                int nextTurn = (myColor == RED) ? BLUE : RED;

                for (int row = 0; row < size; row++) {
                    System.arraycopy(board[row], 0, tempBoard[row], 0, size);
                }

                boolean redWon = simulateRandomGame(size, tempBoard, nextTurn, rolloutEmptySpots, visited);

                if ((myColor == RED && redWon) || (myColor == BLUE && !redWon)) {
                    wins[i]++;
                }
                visits[i]++;

                board[r][c] = EMPTY;
            }
        }

        int bestSpot = emptySpots[0];
        double bestRate = -1;
        for (int i = 0; i < emptyCount; i++) {
            if (visits[i] == 0) continue;
            double rate = (double) wins[i] / visits[i];
            if (rate > bestRate) {
                bestRate = rate;
                bestSpot = emptySpots[i];
            }
        }

        return new int[] { bestSpot / size, bestSpot % size };
    }

    /**
     * Implemented Swap logic: Swap if RED's first move is near the center.
     */
    private static boolean shouldSwap(int size, int[][] board) {
        int redRow = -1, redCol = -1;

        // Locate RED's first and only move
        for (int r = 0; r < size; r++) {
            for (int c = 0; c < size; c++) {
                if (board[r][c] == RED) {
                    redRow = r;
                    redCol = c;
                    break;
                }
            }
        }
        if (redRow == -1) return false;

        int center = size / 2;
        int threshold = size / 4;

        // Return true if RED played within the center threshold zone
        return Math.abs(redRow - center) <= threshold && Math.abs(redCol - center) <= threshold;
    }

    /**
     * Entry point for the agent process.
     * Manages standard I/O communication with the game platform.
     */
    public static void main(String[] args) {
        try {
            // Use BufferedReader for better subprocess compatibility
            java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.InputStreamReader(System.in));

            // Loop version - handles multiple moves
            String line;
            while ((line = reader.readLine()) != null) {
                Object[] parsed = parseBoard(line);
                int size = (int) parsed[0];
                int myColor = (int) parsed[1];
                int[][] board = (int[][]) parsed[2];
                int pieceCount = (int) parsed[3];

                // Update swap rule
                if (myColor == BLUE && pieceCount == 1) {
                    if (shouldSwap(size, board)) {
                        System.out.println("swap");
                        System.out.flush();
                        continue;
                    } else {
                        System.err.println("Error found");
                    }
                }

                // Choose the move
                int[] move = chooseMove(size, myColor, board, pieceCount);

                // Output the move
                System.out.println(move[0] + " " + move[1]);
                System.out.flush();
            }

            reader.close();

        } catch (Exception e) {
            System.err.println("[ERROR] Exception occurred: " + e.getMessage());
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }
}
