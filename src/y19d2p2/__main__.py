from typing import List

from functional import seq

VALID_OPS = (1, 2)


def parse_program(text: str) -> List[int]:
    parts = [p.strip() for p in text.replace("\n", ",").split(",")]
    return [int(p) for p in parts if p != ""]


def run_intcode(mem: List[int]) -> None:
    ip = 0
    while True:
        try:
            op = mem[ip]
        except IndexError:
            raise RuntimeError(f"Instruction pointer out of bounds: ip={ip}")
        if op == 99:
            return
        if op not in VALID_OPS:
            raise RuntimeError(f"Unknown opcode {op} at position {ip}")
        try:
            a, b, out = mem[ip + 1], mem[ip + 2], mem[ip + 3]
        except IndexError:
            raise RuntimeError(f"Incomplete instruction at ip={ip}")
        if not (0 <= a < len(mem) and 0 <= b < len(mem) and 0 <= out < len(mem)):
            raise RuntimeError(
                f"Parameter out of bounds at ip={ip}: a={a}, b={b}, out={out}, len={len(mem)}"
            )
        if op == 1:
            mem[out] = mem[a] + mem[b]
        elif op == 2:
            mem[out] = mem[a] * mem[b]
        ip += 4


def main() -> int:
    for n in range(100):
        for v in range(100):
            with open("input.txt", "r", encoding="utf-8") as f:
                mem = parse_program(f.read())

            mem[1] = n
            mem[2] = v

            run_intcode(mem)
            if mem[0] == 19690720:
                print((n, v), 100 * n + v)
                return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
