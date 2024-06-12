"""
responses module contains api response definitions
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from fia_api.core.model import Reduction, ReductionState, Run, Script
from fia_api.core.utility import filter_script_for_tokens

if TYPE_CHECKING:
    from datetime import datetime


class CountResponse(BaseModel):
    """Count response shows the count of a model"""

    count: int


class ScriptResponse(BaseModel):
    """
    ScriptResponse returns from the API a script value
    """

    value: str

    @staticmethod
    def from_script(script: Script) -> ScriptResponse:
        """
        Given a script return a ScriptResponse, filtered for tokens.
        :param script: The script to convert
        :return: The ScriptResponse object
        """
        script_to_send = filter_script_for_tokens(script.script)
        return ScriptResponse(value=script_to_send)


class PreScriptResponse(BaseModel):
    """
    PreScript response returns from the API a PreScript
    """

    value: str
    is_latest: bool
    sha: str | None = None


class RunResponse(BaseModel):
    """
    Run Response object
    """

    filename: str
    experiment_number: int
    title: str
    users: str
    run_start: datetime
    run_end: datetime
    good_frames: int
    raw_frames: int
    instrument_name: str

    @staticmethod
    def from_run(run: Run) -> RunResponse:
        """
        Given a run return a RunResponse object
        :param run: The run to convert
        :return: The RunResponse object
        """
        return RunResponse(
            filename=run.filename,
            experiment_number=run.experiment_number,
            title=run.title,
            users=run.users,
            run_start=run.run_start,
            run_end=run.run_end,
            good_frames=run.good_frames,
            raw_frames=run.raw_frames,
            instrument_name=run.instrument.instrument_name,
        )


class ReductionResponse(BaseModel):
    """
    ReductionResponse object that does not contain the related runs
    """

    id: int
    reduction_start: datetime | None
    reduction_end: datetime | None
    reduction_state: ReductionState
    reduction_status_message: str | None
    reduction_inputs: Any
    reduction_outputs: str | None
    stacktrace: str | None
    script: ScriptResponse | None

    @staticmethod
    def from_reduction(reduction: Reduction) -> ReductionResponse:
        """
        Given a reduction return a ReductionResponse
        :param reduction: The Reduction to convert
        :return: The ReductionResponse object
        """
        script = ScriptResponse.from_script(reduction.script) if isinstance(reduction.script, Script) else None
        return ReductionResponse(
            reduction_start=reduction.reduction_start,
            reduction_end=reduction.reduction_end,
            reduction_state=reduction.reduction_state,
            reduction_status_message=reduction.reduction_status_message,
            reduction_inputs=reduction.reduction_inputs,
            reduction_outputs=reduction.reduction_outputs,
            script=script,
            stacktrace=reduction.stacktrace,
            id=reduction.id,
        )


class ReductionWithRunsResponse(ReductionResponse):
    """
    ReductionWithRunsResponse is the same as a reduction response, with the runs nested
    """

    runs: list[RunResponse]

    @staticmethod
    def from_reduction(reduction: Reduction) -> ReductionWithRunsResponse:
        """
        Given a Reduction, return the ReductionWithRunsResponse
        :param reduction: The Reduction to convert
        :return: The ReductionWithRunsResponse Object
        """
        script = ScriptResponse.from_script(reduction.script) if isinstance(reduction.script, Script) else None
        return ReductionWithRunsResponse(
            reduction_start=reduction.reduction_start,
            reduction_end=reduction.reduction_end,
            reduction_state=reduction.reduction_state,
            reduction_status_message=reduction.reduction_status_message,
            reduction_inputs=reduction.reduction_inputs,
            reduction_outputs=reduction.reduction_outputs,
            script=script,
            id=reduction.id,
            stacktrace=reduction.stacktrace,
            runs=[RunResponse.from_run(run) for run in reduction.runs],
        )
