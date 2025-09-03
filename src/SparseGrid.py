from typing import Dict, Tuple


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
