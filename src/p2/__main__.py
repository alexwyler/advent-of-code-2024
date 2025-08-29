import heapq
import sys
from collections import Counter, defaultdict
from typing import List, Tuple


def parse_and_sort_file(file_path: str) -> Tuple[List[int], List[int]]:
    left_column: List[int] = []
    right_column: List[int] = []

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            try:
                left_column.append(int(parts[0]))
                right_column.append(int(parts[1]))
            except ValueError:
                continue  # skip lines that aren't numbers

    left_column.sort()
    right_column.sort()
    return left_column, right_column



if __name__ == "__main__":

    (left_column, right_column) = parse_and_sort_file("input.txt")

    similarity_map = {}

    freq_left = Counter(left_column)
    freq_right = Counter(right_column)

    print(freq_left, freq_right)

    for key in freq_left:

        other_freq = freq_right.get(key, 0)
        sim_delta = key * other_freq
        if sim_delta > 0:
            print(f"{key} appears {other_freq} times in right, so similarity += {sim_delta}")
        similarity_map[key] = similarity_map.get(key, 0) + sim_delta

    # for key in freq_right:
    #     other_freq = freq_left.get(key, 0)
    #     sim_delta = key * other_freq
    #     if sim_delta > 0:
    #         print(f"{key} appears {other_freq} times in left, so similarity += {sim_delta}")
    #     similarity_map[key] = similarity_map.get(key, 0) + sim_delta

    print(sum(similarity_map.values()))