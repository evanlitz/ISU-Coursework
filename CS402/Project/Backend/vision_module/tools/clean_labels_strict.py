import os
import glob

def clean_labels(path):
    kept, dropped = 0, 0
    for label_file in glob.glob(os.path.join(path, "*.txt")):
        new_lines = []
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    dropped += 1
                    continue
                cls, x, y, w, h = parts[:5]
                try:
                    cls = int(cls)
                    x, y, w, h = map(float, (x, y, w, h))
                    if cls < 0 or x < 0 or y < 0 or w <= 0 or h <= 0:
                        dropped += 1
                        continue
                    new_lines.append(line)
                    kept += 1
                except ValueError:
                    dropped += 1
        with open(label_file, "w") as f:
            f.writelines(new_lines)
    print(f"{path}: kept={kept}, dropped={dropped}")

if __name__ == "__main__":
    for split in ["train/labels", "valid/labels"]:
        if os.path.exists(split):
            clean_labels(split)
