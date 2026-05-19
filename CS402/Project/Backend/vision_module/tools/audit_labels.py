# data/chess_dataset/tools/audit_labels.py
from pathlib import Path
import argparse

def parse_line(line):
    parts = line.strip().split()
    if len(parts) != 5:
        return None
    try:
        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        return cls, x, y, w, h
    except Exception:
        return None

def clamp01(v): 
    return max(0.0, min(1.0, v))

def audit_dir(lbl_dir: Path, nc: int, fix: bool):
    bad_files = 0
    bad_lines = 0
    files = list(lbl_dir.rglob("*.txt"))
    for fp in files:
        with fp.open() as f:
            lines = f.readlines()

        keep = []
        file_had_issue = False
        for i, line in enumerate(lines, 1):
            parsed = parse_line(line)
            if not parsed:
                file_had_issue = True
                bad_lines += 1
                continue
            cls, x, y, w, h = parsed

            # checks
            if cls < 0 or cls >= nc:
                file_had_issue = True
                bad_lines += 1
                continue
            if any(map(lambda v: v != v, [x, y, w, h])):  # NaN check
                file_had_issue = True
                bad_lines += 1
                continue
            # clamp
            x2 = clamp01(x); y2 = clamp01(y); w2 = clamp01(w); h2 = clamp01(h)
            # drop zero/negative boxes
            if w2 <= 0 or h2 <= 0:
                file_had_issue = True
                bad_lines += 1
                continue

            keep.append(f"{cls} {x2:.6f} {y2:.6f} {w2:.6f} {h2:.6f}\n")

        if file_had_issue:
            bad_files += 1
            if fix:
                if keep:
                    with fp.open("w") as f:
                        f.writelines(keep)
                else:
                    fp.unlink()  # remove empty/invalid file

    return bad_files, bad_lines, len(files)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--nc", type=int, default=12)
    p.add_argument("--fix", action="store_true")
    p.add_argument("--root", type=str, default=str(Path(__file__).resolve().parents[1]))
    args = p.parse_args()

    root = Path(args.root)
    for split in ["train", "valid"]:
        lbl_dir = root / split / "labels"
        if not lbl_dir.exists():
            print(f"Missing {lbl_dir}")
            continue
        bad_files, bad_lines, total = audit_dir(lbl_dir, args.nc, args.fix)
        print(f"[{split}] scanned {total} files • bad_files={bad_files} • bad_lines={bad_lines}")

if __name__ == "__main__":
    main()
