from dataclasses import dataclass
from random import random, shuffle
from itertools import cycle


@dataclass
class Pattern:
    size: int = 33
    max_continuous: int = 24
    odds_max: float = 1 / 32

    def rand_lengths(self):
        used = 0
        while self.size > used:
            n = min(self.rand_length(), self.size - used)
            yield n
            used += n

    def rand_length(self) -> int:
        p = self.odds_max ** (1 / (self.max_continuous - 2))
        for res in range(2, self.max_continuous):
            if random() > p:
                break
        return res

    def make_row(self):
        stitch_order = list('kp')  # needs to be a list for shuffle
        shuffle(stitch_order)  # Do we start by knitting or pearling?
        return ",".join(
            f"{s}{n}" for (s, n) in zip(
                cycle(stitch_order),
                self.rand_lengths()
            )
        )

    def print_pattern(self):
        for _ in range(self.size):
            print(self.make_row(), sep='')


Pattern().print_pattern()