"""Base executor class definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ExecutionReport, OrderRequest


class Executor(ABC):
    @abstractmethod
    def execute(self, order: OrderRequest, price: float) -> ExecutionReport:
        """Execute an order and return an execution report."""
        raise NotImplementedError
