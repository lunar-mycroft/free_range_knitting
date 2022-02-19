from __future__ import annotations

from dataclasses import dataclass
from itertools import cycle
from random import Random
from typing import Iterable, Iterator, Type
from uuid import UUID

import httpx
from pydantic import BaseModel


@dataclass
class Stitch:
    size: int

    @staticmethod
    def join_alike(stitches: Iterable[Stitch]):
        a, b, *rest, c, d = stitches  # a bit space inefficient, but it does the job

        if (cls := type(a)) == type(b):
            yield cls(a.size+b.size)
        else:
            yield from [a, b]
        yield from rest
        if (cls := type(c)) == type(d):
            yield cls(c.size+d.size)
        else:
            yield from [c, d]


class Knit(Stitch):
    def __str__(self):
        return f"K{self.size}"


class Purl(Stitch):
    def __str__(self):
        return f"P{self.size}"


@dataclass
class Pattern:
    stitches: list[list[Stitch]]

    def visualize(self) -> Iterator[str]:
        for line in self.stitches:
            yield "".join(
                ("#" if isinstance(s, Purl) else "_")*s.size for s in line
            )

    def pattern(self) -> Iterator[str]:
        for i, line in enumerate(self.stitches[::-1]):
            yield ", ".join(list(map(str, line))[::(-1)**i])


@dataclass
class RandomGenerator:
    rng: Random
    min_continuous: int
    max_continuous: int
    p_max: float

    def rand_number(self):
        p = self.p_max**(1/(self.max_continuous-self.min_continuous))
        for res in range(self.min_continuous, self.max_continuous+1):
            if self.rng.random() > p:
                break
        return res

    def rand_row(self, width: int):
        order = [Knit, Purl]
        self.rng.shuffle(order)
        stitches: Iterator[Type[Stitch]] = cycle(order)
        used = 0

        while used < width:
            n = min(self.rand_number(), width-used)
            used += n
            yield next(stitches)(n)


class DishClothGenerator(BaseModel):
    width: int = 33
    height: int = 33
    max_continuous: int = 24
    min_continuous: int = 2
    num_max: float = 1.0
    border: int = 3

    def __call__(self, seed: UUID) -> Pattern:
        random = RandomGenerator(
            Random(seed),
            self.min_continuous,
            self.max_continuous,
            self.num_max/self.height
        )
        ends = [[Knit(self.width + 2 * self.border)]] * self.border
        middle = [
            list(Stitch.join_alike(self._to_row(random.rand_row(self.width))))
            for _ in range(self.height-2*self.border)
        ]

        return Pattern(ends + middle + ends)

    def _to_row(self, stitches: Iterable[Stitch])->Iterator[Stitch]:
        yield Knit(self.border)
        yield from stitches
        yield Knit(self.border)

    def url(self, url: httpx.URL) -> httpx.URL:
        default_dict = type(self)().dict()
        our_dict = self.dict()
        for key, value in default_dict.items():
            if value==our_dict[key]:
                our_dict.pop(key)
        return url.copy_merge_params(our_dict)