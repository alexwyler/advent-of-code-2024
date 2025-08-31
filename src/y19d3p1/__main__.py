import sys
from functools import lru_cache
from itertools import product
from typing import Callable, List, Tuple

from functional import seq

VALID_OPS = (1, 2)


def parse_program(text: str) -> List[int]:
    parts = [p.strip() for p in text.replace("\n", ",").split(",")]
    return [int(p) for p in parts if p != ""]

@lru_cache
def load_mem_cached() -> List[int]:
    with open("input.txt", "r", encoding="utf-8") as f:
        mem = parse_program(f.read())
        return mem

def run_intcode(nvMem: Tuple[Tuple[int, int], List[int]]) -> Tuple[Tuple[int, int], List[int]]:
    mem = nvMem[1]
    nv = nvMem[0]
    ip = 0
    while True:
        try:
            op = mem[ip]
        except IndexError:
            raise RuntimeError(f"Instruction pointer out of bounds: ip={ip}")
        if op == 99:
            break
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

    return (nv, mem)

def map_tuple_2[A, B, C](f: Callable[[B], C]) -> Callable[[Tuple[A, B]], Tuple[A, C]]:
    def g(ab: Tuple[A, B]) -> Tuple[A, C]:
        return (ab[0], f(ab[1]))

    return g


def find_nv() -> Tuple[int, int]:
    nv = (
        seq(product(range(100), repeat=2))
        .map(lambda nv: (nv, load_mem_cached))
        .map(map_tuple_2(lambda mem: [mem[0], nv[0], nv[1], *mem[3:]]))
        .map(map_tuple_2(run_intcode))
        .filter(map_tuple_2(lambda mem: mem[0] == 19690720))
        .map(lambda nvMem: nvMem[0])
        .first()
    )

    return nv


def find_nv_2() -> Tuple[int, int]:
    nv = (
        seq(product(range(100), repeat=2))
        .map(lambda nv: (nv[0], nv[1]))
        .map(lambda nv: (nv, load_mem_cached))
        .map(
            lambda nvMem: (lambda nv, mem: (nv, [mem[0], nv[0], nv[1], *mem[3:]]))(
                nvMem[0], nvMem[1])
        )
        .map(lambda nvMem: (lambda nv, mem: (nv, run_intcode(mem)))(nvMem[0], nvMem[1]))
        .filter(lambda nvMem: (mem := nvMem[1]) and mem[0] == 19690720)
        .map(lambda nvMem: nvMem[0])
        .first()
    )

    return nv


if __name__ == "__main__":
    raise SystemExit(main())
