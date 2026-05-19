import time
from board_state import BoardState
from game_state import GameStateMachine, GameState
from move_validator import MoveValidator
from stockfish_engine import StockfishEngine
from game_over_detector import GameOverDetector
from robot_planner import plan_robot_action


SKILL_LEVEL_1 = 20
SKILL_LEVEL_2 = 1
MOVE_DELAY = 2.5  # seconds between moves
MAX_MOVES = 300   # safety cap to prevent infinite games


def main():
    # Initialize all components
    board_state = BoardState()
    state_machine = GameStateMachine()
    validator = MoveValidator()
    game_over = GameOverDetector()

    # Two separate Stockfish engines
    white_engine = StockfishEngine(skill_level=SKILL_LEVEL_1)
    black_engine = StockfishEngine(skill_level=SKILL_LEVEL_2)
    white_engine.start()
    black_engine.start()

    move_count = 0
    move_history = []

    print("=" * 50)
    print("  ROBOT vs ROBOT - Stockfish vs Stockfish")
    print(f"  White Engine: Stockfish (Skill {SKILL_LEVEL_1})")
    print(f"  Black Engine: Stockfish (Skill {SKILL_LEVEL_2})")
    print(f"  Delay between moves: {MOVE_DELAY}s")
    print("=" * 50)
    print()
    print(board_state.board)
    print()

    # IDLE -> WAITING_FOR_OPPONENT
    state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)

    try:
        while move_count < MAX_MOVES:
            turn = board_state.get_turn()  # "white" or "black"
            engine = white_engine if turn == "white" else black_engine
            move_count += 1

            print(f"\n{'=' * 50}")
            print(f"  Move {move_count} - {turn.upper()}'s turn")
            print(f"{'=' * 50}")

            # WAITING_FOR_OPPONENT -> ROBOT_THINKING
            state_machine.transition_to(GameState.ROBOT_THINKING)
            print(f"State: {state_machine.get_state().value}")
            print(f"{turn.capitalize()} engine is thinking...")

            # Get best move from the active engine
            try:
                sf_result = engine.get_best_move_with_info(board_state.get_fen())
                best_move = sf_result["best_move"]

                if best_move is None:
                    print("Engine returned no move. Game may be over.")
                    break

                print(f"\n  {turn.capitalize()} plays: {best_move}")
                print(f"  Depth: {sf_result.get('depth', '?')}")
                print(f"  Score: {sf_result.get('score_value', '?')} ({sf_result.get('score_type', '?')})")

            except Exception as e:
                print(f"\nStockfish error: {e}")
                print("Falling back to first legal move...")
                best_move = board_state.get_legal_moves()[0]
                print(f"  Playing: {best_move}")

            # Classify the move and plan robot action
            move_info = validator.classify_move(board_state.get_fen(), best_move)
            robot_plan = plan_robot_action(move_info)
            print(f"\n  Move type: {move_info.special or 'normal'}")
            print(f"  Robot Action: {robot_plan}")

            # ROBOT_THINKING -> ROBOT_MOVING
            state_machine.transition_to(GameState.ROBOT_MOVING)
            print(f"\nState: {state_machine.get_state().value}")

            # Apply the move
            board_state.push_move(best_move)
            move_history.append(f"{'W' if turn == 'white' else 'B'}: {best_move}")

            print()
            print(board_state.board)

            # ROBOT_MOVING -> WAITING_FOR_OPPONENT
            state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
            print(f"State: {state_machine.get_state().value}")

            # Check for game over
            result = game_over.check(board_state.board)
            if result.is_over:
                state_machine.transition_to(GameState.GAME_OVER)
                print(f"\n{'*' * 50}")
                print(f"  GAME OVER: {result.message}")
                print(f"  Result: {result.score}")
                print(f"  Total moves: {move_count}")
                print(f"{'*' * 50}")
                break

            # Print move history
            print(f"\nMove history: {', '.join(move_history[-10:])}")
            if len(move_history) > 10:
                print(f"  (showing last 10 of {len(move_history)})")

            print(f"\n--- Next move in {MOVE_DELAY}s ---")
            time.sleep(MOVE_DELAY)

        else:
            print(f"\nMax move limit ({MAX_MOVES}) reached. Stopping game.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Shutting down...")

    finally:
        white_engine.stop()
        black_engine.stop()
        print("\nBoth Stockfish engines stopped.")
        print(f"Total moves played: {move_count}")
        print("Demo complete.")


if __name__ == "__main__":
    main()
