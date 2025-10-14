"""Live executor with strict safety gate."""

from __future__ import annotations

import json
import os
from typing import Optional

from .base import Executor
from .models import ExecutionReport, OrderRequest


class LiveExecutionNotApproved(RuntimeError):
    """Raised when live execution gating requirements are not met."""


class LiveExecutor(Executor):
    def __init__(self, broker_api_key: Optional[str] = None) -> None:
        self.broker_api_key = broker_api_key or os.getenv("BROKER_API_KEY")

    def execute(self, order: OrderRequest, price: float) -> ExecutionReport:  # pragma: no cover - live path disabled
        if os.getenv("EXECUTE_LIVE") != "true":
            raise LiveExecutionNotApproved("Live execution requires EXECUTE_LIVE=true")
        approval_blob = os.getenv("APPROVAL_JSON")
        if not approval_blob:
            raise LiveExecutionNotApproved("Live execution requires APPROVAL_JSON with human approval")
        try:
            json.loads(approval_blob)
        except json.JSONDecodeError as exc:
            raise LiveExecutionNotApproved("APPROVAL_JSON is not valid JSON") from exc
        raise NotImplementedError("Live execution is disabled in this environment")
