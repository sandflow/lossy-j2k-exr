import re
import csv
import sys
import argparse


def parse(path):
    rows = []
    filename = None
    dwa_row = None
    ojph_rows = []
    in_dwa = False
    in_ojph = False

    with open(path) as f:
        for line in f:
            line = line.rstrip()

            m = re.match(r'^=== (.+) ===$', line)
            if m:
                if filename and dwa_row and ojph_rows:
                    rows.append((filename, dwa_row, ojph_rows[-1]))
                filename = m.group(1)
                dwa_row = None
                ojph_rows = []
                in_dwa = False
                in_ojph = False
                continue

            if line == 'DWA':
                in_dwa = True
                in_ojph = False
                continue

            if line == 'OJPH':
                in_ojph = True
                in_dwa = False
                continue

            if line in ('Q,MSE,size', 'Q,MSE,size,diff'):
                continue

            parts = line.split(',')
            if in_dwa and dwa_row is None and len(parts) == 3:
                dwa_row = parts
            elif in_ojph and len(parts) == 4:
                ojph_rows.append(parts[:3])

    if filename and dwa_row and ojph_rows:
        rows.append((filename, dwa_row, ojph_rows[-1]))

    return rows


def main():
    parser = argparse.ArgumentParser(description="Parse out.txt into a CSV.")
    parser.add_argument("input", nargs="?", default="out.txt")
    parser.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args()

    rows = parse(args.input)

    with open(args.output, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "dwa_q", "dwa_mse", "dwa_size",
                    "ojph_q", "ojph_mse", "ojph_size"])
        for filename, dwa, ojph in rows:
            w.writerow([filename] + dwa + ojph)

    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
