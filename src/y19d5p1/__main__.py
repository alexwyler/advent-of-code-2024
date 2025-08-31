import pathlib
from enum import Enum
from typing import Callable, List, Tuple

from functional import seq


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

    def __init__(self, code, args):
        self.code = code
        self.args = args

    @classmethod
    def from_code(cls, code):
        return next((op for op in cls if op.code == code), OP.HALT)


def parse_program(text: str) -> List[int]:
    parts = [p.strip() for p in text.replace("\n", ",").split(",")]
    return [int(p) for p in parts if p != ""]


def parse_op(op: int) -> Tuple[OP, List[int]]:
    code = op % 100
    op = op // 100
    modes = [0, 0, 0, 0]
    for i in range(3):
        modes[i] = op % 10
        op = op // 10

    return (OP.from_code(code), modes)


def run_intcode(
    mem: List[int],
    in_f: Callable[[], int] = (lambda: int(input("input> "))),
    out_f: Callable[[int], None] = print,
) -> None:
    ip = 0

    def next_mem() -> int:
        nonlocal ip
        val = mem[ip]
        ip += 1
        return val

    def param_value(mode, val) -> int:
        return val if mode else mem[val]

    while True:
        try:
            op, modes = parse_op(next_mem())
        except IndexError:
            raise RuntimeError(f"Instruction pointer out of bounds: ip={ip}")

        args = [next_mem() for _ in range(op.args)]

        if op == OP.ADD:
            a = param_value(modes[0], args[0])
            b = param_value(modes[1], args[1])
            out_addr = args[2]
            mem[out_addr] = a + b

        elif op == OP.MULT:
            a = param_value(modes[0], args[0])
            b = param_value(modes[1], args[1])
            out_addr = args[2]
            mem[out_addr] = a * b

        elif op == OP.IN:
            val = in_f()
            out_addr = args[0]
            mem[out_addr] = val

        elif op == OP.OUT:
            val = param_value(modes[0], args[0])
            out_f(val)

        elif op == OP.JUMP_TRUE:
            val = param_value(modes[0], args[0])
            if val != 0:
                ip = param_value(modes[1], args[1])

        elif op == OP.JUMP_FALSE:
            val = param_value(modes[0], args[0])
            if val == 0:
                ip = param_value(modes[1], args[1])

        elif op == OP.LESS_THAN:
            a = param_value(modes[0], args[0])
            b = param_value(modes[1], args[1])
            out_addr = args[2]
            mem[out_addr] = 1 if a < b else 0

        elif op == OP.EQUALS:
            a = param_value(modes[0], args[0])
            b = param_value(modes[1], args[1])
            out_addr = args[2]
            mem[out_addr] = 1 if a == b else 0

        elif op == OP.HALT:
            return

        else:
            raise RuntimeError(f"Unexpected op {op} at ip={ip}")


def main() -> int:

    input_file = pathlib.Path(__file__).parent / "input.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        run_intcode(mem, (lambda: int(input("input> "))), print)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
