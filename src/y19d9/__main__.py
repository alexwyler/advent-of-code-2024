import pathlib
from enum import Enum
from typing import Callable, List, Tuple


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


def main() -> int:

    input_file = pathlib.Path(__file__).parent / "input.txt"

    with open(input_file, "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        run_intcode(mem, (lambda: int(input("input> "))), print)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
