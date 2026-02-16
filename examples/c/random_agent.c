/**
 * Simple random Hex agent - C example.
 * 
 * SIMPLIFIED VERSION - Just one function!
 * 
 * Your agent receives ONE line:
 *   <SIZE> <YOUR_COLOR> <MOVES>
 *   Example: 11 RED 5:5:B,6:6:R
 * 
 * Your agent outputs ONE line:
 *   <ROW> <COL>
 *   Example: 7 7
 * 
 * That's it! No need to track state, handle errors, or manage game flow.
 *
 * Compile: gcc -o random_agent random_agent.c
 * Run: ./random_agent
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_SIZE 20
#define MAX_LINE 10000

/**
 * Structure to represent a cell position
 */
typedef struct {
    int row;
    int col;
} Cell;

/**
 * Parse the board state from input line.
 * 
 * Returns: board size
 * Sets: myColor (must be a buffer of at least 10 chars)
 *       board (2D array where board[row][col] = 'R', 'B', or ' ')
 */
int parseBoard(const char* line, char* myColor, char board[MAX_SIZE][MAX_SIZE]) {
    int size;
    char moves[MAX_LINE];
    
    // Initialize board to empty
    for (int i = 0; i < MAX_SIZE; i++) {
        for (int j = 0; j < MAX_SIZE; j++) {
            board[i][j] = ' ';
        }
    }
    
    // Parse: SIZE COLOR MOVES
    int parsed = sscanf(line, "%d %s %[^\n]", &size, myColor, moves);
    
    // If there are moves, parse them
    if (parsed >= 3 && strlen(moves) > 0) {
        char* move = strtok(moves, ",");
        while (move != NULL) {
            int row, col;
            char color;
            
            // Parse format: row:col:color
            if (sscanf(move, "%d:%d:%c", &row, &col, &color) == 3) {
                if (row >= 0 && row < size && col >= 0 && col < size) {
                    board[row][col] = color;
                }
            }
            
            move = strtok(NULL, ",");
        }
    }
    
    return size;
}

/**
 * Get all empty cells on the board.
 * 
 * Returns: number of empty cells
 * Sets: emptyCells array with all empty positions
 */
int getEmptyCells(int size, char board[MAX_SIZE][MAX_SIZE], Cell* emptyCells) {
    int count = 0;
    
    for (int row = 0; row < size; row++) {
        for (int col = 0; col < size; col++) {
            if (board[row][col] == ' ') {
                emptyCells[count].row = row;
                emptyCells[count].col = col;
                count++;
            }
        }
    }
    
    return count;
}

/**
 * Choose your move. This is where your AI logic goes!
 */
Cell chooseMove(int size, const char* myColor, char board[MAX_SIZE][MAX_SIZE]) {
    Cell emptyCells[MAX_SIZE * MAX_SIZE];
    int numEmpty = getEmptyCells(size, board, emptyCells);
    
    Cell move = {0, 0};
    
    if (numEmpty > 0) {
        // Pick a random empty cell
        int index = rand() % numEmpty;
        move = emptyCells[index];
    }
    
    return move;
}

/**
 * Main function - this is all you need!
 */
int main() {
    char line[MAX_LINE];
    char myColor[10];
    char board[MAX_SIZE][MAX_SIZE];
    
    // Seed random number generator
    srand(time(NULL));
    
    // Loop version - handles multiple moves
    while (1) {
        // Read the board state (one line per turn)
        if (fgets(line, sizeof(line), stdin) == NULL) {
            // Game ended - controller closed our stdin
            break;
        }
        
        // Parse it
        int size = parseBoard(line, myColor, board);
        
        if (size <= 0 || size > MAX_SIZE) {
            fprintf(stderr, "Invalid board size: %d\n", size);
            return 1;
        }
        
        // Choose your move
        Cell move = chooseMove(size, myColor, board);
        
        // Output your move (don't forget to flush!)
        printf("%d %d\n", move.row, move.col);
        fflush(stdout);
    }
    
    return 0;
}
