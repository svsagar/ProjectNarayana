"""Location UX behaviour of the browser client.

The real src/narayana/interface/web/app.js is executed in a minimal fake DOM
under Node (tests/interface/web_harness.js) with controllable timers and a
mocked fetch, so debounce, stale-data clearing and candidate selection are
verified as behaviour rather than asserted against source text.

If Node is not installed the behavioural tests skip; the asset-integrity tests
still run everywhere.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.narayana.interface.http import app

WEB_DIR = Path(__file__).resolve().parents[2] / "src" / "narayana" / "interface" / "web"
HARNESS = Path(__file__).with_name("web_harness.js")
NODE = shutil.which("node")

client = TestClient(app)

requires_node = pytest.mark.skipif(
    NODE is None, reason="Node.js is not available to run the browser harness."
)


@pytest.fixture(scope="module")
def observations() -> dict:
    """Run every harness scenario once and share the results."""
    completed = subprocess.run(
        [NODE, str(HARNESS)],
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    for name, result in data.items():
        assert "harness_error" not in result, f"{name}: {result.get('harness_error')}"
    return data


# --------------------------------------------------------------------------
# The served assets are the files in this workspace
# --------------------------------------------------------------------------

@pytest.mark.parametrize("route,filename", [
    ("/", "index.html"),
    ("/static/app.js", "app.js"),
    ("/static/styles.css", "styles.css"),
])
def test_server_serves_the_current_workspace_assets(route, filename):
    response = client.get(route)
    assert response.status_code == 200
    assert response.text == (WEB_DIR / filename).read_text(encoding="utf-8")


def test_place_field_is_wired_for_automatic_resolution():
    """Guards the specific defect: the place field had no input listener."""
    source = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    assert 'placeInput.addEventListener("input"' in source


# --------------------------------------------------------------------------
# Debounced automatic resolution
# --------------------------------------------------------------------------

@requires_node
def test_typing_does_not_resolve_on_every_keystroke(observations):
    result = observations["debounce"]
    assert result["requests_during_typing"] == 0


@requires_node
def test_resolution_fires_once_after_the_user_pauses(observations):
    result = observations["debounce"]
    assert result["requests_after_pause"] == 1
    assert result["resolved_query"] == "Kochi"
    assert result["geo"]["latitude"] == "9.93988"
    assert result["geo"]["longitude"] == "76.26022"
    assert result["geo"]["timezone"] == "Asia/Kolkata"


@requires_node
def test_resolving_status_is_shown_and_replaced_by_the_result(observations):
    assert "Location resolved" in observations["debounce"]["status"]


# --------------------------------------------------------------------------
# Critical stale-data rule
# --------------------------------------------------------------------------

@requires_node
def test_changing_the_place_clears_resolved_coordinates_immediately(observations):
    result = observations["stale_cleared_immediately"]

    # Kottayam resolved first.
    assert result["after_first_resolution"]["latitude"] == "9.59273"
    assert result["after_first_resolution"]["longitude"] == "76.52213"

    # The instant the text becomes "Cochin" -- before any response arrives --
    # the Kottayam coordinates are gone.
    edited = result["immediately_after_edit"]
    assert edited["place_name"] == "Cochin"
    assert edited["latitude"] == ""
    assert edited["longitude"] == ""
    assert edited["timezone"] == ""

    # A fresh resolution is queued rather than fired immediately.
    assert result["pending_timers"] == 1


@requires_node
def test_a_superseded_request_is_aborted(observations):
    result = observations["previous_request_is_aborted"]
    assert result["aborts_before_retype"] == 0
    assert result["aborts_after_retype"] == 1
    assert result["requests"] == ["Kochi", "Kottayam"]
    # The newer place wins.
    assert result["geo"]["latitude"] == "9.59273"
    assert result["geo"]["place_name"] == "Kottayam, Kerala, India"


# --------------------------------------------------------------------------
# Candidate handling
# --------------------------------------------------------------------------

@requires_node
def test_single_candidate_populates_all_three_fields(observations):
    result = observations["single_candidate_autopopulates"]
    assert result["candidates_shown"] == 0
    assert result["geo"]["latitude"] == "9.93988"
    assert result["geo"]["longitude"] == "76.26022"
    assert result["geo"]["timezone"] == "Asia/Kolkata"
    assert result["geo"]["place_name"] == "Kochi, Kerala, India"
    assert "is-resolved" in result["status_class"]


@requires_node
def test_multiple_candidates_are_never_auto_selected(observations):
    result = observations["multiple_candidates_need_selection"]
    assert result["candidates_shown"] == 2
    assert result["candidate_labels"] == [
        "London, England, United Kingdom",
        "London, Ontario, Canada",
    ]
    before = result["geo_before_selection"]
    assert before["latitude"] == ""
    assert before["longitude"] == ""
    assert before["timezone"] == ""


@requires_node
def test_selecting_a_candidate_populates_that_candidate(observations):
    after = observations["multiple_candidates_need_selection"]["geo_after_selection"]
    assert after["latitude"] == "42.98339"
    assert after["longitude"] == "-81.23304"
    assert after["timezone"] == "America/Toronto"
    assert after["place_name"] == "London, Ontario, Canada"


# --------------------------------------------------------------------------
# Failure paths
# --------------------------------------------------------------------------

@requires_node
def test_no_result_leaves_the_fields_empty_with_guidance(observations):
    result = observations["no_result_leaves_fields_empty"]
    assert result["geo"]["latitude"] == ""
    assert result["geo"]["longitude"] == ""
    assert result["geo"]["timezone"] == ""
    assert "No matching location found" in result["status"]


@requires_node
def test_service_failure_leaves_fields_empty_and_permits_manual_entry(observations):
    result = observations["service_failure_allows_manual_entry"]
    assert result["geo_after_failure"]["latitude"] == ""
    assert "manually" in result["status"].lower()

    # Fields stay usable, and typed values stick.
    assert result["latitude_disabled"] is False
    assert result["timezone_disabled"] is False
    assert result["manual_geo"]["latitude"] == "9.93988"
    assert result["manual_geo"]["timezone"] == "Asia/Kolkata"


# --------------------------------------------------------------------------
# Enter key and manual override
# --------------------------------------------------------------------------

@requires_node
def test_enter_resolves_immediately_without_submitting(observations):
    result = observations["enter_resolves_immediately"]
    assert result["requests_before_enter"] == 0
    assert result["requests_after_enter"] == 1
    assert result["default_prevented"] is True
    assert result["geo"]["latitude"] == "9.93988"


@requires_node
def test_manual_override_after_resolution_wins(observations):
    result = observations["manual_override_is_authoritative"]
    assert result["resolved_geo"]["latitude"] == "9.93988"
    assert result["final_geo"]["latitude"] == "19.07283"
    assert result["final_geo"]["longitude"] == "72.88261"
    assert "Manually adjusted" in result["status"]


@requires_node
def test_overridden_values_are_what_the_chart_endpoint_receives(observations):
    """The final field values -- not the resolved ones -- drive the calculation."""
    final = observations["manual_override_is_authoritative"]["final_geo"]

    served = client.post("/api/v1/chart", json={
        "birth_date": "1978-08-17",
        "birth_time": "10:10:00",
        "timezone": final["timezone"],
        "latitude": float(final["latitude"]),
        "longitude": float(final["longitude"]),
        "place_name": final["place_name"],
    }).json()

    assert served["input"]["latitude"] == 19.07283
    assert served["input"]["longitude"] == 72.88261
    assert served["input"]["timezone"] == "Asia/Kolkata"
    # place_name is descriptive metadata and does not steer the calculation.
    assert served["input"]["place_name"] == "Kochi, Kerala, India"
