import pathlib
import queue
import random
from encodings.punycode import T
from enum import Enum
from operator import contains
from queue import Queue
from typing import Callable, List, Tuple

from IntCode import run_intcode
from SparseGrid import SparseGrid


def parse_program(text: str) -> dict[int, int]:
    parts = [int(p.strip()) for p in text.replace("\n", ",").split(",")]
    return {i: v for i, v in enumerate(parts)}


# print_ascii by chatGPT
def print_ascii(
    panels: List[List[int]], cur_loc: Tuple[int, int], heading: Tuple[int, int]
) -> None:
    rows, cols = len(panels), len(panels[0])

    # choose a character to represent heading
    heading_char = {
        (-1, 0): "^",
        (1, 0): "v",
        (0, -1): "<",
        (0, 1): ">",
    }[heading]

    for r in range(rows):
        line = []
        for c in range(cols):
            if (r, c) == cur_loc:
                line.append(heading_char)
            else:
                line.append("#" if panels[r][c] == 1 else ".")
        print("".join(line))


OP_NORTH = 1
OP_SOUTH = 2
OP_WEST = 3
OP_EAST = 4

ALL_OPS = [OP_NORTH, OP_SOUTH, OP_EAST, OP_WEST]

RET_WALL = 0
RET_MOVE = 1
RET_MOVE_O2 = 2


def path_to_ops(path: List[Tuple[int, int]]) -> List[int]:
    ops = []
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        right, up = x2 - x1, y2 - y1
        if right == 1 and up == 0:
            ops.append(OP_EAST)
        elif right == -1 and up == 0:
            ops.append(OP_WEST)
        elif right == 0 and up == 1:
            ops.append(OP_NORTH)
        elif right == 0 and up == -1:
            ops.append(OP_SOUTH)
        else:
            raise ValueError(f"Invalid move from {(x1,y1)} to {(x2,y2)}")
    return ops


def find_path(
    grid: SparseGrid, start: Tuple[int, int], end: Tuple[int, int]
) -> List[Tuple[int, int]]:
    paths: Queue[Tuple[List[Tuple[int, int]], Tuple[int, int]]] = Queue()

    visited: List[Tuple[int, int]] = []
    paths.put(([start], start))

    bounds = grid.bounds_square()

    while paths.qsize() > 0:
        path = paths.get()
        loc = path[1]

        if loc == end:
            return path[0]

        if (
            loc not in visited
            and grid.get(loc[0], loc[1]) != 1
            and loc[0] >= bounds[0]
            and loc[0] <= bounds[1]
            and loc[1] >= bounds[2]
            and loc[1] <= bounds[3]
        ):
            visited.append(loc)
            left = (loc[0] - 1, loc[1])
            paths.put(([*path[0], left], left))
            right = (loc[0] + 1, loc[1])
            paths.put(([*path[0], right], right))
            down = (loc[0], loc[1] - 1)
            paths.put(([*path[0], down], down))
            up = (loc[0], loc[1] + 1)
            paths.put(([*path[0], up], up))

    return []


def get_target_xy(cur_xy: Tuple[int, int], movement_op: int) -> Tuple[int, int]:
    if movement_op == OP_NORTH:
        target_xy = (cur_xy[0], cur_xy[1] + 1)
    elif movement_op == OP_SOUTH:
        target_xy = (cur_xy[0], cur_xy[1] - 1)
    elif movement_op == OP_WEST:
        target_xy = (cur_xy[0] - 1, cur_xy[1])
    elif movement_op == OP_EAST:
        target_xy = (cur_xy[0] + 1, cur_xy[1])
    else:
        raise RuntimeError(f"response for unknown movement op {movement_op}")
    return target_xy


def main() -> int:

    input_file = pathlib.Path(__file__).parent / "input.txt"

    grid: List[List[int]] = [[]]
    robot_xy = (0, 0)

    def print_grid(grid):
        for row in grid:
            print("".join(chr(val) for val in row))

    def find_intersections(grid: list[List[int]]):
        intersections = []
        rows, cols = len(grid), len(grid[0])
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == ord("#"):
                    neighbors = 0
                    for dr, dc in [
                        (0, 1),
                        (1, 0),
                        (0, -1),
                        (-1, 0),
                    ]:
                        nr, nc = r + dr, c + dc
                        if (
                            0 <= nr < rows
                            and 0 <= nc < cols
                            and grid[nr][nc] == ord("#")
                        ):
                            neighbors += 1
                    if neighbors > 2:
                        intersections.append((r, c))
        return intersections

    def write_in() -> int:
        return 0

    lastval = 0

    def read_out(val: int):
        nonlocal lastval
        if val == ord("\n"):
            print_grid(grid)
            intersections: List[Tuple[int, int]] = find_intersections(grid)
            print(sum(a * b for a, b in intersections))

        else:
            if lastval == ord("\n"):
                grid.append([])
            grid[-1].append(val)
        lastval = val

    with open(input_file, "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        mem[0] = 2
        run_intcode(mem, write_in, read_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
