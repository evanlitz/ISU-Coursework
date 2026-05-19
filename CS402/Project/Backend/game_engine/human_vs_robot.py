from board_state import BoardState
from game_state import GameStateMachine, GameState, GameInfo
from move_validator import MoveValidator
from stockfish_engine import StockfishEngine
from game_over_detector import GameOverDetector
from robot_planner import plan_robot_action


def print_game_info(info):
    print(f"\n  --- Game Info ---")
    print(f"  state:              {info.state.value}")
    print(f"  current_fen:        {info.current_fen}")
    print(f"  turn:               {info.turn}")
    print(f"  move_number:        {info.move_number}")
    print(f"  last_move:          {info.last_move}")
    print(f"  pending_robot_move: {info.pending_robot_move}")
    print(f"  evaluation:         {info.evaluation}")
    print(f"  is_check:           {info.is_check}")
    print(f"  game_result:        {info.game_result}")
    print(f"  message:            {info.message}")
    print(f"  -------------------")


def main():
    # Initialize all of the components of the game loop
    board_state = BoardState()
    state_machine = GameStateMachine()
    validator = MoveValidator()
    game_over = GameOverDetector()
    engine = StockfishEngine()
    engine.start()

    # Unnecessary but move count and move history is easy to track and may work well for validation, so initializing here.
    move_count = 0
    move_history = []

    print("=" * 40)
    print("  CHESS GAME LOOP DEMO 1")
    print("  Type moves in UCI (e.g. e2e4)")
    print("  Type 'resign' or 'quit' to exit")
    print("=" * 40)
    print()
    print(board_state.board)
    print()

    # Transition: IDLE -> WAITING_FOR_OPPONENT
    # This represents starting the game. For this loop, I always have the opponent (human in this case) starting the game and representing white, while the robot plays black.
    state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
    print(f"State: {state_machine.get_state()}")
    print("Waiting for your move...")

    try:
        # Game loop, while the game is not over
        while not board_state.is_game_over():
            print(f"\nTurn: {board_state.get_turn().upper()}")
            print(f"State: {state_machine.get_state()}")

            # Check if the game is over, and if it is, then transition to the game over state and print result and board
            result = game_over.check(board_state.board)
            if result.is_over:
                state_machine.transition_to(GameState.GAME_OVER)
                print(f"\nGAME OVER: {result.message}")
                print(f"Result: {result.score}")
                print()
                print(board_state.board)
                break

            # Get human move
            while True:
                uci_move = input("\nEnter your move (UCI format, e.g. e2e4): ").strip()
                if uci_move.lower() in ("resign", "quit", "exit"):
                    print("\nYou resigned. Game over.")
                    state_machine.transition_to(GameState.GAME_OVER)
                    break
                is_valid, message = validator.validate_move(board_state.get_fen(), uci_move)
                if is_valid:
                    break
                print(f"Invalid move: {message}")

            if uci_move.lower() in ("resign", "quit", "exit"):
                break

            # Apply human move
            board_state.push_move(uci_move)
            move_count += 1
            move_history.append(f"{move_count}. {uci_move}")
            print(f"\nYou played: {uci_move}")
            print()
            print(board_state.board)

            print_game_info(GameInfo(
                state=state_machine.get_state(),
                current_fen=board_state.get_fen(),
                turn=board_state.get_turn(),
                move_number=move_count,
                last_move=uci_move,
                is_check=board_state.board.is_check(),
            ))

            # Check game over after human move
            result = game_over.check(board_state.board)
            if result.is_over:
                state_machine.transition_to(GameState.GAME_OVER)
                print(f"\nGAME OVER: {result.message}")
                print(f"Result: {result.score}")
                break

            # Transition: WAITING_FOR_OPPONENT -> ROBOT_THINKING
            state_machine.transition_to(GameState.ROBOT_THINKING)
            print(f"\nState: {state_machine.get_state()}")
            print("Robot is thinking...")

            # Stockfish response
            try:
                sf_result = engine.get_best_move_with_info(board_state.get_fen())
                best_move = sf_result["best_move"]
                print(f"\nStockfish plays: {best_move}")
                print(f"  Depth: {sf_result.get('depth', '?')}")
                print(f"  Score: {sf_result.get('score_value', '?')} ({sf_result.get('score_type', '?')})")
            except Exception as e:
                print(f"\nStockfish error: {e}")
                print("Falling back to first legal move...")
                best_move = board_state.get_legal_moves()[0]
                print(f"Playing: {best_move}")

            # Classify the move and plan robot action
            move_info = validator.classify_move(board_state.get_fen(), best_move)
            robot_plan = plan_robot_action(move_info)
            print(f"\nRobot Action Plan:")
            print(f"  Move type: {move_info.special or 'normal'}")
            print(f"  {robot_plan}")

            # Apply AI move
            board_state.push_move(best_move)
            move_history.append(f"   ...{best_move}")
            print()
            print(board_state.board)

            # Transition: ROBOT_THINKING -> ROBOT_MOVING -> WAITING_FOR_OPPONENT
            state_machine.transition_to(GameState.ROBOT_MOVING)
            print(f"\nState: {state_machine.get_state()}")
            state_machine.transition_to(GameState.WAITING_FOR_OPPONENT)
            print(f"State: {state_machine.get_state()}")

            print_game_info(GameInfo(
                state=state_machine.get_state(),
                current_fen=board_state.get_fen(),
                turn=board_state.get_turn(),
                move_number=move_count,
                last_move=best_move,
                evaluation=sf_result,
                is_check=board_state.board.is_check(),
            ))

            # Move history
            print(f"\nMove history:")
            for move in move_history:
                print(f"  {move}")
            print("-" * 40)

    except KeyboardInterrupt:
        print("\n\nInterrupted. Shutting down...")

    finally:
        engine.stop()
        print("\nStockfish engine stopped.")
        print("Demo complete.")


if __name__ == "__main__":
    main()
