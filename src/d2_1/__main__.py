import heapq
import sys
from collections import Counter, defaultdict
from typing import List, Tuple


def is_valid_sequence(nums: List[int]) -> bool:
    if len(nums) < 2:
        return True  # trivially valid

    diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]

    # Condition 1: check monotonic (allowing equals)
    non_decreasing = all(d > 0 for d in diffs)
    non_increasing = all(d < 0 for d in diffs)

    # Condition 2: adjacent differences must be <= 3 in absolute value
    small_steps = all(abs(d) <= 3 for d in diffs)

    return (non_decreasing or non_increasing) and small_steps

def valid_with_single_mod(nums: List[int]) -> bool:
    # If already valid, return True
    if is_valid_sequence(nums):
        return True
    # Try removing each element one by one
    for i in range(len(nums)):
        candidate = nums[:i] + nums[i+1:]
        if is_valid_sequence(candidate):
            return True
    return False

def count_invalid_lines(filename: str) -> int:
    valid_count = 0
    with open(filename, "r") as f:
        for line in f:
            mapInts = map(int, line.strip().split())
            nums = list(mapInts)
            if valid_with_single_mod(nums):
                print(f"{nums} valid")
                valid_count += 1
    return valid_count

if __name__ == "__main__":

    print(count_invalid_lines("input.txt"))
