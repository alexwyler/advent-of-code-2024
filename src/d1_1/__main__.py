import heapq
import sys
from collections import defaultdict


def stream_smallest_two_columns(file_path, n, offset_i, m, offset_j):
    # Track smallest > n for left column
    smallest_i = None
    lines_i = []

    # Track smallest > m for right column
    smallest_j = None
    lines_j = []

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            try:
                left = int(parts[0])
                right = int(parts[1])
            except ValueError:
                continue

            # --- left column ---
            if left > n:
                if smallest_i is None or left < smallest_i:
                    smallest_i = left
                    lines_i = [left]
                elif left == smallest_i:
                    lines_i.append(left)

            # --- right column ---
            if right > m:
                if smallest_j is None or right < smallest_j:
                    smallest_j = right
                    lines_j = [right]
                elif right == smallest_j:
                    lines_j.append(right)

    # Apply offsets, always return smallest number even if resulting list is empty
    result_i = lines_i[offset_i:] if smallest_i is not None else []
    result_j = lines_j[offset_j:] if smallest_j is not None else []

    return (smallest_i, result_i), (smallest_j, result_j)


if __name__ == "__main__":

    n, m = 0, 0
    offset_i, offset_j = 0, 0

    diff = 0
    while True:
        (smallest_i, lines_i), (smallest_j, lines_j) = stream_smallest_two_columns(
            "./input.txt",
            n, offset_i,
            m, offset_j
        )

        if smallest_i is None and smallest_j is None:
            break

        if not lines_i:
            n += 1
            offset_i = 0
            continue
        else:
            if len(lines_i) == 1:
                n = smallest_i
                offset_i = 0
            else:
                offset_i += 1
           
        if not lines_j:
            m += 1
            offset_j = 0
            continue
        else:
            if len(lines_j) == 1:
                m = smallest_j
                offset_j = 0
            else:
                offset_j += 1
        
         

        print("Smallest left number:", smallest_i, "Lines:", lines_i)
        print("Smallest right number:", smallest_j, "Lines:", lines_j)

        diff += abs(smallest_i - smallest_j)
        # update n/m to previous smallest for next iteration

    print(diff)


