import heapq
import sys
from collections import Counter, defaultdict
from typing import List, Tuple


def parse_input_file(filename: str) -> Tuple[List[List[int]], List[List[int]]]:
    keys, locks = [], []
    buffer = []

    def process_block(block: List[str]):
        if not block:
            return
        cols = len(block[0])
        col_counts = [sum(1 for row in block if row[c] == '#') for c in range(cols)]
        if block[-1] == '#'*cols:
            keys.append([count - 1 for count in col_counts])
        elif block[0] == '#'*cols:
            locks.append([cols - (count - 1) for count in col_counts])
        else:
            raise ValueError("Block does not match any known type")

    with open(filename, "r") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "":
                process_block(buffer)
                buffer = []
            else:
                buffer.append(line)
        process_block(buffer)

    return keys, locks


def count_keys_fit_in_locks(keys: List[List[int]], locks: List[List[int]]) -> List[Tuple[List[int], List[int]]]:
    result: List[Tuple[List[int], List[int]]] = []
    for row1 in keys:
        for row2 in locks:
            if len(row1) != len(row2):
                continue 
            if all(pin <= lock_hole for pin, lock_hole in zip(row1, row2)):
                result.append((row1, row2))
    return result

if __name__ == "__main__":

    keys, locks = parse_input_file("input.txt")
    print("Type 1:", keys)
    print("Type 2:", locks)
    pairs = count_keys_fit_in_locks(keys, locks)
    print(len(pairs))

