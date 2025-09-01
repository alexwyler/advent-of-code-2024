import pathlib
from encodings.punycode import T
from enum import Enum
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


EMPTY = 0
WALL = 1
BLOCK = 2
PADDLE = 3
BALL = 4


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
        ys = range(min_y, max_y + 1)

        for y in ys:
            row = "".join(str(self.get(x, y)) for x in range(min_x, max_x + 1))
            print(row)
        print("")


def main() -> int:

    input_file = pathlib.Path(__file__).parent / "input.txt"

    screen: SparseGrid = SparseGrid()

    def write_in() -> int:
        if ball_x_y[0] > paddle_x_y[0]:
            return 1
        elif ball_x_y[0] < paddle_x_y[0]:
            return -1
        else:
            return 0

    out_index = 0
    draw_x = 0
    draw_y = 0
    tile = 0
    ball_x_y = (0, 0)
    paddle_x_y = (0, 0)

    def read_out(val: int):
        nonlocal out_index
        nonlocal draw_x
        nonlocal draw_y
        nonlocal tile
        nonlocal ball_x_y
        nonlocal paddle_x_y
        if out_index == 0:
            draw_x = val
        elif out_index == 1:
            draw_y = val
        elif out_index == 2:
            tile = val
            if (draw_x, draw_y) == (-1, 0):
                print(f"SCORE: {val}")
            else:
                if tile == BALL:
                    ball_x_y = (draw_x, draw_y)

                if tile == PADDLE:
                    paddle_x_y = (draw_x, draw_y)
                screen.set(draw_x, draw_y, tile)
                screen.render()
        else:
            raise RuntimeError("More than 2 outputs since last input")
        out_index = (out_index + 1) % 3

    with open(input_file, "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        mem[0] = 2  # quarters
        print(mem)

        run_intcode(mem, write_in, read_out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
