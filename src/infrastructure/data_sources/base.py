from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Dict


class DataSource(ABC):
    @abstractmethod
    def load(self) -> Iterable[Dict]:  # yield normalized dict rows
        raise NotImplementedError
