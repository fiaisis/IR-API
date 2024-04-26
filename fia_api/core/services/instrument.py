"""
Service Layer for instruments
"""
from typing import Sequence

from fia_api.core.model import Instrument
from fia_api.core.repositories import Repo
from fia_api.core.specifications.instrument import InstrumentSpecification

_REPO: Repo[Instrument] = Repo()


def get_all_instruments() -> Sequence[Instrument]:
    """Return all instruments"""
    return _REPO.find(InstrumentSpecification().all())


def get_specification_by_instrument_name(instrument_name: str) -> InstrumentSpecification:
    """
    Given an instrument name, return the specification for that instrument
    :param instrument_name:
    :return:
    """
    return _REPO.find_one(InstrumentSpecification().by_name(instrument_name)).specification
