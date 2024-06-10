"""
Module containing the REST endpoints
"""

from __future__ import annotations

from typing import Optional, List, Literal, Sequence, Any, Dict

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from fia_api.core.responses import (
    PreScriptResponse,
    ReductionResponse,
    ReductionWithRunsResponse,
    CountResponse,
    RunResponse,
    InstrumentResponse,
)
from fia_api.core.services.instrument import (
    get_all_instruments,
    get_specification_by_instrument_name,
    update_specification_for_instrument,
)
from fia_api.core.services.reduction import (
    get_reductions_by_instrument,
    get_reduction_by_id,
    get_reductions_by_experiment_number,
    count_reductions,
    count_reductions_by_instrument,
)
from fia_api.core.services.run import get_total_run_count, get_run_count_by_instrument, get_runs_by_instrument
from fia_api.scripts.acquisition import (
    get_script_for_reduction,
    write_script_locally,
    get_script_by_sha,
)
from fia_api.scripts.pre_script import PreScript

ROUTER = APIRouter()


@ROUTER.get("/healthz", tags=["k8s"])
async def get() -> Literal["ok"]:
    """Health Check endpoint."""
    return "ok"


@ROUTER.get("/instrument/{instrument}/script", tags=["scripts"])
async def get_pre_script(
    instrument: str,
    background_tasks: BackgroundTasks,
    reduction_id: Optional[int] = None,
) -> PreScriptResponse:
    """
    Script URI - Not intended for calling
    \f
    :param instrument: the instrument
    :param background_tasks: handled by fastapi
    :param reduction_id: optional query parameter of runfile, used to apply transform
    :return: ScriptResponse
    """
    script = PreScript(value="")
    # This will never be returned from the api, but is necessary for the background task to run
    try:
        script = get_script_for_reduction(instrument, reduction_id)
        return script.to_response()
    finally:
        background_tasks.add_task(write_script_locally, script, instrument)
        # write the script after to not slow down request


@ROUTER.get("/instrument/{instrument}/script/sha/{sha}", tags=["scripts"])
async def get_pre_script_by_sha(instrument: str, sha: str, reduction_id: Optional[int] = None) -> PreScriptResponse:
    """
    Given an instrument and the commit sha of a script, obtain the pre script. Optionally providing a reduction id to
    transform the script
    \f
    :param instrument: The instrument
    :param sha: The commit sha of the script
    :param reduction_id: The reduction id to apply transforms
    :return:
    """
    return get_script_by_sha(instrument, sha, reduction_id).to_response()


OrderField = Literal[
    "reduction_start",
    "reduction_end",
    "reduction_state",
    "id",
    "run_start",
    "run_end",
    "reduction_outputs",
    "experiment_number",
    "experiment_title",
    "filename",
]


@ROUTER.get("/instrument/{instrument}/reductions", tags=["reductions"])
async def get_reductions_for_instrument(
    instrument: str,
    limit: int = 0,
    offset: int = 0,
    order_by: OrderField = "reduction_start",
    order_direction: Literal["asc", "desc"] = "desc",
    include_runs: bool = False,
) -> List[ReductionResponse] | List[ReductionWithRunsResponse]:
    """
    Retrieve a list of reductions for a given instrument.
    \f
    :param instrument: the name of the instrument
    :param limit: optional limit for the number of reductions returned (default is 0, which can be interpreted as
    no limit)
    :param offset: optional offset for the list of reductions (default is 0)
    :param order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"]
    :param order_direction: Literal["asc", "desc"]
    :param include_runs: bool
    :return: List of ReductionResponse objects
    """
    instrument = instrument.upper()
    reductions = get_reductions_by_instrument(
        instrument, limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
    )
    if include_runs:
        return [ReductionWithRunsResponse.from_reduction(r) for r in reductions]
    return [ReductionResponse.from_reduction(r) for r in reductions]


@ROUTER.get("/instrument/{instrument}/reductions/count", tags=["reductions"])
async def count_reductions_for_instrument(
    instrument: str,
) -> CountResponse:
    """
    Count reductions for a given instrument.
    \f
    :param instrument: the name of the instrument
    :return: List of ReductionResponse objects
    """
    instrument = instrument.upper()
    return CountResponse(count=count_reductions_by_instrument(instrument))


@ROUTER.get("/reduction/{reduction_id}", tags=["reductions"])
async def get_reduction(reduction_id: int) -> ReductionWithRunsResponse:
    """
    Retrieve a reduction with nested run data, by iD.
    \f
    :param reduction_id: the unique identifier of the reduction
    :return: ReductionWithRunsResponse object
    """
    reduction = get_reduction_by_id(reduction_id)
    return ReductionWithRunsResponse.from_reduction(reduction)


@ROUTER.get("/experiment/{experiment_number}/reductions", tags=["reductions"])
async def get_reductions_for_experiment(
    experiment_number: int,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"] = "reduction_start",
    order_direction: Literal["desc", "asc"] = "desc",
) -> List[ReductionResponse]:
    """
    Retrieve a list of reductions associated with a specific experiment number.
    \f
    :param experiment_number: the unique experiment number:
    :param limit: Number of results to limit to
    :param offset: Number of results to offset by
    :param order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"]
    :param order_direction: Literal["asc", "desc"]
    :return: List of ReductionResponse objects
    """
    return [
        ReductionResponse.from_reduction(r)
        for r in get_reductions_by_experiment_number(
            experiment_number, limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
        )
    ]


@ROUTER.get("/reductions/count", tags=["reductions"])
async def count_all_reductions() -> CountResponse:
    """
    Count all reductions
    \f
    :return: CountResponse containing the count
    """
    return CountResponse(count=count_reductions())


@ROUTER.get("/runs/count", tags=["runs"])
async def count_all_runs() -> CountResponse:
    """
    Count all runs
    \f
    :return: Count response containing the count
    """
    return CountResponse(count=get_total_run_count())


@ROUTER.get("/instrument/{instrument}/runs/count", tags=["runs"])
async def count_runs_for_instrument(instrument: str) -> CountResponse:
    """
    Count the total runs for the given instrument
    \f
    :param instrument: The instrument
    :return: The count response
    """
    instrument = instrument.upper()
    return CountResponse(count=get_run_count_by_instrument(instrument))


@ROUTER.get("/instrument/{instrument}/runs", tags=["runs"])
async def get_runs_for_instrument(
    instrument: str,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal[
        "experiment_number", "run_end", "run_start", "good_frames", "raw_frames", "id", "filename"
    ] = "run_start",
    order_direction: Literal["asc", "desc"] = "desc",
) -> List[RunResponse]:
    """
    Get all runs for the given instrument
    \f
    :param instrument: The instrument
    :param limit: Optional limit to apply
    :param offset: Optional offset to apply
    :param order_by: Optional field to order by
    :param order_direction: Optional direction to order by
    :return: List of RunResponses
    """
    return [
        RunResponse.from_run(run)
        for run in get_runs_by_instrument(
            instrument.upper(), limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
        )
    ]


@ROUTER.get("/instrument", tags=["instrument"])
async def get_instruments() -> Sequence[InstrumentResponse]:
    """
    Get all instruments
    \f
    :return: Sequence of instruments
    """
    return [
        InstrumentResponse(instrument_name=instrument.instrument_name, specification=instrument.specification)
        for instrument in get_all_instruments()
    ]


@ROUTER.get("/instrument/{instrument_name}/specification", tags=["instrument"])
async def get_instrument_specification(instrument_name: str) -> Dict[str, Any]:
    """
    Return the specification for the given instrument
    \f
    :param instrument_name: The instrument
    :return: The specificaiton
    """
    return get_specification_by_instrument_name(instrument_name.upper())


@ROUTER.put("/instrument/{instrument_name}/specification", tags=["instrument"])
async def update_instrument_specification(instrument_name: str, specification: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace the current specification with the given specification for the given instrument
    \f
    :param instrument_name: The instrument name
    :param specification: The new specification
    :return: The new specification
    """
    update_specification_for_instrument(instrument_name.upper(), specification)
    return specification
