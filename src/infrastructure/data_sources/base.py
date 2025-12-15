from __future__ import annotations
"""Abstract data source interface.

Implementations should yield normalized dict rows suitable for
insertion into the repository without further transformation.
"""
from abc import ABC, abstractmethod
from typing import Iterable, Dict


class DataSource(ABC):
    @abstractmethod
    def load(self) -> Iterable[Dict]:  # yield normalized dict rows
        """Stream normalized records. Implementations may perform cleaning."""
        raise NotImplementedError
