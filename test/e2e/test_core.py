"""
end-to-end tests
"""

# pylint: disable=line-too-long, wrong-import-order
from unittest.mock import patch

from starlette.testclient import TestClient

from fia_api.fia_api import app
from test.utils import FIA_FAKER_PROVIDER

client = TestClient(app)


faker = FIA_FAKER_PROVIDER


def test_get_reduction_by_id_reduction_doesnt_exist():
    """
    Test 404 for reduction not existing
    :return:
    """
    response = client.get("/reduction/123144324234234234")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


def test_get_reduction_by_id_reduction_exists():
    """
    Test reduction returned for id that exists
    :return:
    """
    response = client.get("/reduction/5001")
    assert response.status_code == 200
    assert response.json() == {
        "id": 5001,
        "reduction_end": None,
        "reduction_inputs": {
            "ei": "'auto'",
            "sam_mass": 0.0,
            "sam_rmm": 0.0,
            "monovan": 0,
            "remove_bkg": True,
            "sum_runs": False,
            "runno": 25581,
            "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
            "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
            "wbvan": 12345,
        },
        "reduction_outputs": None,
        "reduction_start": None,
        "reduction_state": "NOT_STARTED",
        "reduction_status_message": None,
        "runs": [
            {
                "experiment_number": 1820497,
                "filename": "MAR25581.nxs",
                "good_frames": 6452,
                "instrument_name": "TEST",
                "raw_frames": 8067,
                "run_end": "2019-03-22T10:18:26",
                "run_start": "2019-03-22T10:15:44",
                "title": "Whitebeam - vanadium - detector tests - vacuum bad - HT on not on all LAB",
                "users": "Wood,Guidi,Benedek,Mansson,Juranyi,Nocerino,Forslund,Matsubara",
            }
        ],
        "script": None,
    }


@patch("fia_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "fia_api/local_scripts")
def test_get_prescript_when_reduction_does_not_exist():
    """
    Test return 404 when requesting pre script from non existant reduction
    :return:
    """
    response = client.get("/instrument/mari/script?reduction_id=4324234")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


@patch("fia_api.scripts.acquisition._get_script_from_remote", side_effect=RuntimeError)
def test_unsafe_path_request_returns_400_status(_):
    """
    Test that a 400 is returned for unsafe characters in script request
    :return:
    """
    response = client.get("/instrument/mari./script")  # %2F is encoded /
    assert response.status_code == 400
    assert response.json() == {"message": "The given request contains bad characters"}


@patch("fia_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "fia_api/local_scripts")
def test_get_test_prescript_for_reduction():
    """
    Test the return of transformed test script
    :return: None
    """
    response = client.get("/instrument/test/script?reduction_id=1")
    assert response.status_code == 200
    response_object = response.json()

    assert response_object["is_latest"]
    assert (
        response_object["value"]
        == """from __future__ import print_function
from mantid.kernel import ConfigService
ConfigService.Instance()[\"network.github.api_token\"] = \"\"
# This line is inserted via test


x = 22
y = 2

for i in range(20):
    x *= y

def something() -> None:
    return

something()"""
    )


def test_get_reductions_for_experiment_number():
    """
    Test reduction returned for experiment
    :return:
    """
    response = client.get("/experiment/1820497/reductions")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5001,
            "reduction_end": None,
            "reduction_inputs": {
                "ei": "'auto'",
                "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
                "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
                "monovan": 0,
                "remove_bkg": True,
                "runno": 25581,
                "sam_mass": 0.0,
                "sam_rmm": 0.0,
                "sum_runs": False,
                "wbvan": 12345,
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "script": None,
        }
    ]


def test_get_reductions_for_experiment_number_does_not_exist():
    """
    Test empty array returned when no reduction for an experiment number
    :return:
    """
    response = client.get("/experiment/12345678/reductions")
    assert response.status_code == 200
    assert response.json() == []


def test_get_reductions_for_instrument_reductions_exist():
    """
    Test array of reductions returned for given instrument when the instrument and reductions exist
    :return: None
    """
    response = client.get("/instrument/test/reductions")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5001,
            "reduction_end": None,
            "reduction_inputs": {
                "ei": "'auto'",
                "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
                "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
                "monovan": 0,
                "remove_bkg": True,
                "runno": 25581,
                "sam_mass": 0.0,
                "sam_rmm": 0.0,
                "sum_runs": False,
                "wbvan": 12345,
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "script": None,
        }
    ]


def test_get_reductions_for_instrument_runs_included():
    """Test runs are included when requested for given instrument when instrument and reductions exist"""
    response = client.get("/instrument/test/reductions?include_runs=true")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5001,
            "reduction_end": None,
            "reduction_inputs": {
                "ei": "'auto'",
                "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
                "monovan": 0,
                "remove_bkg": True,
                "runno": 25581,
                "sam_mass": 0.0,
                "sam_rmm": 0.0,
                "sum_runs": False,
                "wbvan": 12345,
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "runs": [
                {
                    "experiment_number": 1820497,
                    "filename": "MAR25581.nxs",
                    "good_frames": 6452,
                    "instrument_name": "TEST",
                    "raw_frames": 8067,
                    "run_end": "2019-03-22T10:18:26",
                    "run_start": "2019-03-22T10:15:44",
                    "title": "Whitebeam - vanadium - detector tests - vacuum bad - HT " "on not on all LAB",
                    "users": "Wood,Guidi,Benedek,Mansson,Juranyi,Nocerino,Forslund,Matsubara",
                }
            ],
            "script": None,
        }
    ]


def test_reductions_by_instrument_no_reductions():
    """
    Test empty array returned when no reductions for instrument
    :return:
    """
    response = client.get("/instrument/foo/reductions")
    assert response.status_code == 200
    assert response.json() == []


def test_reductions_count():
    """
    Test count endpoint for all reductions
    :return:
    """
    response = client.get("/reductions/count")
    assert response.status_code == 200
    assert response.json()["count"] == 5001


def test_limit_reductions():
    """Test reductions can be limited"""
    response = client.get("/instrument/mari/reductions?limit=4")
    assert len(response.json()) == 4


def test_offset_reductions():
    """
    Test results are offset
    """
    response_one = client.get("/instrument/mari/reductions")
    response_two = client.get("/instrument/mari/reductions?offset=10")
    assert response_one.json()[0] != response_two.json()[0]


def test_limit_offset_reductions():
    """
    Test offset with limit
    """
    response_one = client.get("/instrument/mari/reductions?limit=4")
    response_two = client.get("/instrument/mari/reductions?limit=4&offset=10")

    assert len(response_two.json()) == 4
    assert response_one.json() != response_two.json()


def test_instrument_reductions_count():
    """
    Test instrument reductions count
    """
    response = client.get("/instrument/TEST/reductions/count")
    assert response.json()["count"] == 1


def test_instrument_runs_count():
    """
    Test instrument runs count
    :return:
    """
    response = client.get("/instrument/TEST/runs/count")
    assert response.json()["count"] == 1


def test_total_runs_count():
    """
    Test total runs count
    """
    response = client.get("/runs/count")
    assert response.json()["count"] == 5001


def test_get_runs_by_instrument():
    """
    Test getting runs by instrument
    :return:
    """
    response = client.get("/instrument/TEST/runs")
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "experiment_number": 1820497,
        "filename": "MAR25581.nxs",
        "good_frames": 6452,
        "instrument_name": "TEST",
        "raw_frames": 8067,
        "run_end": "2019-03-22T10:18:26",
        "run_start": "2019-03-22T10:15:44",
        "title": "Whitebeam - vanadium - detector tests - vacuum bad - HT on not on all LAB",
        "users": "Wood,Guidi,Benedek,Mansson,Juranyi,Nocerino,Forslund,Matsubara",
    }
    assert response.status_code == 200


def test_readiness_and_liveness_probes():
    """
    Test endpoint for probes
    :return: None
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.text == '"ok"'


def test_get_all_instruments():
    """
    Test all instruments returned
    :return: None
    """
    response = client.get("/instrument")
    assert response.status_code == 200
    assert response.json() == [
        {"instrument_name": "TEST", "specification": {}},
        {
            "instrument_name": "HIFI",
            "specification": {
                "at": "mbmdCddHpPzSiAPeXjOZ",
                "attack": True,
                "form": True,
                "free": "JxwnwBaRizPWYaJEEhZo",
                "include": 5189,
                "inside": True,
                "listen": "nOOUTysjkksQeNeDrlYc",
                "lose": 8662,
                "plant": 533578946923.7,
                "white": "KRFgkCLOQGICXZkpBcSm",
            },
        },
        {
            "instrument_name": "MERLIN",
            "specification": {
                "foot": False,
                "issue": True,
                "national": "ZMDtuWUIUWStyPtMzrxg",
                "party": 9659,
                "player": 193252073471.833,
                "professor": True,
                "tell": 9011,
                "within": 4140,
                "yard": 6469583751.76843,
            },
        },
        {
            "instrument_name": "CRISP",
            "specification": {
                "affect": "qWMvnaTbQYDiTYKAtskJ",
                "child": False,
                "down": "LiKJClYPAlHuDqGdpYTp",
                "industry": 64533.7155233099,
            },
        },
        {
            "instrument_name": "LET",
            "specification": {
                "example": True,
                "popular": "pSdnMntgJeRAkVAuUzgQ",
                "sell": "nYhVSSceQytZcBxguKTb",
                "six": True,
            },
        },
        {
            "instrument_name": "CHRONUS",
            "specification": {
                "exist": False,
                "head": False,
                "machine": 4471,
                "official": 33.4458643181171,
                "participant": "PHCjeCSWbXdTxNonPjpi",
                "politics": 9922,
                "receive": 6800273280538.43,
                "throw": "tSXWAgOkXzsCWvQvaCOr",
                "where": False,
            },
        },
        {"instrument_name": "INTER", "specification": {"end": "vGGWOSNQFsnKTChRzycA", "skill": False}},
        {"instrument_name": "HET", "specification": {"stop": False}},
        {
            "instrument_name": "OFFSPEC",
            "specification": {
                "benefit": -70223.8306026133,
                "part": False,
                "pressure": 883,
                "respond": True,
                "share": "jlwCnoByuftICCRLJbqJ",
            },
        },
        {
            "instrument_name": "LOQ",
            "specification": {
                "all": True,
                "film": False,
                "nature": "VPgBDZOKMsXHuyYBihJD",
                "north": "jvLcfCnfnGBedSHjSbtS",
                "party": 617300258.68013,
                "science": "pPBvqoMBagqLODxoxsMt",
                "serve": 3276,
                "theory": 6.95083928155888,
                "they": True,
                "three": True,
                "watch": 9798,
            },
        },
        {
            "instrument_name": "ZOOM",
            "specification": {
                "alone": -46717908466.2926,
                "energy": True,
                "knowledge": False,
                "seven": -86.1573618178849,
                "shake": "mOwopYrRvsqXAtppgCLi",
                "try": 5337,
            },
        },
        {
            "instrument_name": "NILE",
            "specification": {
                "board": 9511,
                "green": -273.23403846507,
                "mention": 9924,
                "price": True,
                "song": 6779,
                "story": "NLsUKcGpVfAomhnvGUdR",
                "traditional": -259483158.354832,
            },
        },
        {
            "instrument_name": "VESUVIO",
            "specification": {
                "Republican": 83466506.2549855,
                "company": "OxsAkyrZhScfTVnCctqq",
                "executive": 25.4283046849141,
                "fish": False,
                "market": -33473.1332484466,
                "network": True,
                "order": 478333769017.567,
                "southern": False,
                "ten": False,
                "there": "kegZHgJXFmYKjNADtpvB",
            },
        },
        {
            "instrument_name": "ALF",
            "specification": {"south": 7174, "suffer": 6915.3117513184, "throw": "nzxHPebRwNaxLlXUbbCW"},
        },
        {
            "instrument_name": "TOSCA",
            "specification": {
                "also": "WIEGRRErHkAzRFIWSFMV",
                "cell": -47641.4394482745,
                "fine": 9125,
                "name": "ZbnCaNeQbBkpztuHkjJp",
                "trade": "KKGBjUmEYALxOsxWFsWH",
                "with": -0.58756507572524,
            },
        },
        {
            "instrument_name": "HRPD",
            "specification": {
                "left": 789,
                "purpose": 6264,
                "range": False,
                "rich": "zuHtRCZBenfMeYYGYJeS",
                "walk": 3905,
                "wife": -74461639683.4509,
                "wonder": "NHtAPkppCiKyegFAtiwW",
            },
        },
        {
            "instrument_name": "POLREF",
            "specification": {
                "education": 195,
                "else": -699466001.810712,
                "pretty": True,
                "save": "rfACGUNgEykGXulmYrmJ",
                "system": 76695854.819194,
                "ten": "DsiOVqTsIZOcwtpQwKHA",
                "within": 7077,
            },
        },
        {"instrument_name": "EMU", "specification": {"gas": True, "interest": 5555, "population": 3290, "try": False}},
        {
            "instrument_name": "NIMROD",
            "specification": {
                "article": -1986541.17169435,
                "central": False,
                "citizen": 5166,
                "gas": 1442,
                "mother": 4201,
                "newspaper": "DJlkDTvabpFelJZrFAbr",
                "quite": 9404,
                "road": 1857,
                "sort": "seZpmBseWtLJeraUXfWP",
                "task": 9931,
            },
        },
        {
            "instrument_name": "LARMOR",
            "specification": {
                "bring": 5728,
                "different": 8788,
                "model": "cPSqtEVuTNhVahIctgyR",
                "personal": "bdRcogebHMJRIuGYHmdW",
                "where": 46298.6643995838,
            },
        },
        {
            "instrument_name": "SANS2D",
            "specification": {
                "computer": "MrhnsoyhgnkPBkwTECuk",
                "deep": False,
                "improve": True,
                "indicate": True,
                "key": False,
                "once": True,
                "say": "hIbvvhFICWShkLuMjphz",
                "suggest": -5.21319909211595,
                "system": -83402346725502.1,
            },
        },
        {"instrument_name": "CHIPIR", "specification": {"notice": 6626}},
        {"instrument_name": "OSIRIS", "specification": {"particularly": -5.41145308203559, "white": 3543}},
        {
            "instrument_name": "SURF",
            "specification": {
                "area": 4385,
                "article": "SGmkAgVKQtWgLnagkNtz",
                "collection": "EdTDeuADpnsXcXTapMPE",
                "four": False,
                "present": 1692,
                "station": "eMSRjjASusmIENZrccFU",
                "them": "HIVASYNvofRgDxclQCWV",
            },
        },
        {"instrument_name": "MARI", "specification": {"call": False, "now": False, "term": False}},
        {"instrument_name": "INES", "specification": {"particularly": -83433072.9805075}},
        {
            "instrument_name": "POLARIS",
            "specification": {
                "act": -36184.8304433321,
                "cause": False,
                "note": 470.854828913736,
                "question": False,
                "teacher": 82.9329268436538,
                "wide": -7150354.1664076,
            },
        },
        {
            "instrument_name": "SXD",
            "specification": {
                "attorney": 603611.624630889,
                "herself": False,
                "just": -10572249544532.8,
                "policy": "vTvsrntKNmPNuoOeKVXv",
                "stand": 1619,
                "store": 4627,
                "street": True,
                "treatment": "bBfrWNbtdUeCrVCVVshE",
            },
        },
        {
            "instrument_name": "MUSR",
            "specification": {
                "eye": 7859,
                "field": False,
                "kitchen": "dkhLfiOfHjawXclvcHWM",
                "lead": "OJeuIpAVgSfuVkBvUZpz",
                "rock": 4.39233171420508,
                "sister": -96215447570.6965,
            },
        },
        {
            "instrument_name": "GEM",
            "specification": {
                "building": 222924497.683724,
                "lot": True,
                "nor": "RaIefUcmZvgimMfVtYVp",
                "organization": True,
                "wish": False,
            },
        },
        {
            "instrument_name": "IMAT",
            "specification": {
                "card": -16366237521.395,
                "community": 83456628376.8749,
                "gas": "XBEbYmnihkqNRxSSisvg",
                "left": 9347,
                "prevent": "DapJLHdtPwJNqgLsCrMD",
                "when": "HtkaoFTRAZyRvMZpiGBs",
                "where": -4364879366782.48,
            },
        },
        {
            "instrument_name": "ENGINX",
            "specification": {
                "big": "giBnrAnrfmXOLzEOqvtZ",
                "exactly": False,
                "hundred": True,
                "represent": 8.711785453109,
                "third": 2048,
                "work": 1436949884546.34,
            },
        },
        {
            "instrument_name": "WISH",
            "specification": {
                "PM": "RNHflFHYWwOcFAipcTlI",
                "brother": 67.8826215722,
                "final": 2892,
                "official": "PThRhcorExPIgkMgXQlo",
                "past": "BraakkpCnmkUmCxrvajH",
                "race": 3577,
                "take": True,
                "wrong": False,
            },
        },
        {"instrument_name": "PEARL", "specification": {"stuff": True, "time": -6.20429445757731}},
        {
            "instrument_name": "ARGUS",
            "specification": {
                "age": 2762.32221869268,
                "discuss": -91973778293.2834,
                "during": 318104.305113796,
                "early": 2.17013638446512,
                "figure": 2682.48933658041,
                "hair": False,
                "machine": True,
                "research": -9.4861272855624,
                "sort": False,
                "with": 480.33519422558,
            },
        },
        {
            "instrument_name": "MAPS",
            "specification": {"baby": 135, "she": False, "teach": -80124.43351582, "though": -899617208433.3},
        },
        {
            "instrument_name": "SANDALS",
            "specification": {
                "agree": "XauGMVBuaPZVIrmOWXjE",
                "bad": 662,
                "boy": -85.5075856528676,
                "cover": "mOgHuDHyYmaXqovEZKqB",
                "read": 7002,
                "successful": 2527,
                "yeah": 8258,
            },
        },
        {
            "instrument_name": "IRIS",
            "specification": {
                "again": -817754255.260494,
                "audience": False,
                "available": "uJFkkUndRBtAMiHLQoFm",
                "color": 7400,
                "community": True,
                "hear": -286859867665.887,
                "level": 500,
                "movement": "GiYxVLFnBhhLsNmLLpfu",
                "realize": 4239,
                "see": 970855799376.76,
                "young": "UlbKQYFrRgKeuztimQyE",
            },
        },
    ]


def test_get_instrument_specification():
    """
    Test correct spec for instrument returned
    :return:
    """

    response = client.get("/instrument/het/specification")
    assert response.status_code == 200
    assert response.json() == {"stop": False}
