"""Mock executor implementation for dry-run executions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .base import Executor
from .models import ExecutionReport, OrderRequest


class MockExecutor(Executor):
    """Simulate order execution and persist audit logs."""

    def __init__(self, audit_log_path: Optional[Path] = None) -> None:
        default_path = os.getenv("AUDIT_LOG_PATH", "audit_logs.jsonl")
        self.audit_log_path = Path(audit_log_path or default_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def execute(self, order: OrderRequest, price: float) -> ExecutionReport:
        report = ExecutionReport(
            order=order,
            status="filled",
            filled_quantity=order.quantity,
            average_price=price,
        )
        self._write_audit_log(report)
        return report

    def _write_audit_log(self, report: ExecutionReport) -> None:
        payload = {
            "symbol": report.order.symbol,
            "side": report.order.side,
            "quantity": report.filled_quantity,
            "average_price": report.average_price,
            "status": report.status,
            "timestamp": report.timestamp.isoformat(),
            "metadata": report.order.metadata,
        }
        with self.audit_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
