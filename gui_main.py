#!/usr/bin/env python3
"""
GUI runner for Hex game.

Launches the Hex game with a graphical tkinter interface.
"""

import sys
import argparse
from engine.game import GameController
from engine.constants import Color, GameStatus, DEFAULT_BOARD_SIZE, DEFAULT_TIMEOUT, DEFAULT_MEMORY_LIMIT, MIN_BOARD_SIZE, MAX_BOARD_SIZE
from players.gui_player import GUIPlayer
from players.subprocess_player import SubprocessPlayer
from view.tkinter_view import TkinterView


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Hex Game - GUI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gui_main.py                      # Default 11x11 board, human vs human
  python gui_main.py --board-size 7       # Smaller 7x7 board
  python gui_main.py --red-subprocess "python3 examples/python/random_agent.py"  # Human vs AI
  python gui_main.py --blue-subprocess "java Agent"  # Human vs Java AI
  python gui_main.py --red-subprocess "python3 agent1.py" --blue-subprocess "python3 agent2.py"  # AI vs AI
        """
    )

    parser.add_argument(
        '--board-size',
        type=int,
        default=DEFAULT_BOARD_SIZE,
        metavar='N',
        help=f'Board size (default: {DEFAULT_BOARD_SIZE})'
    )

    parser.add_argument(
        '--red-name',
        type=str,
        default='Red Player',
        metavar='NAME',
        help='Name for RED player (default: Red Player)'
    )

    parser.add_argument(
        '--blue-name',
        type=str,
        default='Blue Player',
        metavar='NAME',
        help='Name for BLUE player (default: Blue Player)'
    )

    parser.add_argument(
        '--red-subprocess',
        type=str,
        metavar='COMMAND',
        help='Make RED player a subprocess (e.g., "python3 agent.py" or "java Agent")'
    )

    parser.add_argument(
        '--blue-subprocess',
        type=str,
        metavar='COMMAND',
        help='Make BLUE player a subprocess (e.g., "python3 agent.py" or "java Agent")'
    )

    parser.add_argument(
        '--timeout',
        type=float,
        default=DEFAULT_TIMEOUT,
        metavar='SECONDS',
        help=f'Timeout for subprocess players (default: {DEFAULT_TIMEOUT})'
    )

    parser.add_argument(
        '--memory-limit',
        type=int,
        default=DEFAULT_MEMORY_LIMIT,
        metavar='MB',
        help=f'Memory limit for subprocess players in MB (default: {DEFAULT_MEMORY_LIMIT})'
    )

    return parser.parse_args()


def run_game(args, view=None, is_first_run=True):
    """Run a game with given arguments."""
    # If view is provided, we're replaying; otherwise create new view

    # Create game controller
    game = GameController(board_size=args.board_size)

    # Define stderr callback for subprocess players
    def stderr_callback(message: str):
        from engine.game import LogLevel
        game.log_event(LogLevel.INFO, message)

    # Create players based on arguments
    if args.red_subprocess:
        # Parse subprocess command
        parts = args.red_subprocess.split()
        program = parts[0]
        prog_args = parts[1:] if len(parts) > 1 else []
        red_player = SubprocessPlayer(
            color=Color.RED,
            program_path=program,
            args=prog_args,
            timeout=args.timeout,
            memory_limit_mb=args.memory_limit,
            name=args.red_name,
            stderr_callback=stderr_callback
        )
    else:
        red_player = GUIPlayer(Color.RED, args.red_name)

    if args.blue_subprocess:
        # Parse subprocess command
        parts = args.blue_subprocess.split()
        program = parts[0]
        prog_args = parts[1:] if len(parts) > 1 else []
        blue_player = SubprocessPlayer(
            color=Color.BLUE,
            program_path=program,
            args=prog_args,
            timeout=args.timeout,
            memory_limit_mb=args.memory_limit,
            name=args.blue_name,
            stderr_callback=stderr_callback
        )
    else:
        blue_player = GUIPlayer(Color.BLUE, args.blue_name)

    # Track subprocess players for cleanup
    subprocess_players = []
    if isinstance(red_player, SubprocessPlayer):
        subprocess_players.append(red_player)
    if isinstance(blue_player, SubprocessPlayer):
        subprocess_players.append(blue_player)

    # Create view if not provided (first run)
    if view is None:
        view = TkinterView(game)
        view.setup_window()
    else:
        # Reuse existing view, update controller
        view.controller = game

    # Initialize subprocess players if any
    if subprocess_players:
        print("Initializing subprocess players...")
        for player in subprocess_players:
            if not player.initialize(args.board_size):
                print(f"\nError: Failed to initialize {player.name}")
                print("Make sure the command is correct and the program exists.")
                # Cleanup already initialized players
                for p in subprocess_players:
                    p.cleanup()
                sys.exit(1)
        print("✓ All subprocess players initialized successfully\n")

    # Setup click callback to handle both players
    def handle_click(row_or_move, col=None):
        """Handle click from GUI - determine which player it's for."""
        current_player = game.current_player
        if isinstance(current_player, GUIPlayer):
            # If col is provided, it's a (row, col) click
            if col is not None:
                current_player.set_move((row_or_move, col))
            else:
                # It's a special move like "swap" or None
                current_player.set_move(row_or_move)

    view.set_click_callback(handle_click)

    # Set replay callback
    def replay_game():
        """Replay the game with same settings."""
        # Cleanup current subprocess players
        for player in subprocess_players:
            player.cleanup()
        # Clear the list
        subprocess_players.clear()
        # Restart game
        run_game(args, view, is_first_run=False)

    view.set_replay_callback(replay_game)

    # Start game
    view.display_game_start()

    if not game.start_game(red_player, blue_player):
        print("\nError: Failed to start game")
        # Cleanup subprocess players
        for player in subprocess_players:
            player.cleanup()
        sys.exit(1)

    # Game loop with cleanup handling
    try:
        # Game loop
        def game_loop():
            """Main game loop that runs alongside tkinter event loop."""
            if game.status != GameStatus.ONGOING:
                return

            # Display current state
            view.display_board()
            view.display_stats()
            view.display_log()  # Show all events
            view.display_turn_start()

            # Get current player
            current_player = game.current_player

            if isinstance(current_player, GUIPlayer):
                # GUI player - wait for click
                if current_player.is_waiting():
                    # Still waiting for user input, check again soon
                    view.root.after(50, game_loop)
                    return

                # Check if move was set
                if current_player.pending_move is not None:
                    # Move was made, play the turn
                    continue_game = game.play_turn()

                    if not continue_game:
                        # Game ended
                        view.display_board()
                        view.display_stats()
                        view.display_log()
                        view.display_game_end()
                        return

                    # Continue to next turn
                    view.root.after(100, game_loop)
                else:
                    # Request move from player
                    current_player.get_move(game.board)
                    # Check again soon
                    view.root.after(50, game_loop)
            else:
                # Non-GUI player (subprocess support)
                continue_game = game.play_turn()

                if not continue_game:
                    # Game ended
                    view.display_board()
                    view.display_stats()
                    view.display_log()
                    view.display_game_end()
                    return

                # Continue to next turn
                view.root.after(100, game_loop)

        # Start game loop
        view.root.after(100, game_loop)

        # Run tkinter event loop (only on first run)
        if is_first_run:
            view.run()

    finally:
        # Cleanup subprocess players (only on first run/exit)
        if is_first_run and subprocess_players:
            print("\nCleaning up subprocess players...")
            for player in subprocess_players:
                player.cleanup()
            print("✓ Cleanup complete")

    if is_first_run:
        print("\nThank you for playing!")


def main():
    """Main entry point for GUI game."""
    args = parse_arguments()

    # Validate board size
    if args.board_size < MIN_BOARD_SIZE or args.board_size > MAX_BOARD_SIZE:
        print(
            f"Error: Board size must be between {MIN_BOARD_SIZE} and {MAX_BOARD_SIZE}")
        sys.exit(1)

    # Run the game
    run_game(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
