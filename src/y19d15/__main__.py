import pathlib
import queue
import random
from encodings.punycode import T
from enum import Enum
from operator import contains
from queue import Queue
from typing import Callable, Dict, List, Tuple


class OP(Enum):
    ADD = (1, 3)
    MULT = (2, 3)
    HALT = (99, 0)
    IN = (3, 1)
    OUT = (4, 1)
    JUMP_TRUE = (5, 2)
    JUMP_FALSE = (6, 2)
    LESS_THAN = (7, 3)
    EQUALS = (8, 3)
    UDATE_REL_BASE = (9, 1)

    def __init__(self, code, args):
        self.code = code
        self.args = args

    @classmethod
    def from_code(cls, code):
        return next((op for op in cls if op.code == code), OP.HALT)


def parse_program(text: str) -> dict[int, int]:
    parts = [int(p.strip()) for p in text.replace("\n", ",").split(",")]
    return {i: v for i, v in enumerate(parts)}


def parse_op(op: int) -> Tuple[OP, List[int]]:
    code = op % 100
    op = op // 100
    modes = [0, 0, 0, 0]
    for i in range(3):
        modes[i] = op % 10
        op = op // 10

    return (OP.from_code(code), modes)


def run_intcode(
    mem: dict[int, int],
    in_f: Callable[[], int] = (lambda: int(input("input> "))),
    out_f: Callable[[int], None] = print,
) -> None:
    print(mem)
    ip = 0
    rel_base = 0

    def next_mem() -> int:
        nonlocal ip
        val = mem.get(ip, 0)
        ip += 1
        return val

    def param_read(mode, val) -> int:
        if mode == 0:
            return mem.get(val, 0)
        elif mode == 1:
            return val
        elif mode == 2:
            return mem.get(rel_base + val, 0)
        else:
            raise RuntimeError(f"Invalid parameter mode: {mode}")

    def addr_write(mode, val) -> int:
        if mode == 2:
            return rel_base + val
        else:
            return val

    while True:
        try:
            op, modes = parse_op(next_mem())
        except IndexError:
            raise RuntimeError(f"Instruction pointer out of bounds: ip={ip}")

        args = [next_mem() for _ in range(op.args)]

        if op == OP.ADD:
            a = param_read(modes[0], args[0])
            b = param_read(modes[1], args[1])
            out_addr = addr_write(modes[2], args[2])
            mem[out_addr] = a + b

        elif op == OP.MULT:
            a = param_read(modes[0], args[0])
            b = param_read(modes[1], args[1])
            out_addr = addr_write(modes[2], args[2])
            mem[out_addr] = a * b

        elif op == OP.IN:
            val = in_f()
            out_addr = addr_write(modes[0], args[0])
            mem[out_addr] = val

        elif op == OP.OUT:
            val = param_read(modes[0], args[0])
            out_f(val)

        elif op == OP.JUMP_TRUE:
            val = param_read(modes[0], args[0])
            if val != 0:
                ip = param_read(modes[1], args[1])

        elif op == OP.JUMP_FALSE:
            val = param_read(modes[0], args[0])
            if val == 0:
                ip = param_read(modes[1], args[1])

        elif op == OP.LESS_THAN:
            a = param_read(modes[0], args[0])
            b = param_read(modes[1], args[1])
            out_addr = addr_write(modes[2], args[2])
            mem[out_addr] = 1 if a < b else 0

        elif op == OP.EQUALS:
            a = param_read(modes[0], args[0])
            b = param_read(modes[1], args[1])
            out_addr = addr_write(modes[2], args[2])
            mem[out_addr] = 1 if a == b else 0

        elif op == OP.UDATE_REL_BASE:
            rel_base = rel_base + param_read(modes[0], args[0])

        elif op == OP.HALT:
            return

        else:
            raise RuntimeError(f"Unexpected op {op} at ip={ip}")


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


class SparseGrid:
    def __init__(self) -> None:
        self._map: Dict[Tuple[int, int], int] = {}

    def get(self, y: int, x: int) -> int:
        return self._map.get((y, x), 0)

    def set(self, y: int, x: int, value: int) -> None:
        if value == 0:
            self._map.pop((y, x), None)
        else:
            self._map[(y, x)] = value

    def bounds_square(self) -> Tuple[int, int, int, int]:
        if not self._map:
            return (0, 0, 0, 0)
        ys = [y for (y, _), v in self._map.items() if v != 0]
        xs = [x for (_, x), v in self._map.items() if v != 0]
        min_y, max_y = min(ys), max(ys)
        min_x, max_x = min(xs), max(xs)

        h = max_y - min_y + 1
        w = max_x - min_x + 1
        side = max(h, w)
        return (min_y, min_y + side - 1, min_x, min_x + side - 1)

    def render(self) -> None:
        min_y, max_y, min_x, max_x = self.bounds_square()
        ys = range(min_y - 1, max_y + 1)

        for y in ys:
            row = "".join(str(self.get(x, y)) for x in range(min_x - 1, max_x + 1))
            print(row)
        print("")


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

        if (
            loc not in visited
            and grid.get(loc[0], loc[1]) != 1
            and loc[0] >= bounds[0]
            and loc[0] <= bounds[1]
            and loc[1] >= bounds[2]
            and loc[1] <= bounds[3]
        ):
            if loc == end:
                return path[0]
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


def main() -> int:

    input_file = pathlib.Path(__file__).parent / "input.txt"

    grid: SparseGrid = SparseGrid()
    tried: SparseGrid = SparseGrid()

    movement_op = 0
    ret_code = 0
    robot_xy = (0, 0)
    o2_xy = (None, None)
    grid.set(robot_xy[0], robot_xy[1], 3)
    min_path_size = 100

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

    def write_in() -> int:
        nonlocal movement_op
        # todo: do something smarter plz
        available_ops = [
            # first ones we haven't tried
            op
            for op in ALL_OPS
            if tried.get(*get_target_xy(robot_xy, op)) == 0
        ] or ALL_OPS

        movement_op = available_ops[random.randrange(len(available_ops))]
        return movement_op

    def read_out(val: int):
        nonlocal robot_xy
        nonlocal o2_xy
        nonlocal ret_code
        nonlocal min_path_size

        ret_code = val
        still_unfound = o2_xy == (None, None)

        target_xy = get_target_xy(robot_xy, movement_op)

        tried.set(target_xy[0], target_xy[1], 1)
        if val == RET_WALL:
            grid.set(target_xy[0], target_xy[1], 1)
        elif val == RET_MOVE or val == RET_MOVE_O2:
            grid.set(robot_xy[0], robot_xy[1], grid.get(robot_xy[0], robot_xy[1]) - 3)
            grid.set(target_xy[0], target_xy[1], grid.get(robot_xy[0], robot_xy[1]) + 3)
            robot_xy = target_xy
            if val == RET_MOVE_O2:
                grid.set(target_xy[0], target_xy[1], 5)
                if still_unfound:
                    print(f"FOUND O2!!! {target_xy} {grid.get(*target_xy)}")
                    # grid.render()
                    o2_xy = target_xy
                    path = find_path(grid, (0, 0), o2_xy)
                    # print(path)
                    if min_path_size > len(path):
                        min_path_size = len(path)
                        print(f"length: {min_path_size}")
            else:
                if still_unfound:
                    grid.render()

        else:
            raise RuntimeError(f"unknown response val {val}")

    with open(input_file, "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        run_intcode(mem, write_in, read_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
