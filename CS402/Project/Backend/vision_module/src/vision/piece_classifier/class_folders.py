"""
Windows-safe folder names for piece classification.

On Windows, the filesystem is case-insensitive, so 'P' and 'p' would collide.
We use a suffix for black pieces: p -> p_b, n -> n_b, etc.
"""

# 13 classes in FEN order (empty, white pieces, black pieces)
FEN_CLASSES = ["empty", "P", "p", "N", "n", "B", "b", "R", "r", "Q", "q", "K", "k"]

# Map FEN symbol -> folder name (for Windows case-insensitive FS)
# Black pieces get _b suffix to avoid P/p, N/n, etc. collision
FEN_TO_FOLDER = {
    "empty": "empty",
    "P": "P", "p": "p_b",
    "N": "N", "n": "n_b",
    "B": "B", "b": "b_b",
    "R": "R", "r": "r_b",
    "Q": "Q", "q": "q_b",
    "K": "K", "k": "k_b",
}

# Map folder name -> FEN symbol (for model inference output)
FOLDER_TO_FEN = {v: k for k, v in FEN_TO_FOLDER.items()}

# All folder names (for creating directories)
FOLDER_NAMES = list(FOLDER_TO_FEN.keys())
