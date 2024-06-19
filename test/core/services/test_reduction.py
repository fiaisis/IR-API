"""
Tests for reduction service
"""

from unittest.mock import Mock, patch

import pytest

from fia_api.core.exceptions import MissingRecordError
from fia_api.core.services.reduction import (
    count_reductions,
    count_reductions_by_instrument,
    get_reduction_by_id,
    get_reductions_by_instrument,
)


@patch("fia_api.core.services.reduction._REPO")
@patch("fia_api.core.services.reduction.ReductionSpecification")
def test_get_reductions_by_instrument(mock_spec_class, mock_repo):
    """
    Test that get_reductions by instrument makes correct repo call
    :param mock_repo: Mocked Repo class
    :return: None
    """
    spec = mock_spec_class.return_value
    get_reductions_by_instrument("test", limit=5, offset=6)

    mock_repo.find.assert_called_once_with(spec.by_instrument("test", limit=5, offset=6))


@patch("fia_api.core.services.reduction._REPO")
def test_get_reduction_by_id_reduction_exists(mock_repo):
    """
    Test that correct repo call and return is made
    :param mock_repo: Mocked Repo
    :return:
    """
    expected_reduction = Mock()
    mock_repo.find_one.return_value = expected_reduction
    reduction = get_reduction_by_id(1)
    assert reduction == expected_reduction


@patch("fia_api.core.services.reduction._REPO")
def test_get_reduction_by_id_not_found_raises(mock_repo):
    """
    Test MissingRecordError raised when repo returns None
    :param mock_repo: Mocked Repo
    :return: None
    """
    mock_repo.find_one.return_value = None
    with pytest.raises(MissingRecordError):
        get_reduction_by_id(1)


@patch("fia_api.core.services.reduction._REPO")
def test_count_reductions(mock_repo):
    """
    Test count is called
    :return: None
    """
    count_reductions()
    mock_repo.count.assert_called_once()


@patch("fia_api.core.services.reduction._REPO")
@patch("fia_api.core.services.reduction.ReductionSpecification")
def test_count_reductions_by_instrument(mock_spec_class, mock_repo):
    """
    Test count by instrument
    :param mock_repo: mock repo fixture
    :return: None
    """
    spec = mock_spec_class.return_value
    count_reductions_by_instrument("TEST")
    mock_repo.count.assert_called_once_with(spec.by_instrument("TEST"))
