import subprocess
import shutil
import os
import logging
from config import STOCKFISH_PATHS, STOCKFISH_SKILL_LEVEL
from typing import Optional
from fen_utils import validate_fen_structure
from config import STOCKFISH_TIME_LIMIT

# Turn logging on
logger = logging.getLogger(__name__)

class StockfishEngine:

    def __init__(self, skill_level=None):
        self.skill_level = skill_level or STOCKFISH_SKILL_LEVEL # Set skill level of stockfish engine
        self.process = None     # Hold subprocess object which is the stockfish program running
        self.is_running = False # Tracks UCI handshake
        self.stockfish_path = self._find_stockfish()

    # Loops through the list of Stockfish paths and sees if the direct file path exists, and if it is a command name on system path
    # NEED SYSTEM PATH AND FILEPATH OF STOCKFISH CONFIGURED
    # Called internally to check for existing paths
    def _find_stockfish(self):
        for path in STOCKFISH_PATHS:
            if os.path.isfile(path):
                logger.info(f"Found Stockfish at: {path}")
                return path
            found = shutil.which(path)
            if found:
                logger.info(f"Found Stockfish on PATH: {found}")
                return found
        logger.warning("Stockfish not found in path")
        return None
    
    # Wrute string to Stockfish stdin and then flushes. 
    def _send_command(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    # Reads the stdout line by line until it sees line containing target (uciok or readyok)
    # Set lines to 1000 so it does not loop forever when unexpected Stockfish return
    def _read_until(self, target, max_lines=1000):
        lines = []
        for _ in range(max_lines):
            line = self.process.stdout.readline().strip()
            lines.append(line)
            if target in line :
                return lines
        return lines
    
    # subprocess.Popen spawns Stockfish as child process with three pipes
    # stdin --> write commands here
    # stdout --> read responses here
    # stderr --> captures error output
    # UCI handshake: Send UCI --> wait for uciok --> set options --> send isready --> wait for readyok
    def start(self):
        if self.stockfish_path is None:
            logger.error("Stockfish path is not found")
            return False
        if self.is_running:
            return True
        try:
            self.process = subprocess.Popen(
                [self.stockfish_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self._send_command("uci")
            self._read_until("uciok")
            self._send_command(f"setoption name Skill Level value {self.skill_level}")
            self._send_command("isready")
            self._read_until("readyok")
            self.is_running = True
            logger.info(f"Stockfish started (skill level {self.skill_level})")
            return True
        except Exception as e:
            logger.error(f"Failed to start Stockfish: {e}")
            self.is_running = False
            return False
        
    def stop(self):
        if self.process and self.is_running:
            try:
                self._send_command("quit")
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
            self.is_running = False
            self.process = None
            logger.info("Stockfish stopped")

    def is_available(self) :
        return self.is_running and self.process is not None
    
    # FEN position tells Stockfish what is current board, go movetime tells stockfish to think for 2000ms
    def get_best_move(self, fen, time_limit=None):
        time_limit = time_limit or STOCKFISH_TIME_LIMIT
        if not self.is_available():
            logger.warning("Engine not running")
            return None
        
        try:
            # _read_until("bestmove") --> Stockfish outputs analysis lines, then finally returns best move and best follow up move
            self._send_command(f"position fen {fen}")
            self._send_command(f"go movetime {int(time_limit * 1000)}")
            output = self._read_until("bestmove")
            
            for line in output:
                # Need only the best move and not the followup, so split it and grab index [1]
                if line.startswith("bestmove"):
                    parts = line.split()
                    move = parts[1] # ex e2e4
                    if move == "(none)":
                        return None
                    return move
            return None

        except Exception as e:
            logger.error(f"Error getting best move: {e}")
            return None
        
    # Same as get best move, except this method includes Stockfish analysis lines to observe search depth and evaluated nodes.
    def get_best_move_with_info(self, fen, time_limit=None):
        time_limit = time_limit or STOCKFISH_TIME_LIMIT
        if not self.is_available():
            return {"best_move": None}

        try:
            self._send_command(f"position fen {fen}")
            self._send_command(f"go movetime {int(time_limit * 1000)}")
            output = self._read_until("bestmove")

            result = {
                "best_move": None,
                "ponder_move": None,
                "depth": 0,
                "nodes": 0,
                "time_ms": 0,
                "score_type": None,
                "score_value": 0,
            }

            # Stockfish outputs lines in this format while thinking.
            # info depth ## nodes ## time 2000
            # Only really care about the last line as it is the deepest search before the end of the time allotted --> highest depth
            # Dynamically assign the last_info
            # Do we need this? Probably not. But I am using it to analyze depth when we get a stockfish response
            last_info = None
            last_score_info = None
            for line in output:
                if line.startswith("info depth"):
                    last_info = line
                    if "score" in line:
                        last_score_info = line

                if line.startswith("bestmove"):
                    parts = line.split()
                    result["best_move"] = parts[1] if parts[1] != "(none)" else None
                    # Ponder is what Stockfish expects the opponent to play next --> factors into decision making
                    if "ponder" in parts:
                        ponder_idx = parts.index("ponder")
                        result["ponder_move"] = parts[ponder_idx + 1]

            
            if last_info:
                tokens = last_info.split()
                for key in ["depth", "nodes", "time"]:
                    if key in tokens:
                        idx = tokens.index(key)
                        value = int(tokens[idx + 1])
                        if key == "time":
                            result["time_ms"] = value
                        else:
                            result[key] = value
            
            if last_score_info:
                tokens = last_score_info.split()
                if "score" in tokens:
                    score_idx = tokens.index("score")
                    result["score_type"] = tokens[score_idx + 1]
                    result["score_value"] = int(tokens[score_idx + 2])

            return result

        except Exception as e:
            logger.error(f"Error getting move info: {e}")
            return {"best_move": None}
    

    # Evaluation function for the stockfish analysis of the position, not just finding the best move BUT ALSO evaluating the position.
    # Depth is currently set to 18, can be changed.
    def get_evaluation(self, fen, depth=18):
        if not self.is_available():
            return {"type": "cp", "value": 0, "best_move": None}
        
        try:
            # Send the FEN and depth, output the best move
            self._send_command(f"position fen {fen}")
            self._send_command(f"go depth {depth}")
            output = self._read_until("bestmove")


            result = {
                "type": "cp",
                "value": 0,
                "depth": 0,
                "best_move": None,
                "is_white_better": True,
                "human_readable": "0.00",
            }

            # Same as before. Find the last info line that contains the score which represents the deepest search.
            last_score_line = None
            for line in output:
                if "score" in line and line.startswith("info"):
                    last_score_line = line
                if line.startswith("bestmove"):
                    parts = line.split()
                    result["best_move"] = parts[1] if parts[1] != "(none)" else None

            # If last score line exists, then parse through it and find the score type (either cp (centipawns) or mate (checkmate in x moves)) and the score value (either # of centipawns or # of moves until checkmate)
            if last_score_line:
                tokens = last_score_line.split()
                if "score" in tokens:
                    score_idx = tokens.index("score")
                    score_type = tokens[score_idx + 1]
                    score_value = int(tokens[score_idx + 2])

                    result["type"] = score_type
                    result["value"] = score_value
                    result["is_white_better"] = score_value > 0

                    if score_type == "cp":
                        val = score_value / 100 # Convert to pawns
                        result["human_readable"] = f"+{val:.2f}" if val >= 0 else f"{val:.2f}"
                    elif score_type == "mate":
                        if score_value > 0:
                            result["human_readable"] = f"Mate in {score_value}" # Convert to a readable value
                        else :
                            result["human_readable"] = f"Mated in {abs(score_value)}"
                
                if "depth" in tokens:
                    depth_idx = tokens.index("depth")
                    result["depth"] = int(tokens[depth_idx + 1])

            return result
        
        except Exception as e:
            logger.error(f"Error evaluating position: {e}")
            return {"type": "cp", "value": 0, "best_move":None}


    # UCI handshake where option is set and then isready and readyok is used to confirm that Stockfish accepted the level change
    # Updating the level of the engine results in it being stronger (closer to 20) or weaker (closer to 1)
    def set_skill_level(self, level):
        if not 1 <= level <= 20:
            logger.warning(f"Skill level that is {level} is out of the 1-20 range. Reset it")
            return
        
        self._send_command(f"setoption name Skill Level value {level}")
        self._send_command("isready")
        self._read_until("readyok")
        self.skill_level = level
        logger.info(f"Skill level has been changed to {level}")

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False