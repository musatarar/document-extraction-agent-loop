import pytest

import functions
from agent import DocumentTotals


def make_claim(claim_number, status, paid, reserve, incurred):
    return {
        "claim_number": claim_number,
        "status": status,
        "total_paid": paid,
        "total_reserve": reserve,
        "total_incurred": incurred,
    }


CLAIMS = [
    make_claim("WC-001", "Open", 1200.50, 800.00, 2000.50),
    make_claim("WC-002", "Closed", 5000.00, 0.00, 5000.00),
    make_claim("WC-003", "Reopened", 0.00, 2500.25, 2500.25),
]

MATCHING_TOTALS = DocumentTotals(
    total_claims=3,
    total_paid=6200.50,
    total_reserve=3300.25,
    total_incurred=9500.75,
)


@pytest.fixture
def document_totals(monkeypatch):
    """Hardcode what the document totals call returns."""
    def set_totals(totals):
        monkeypatch.setattr(functions, "get_document_totals", lambda file_path: totals)
    return set_totals


def test_matching_totals_pass(document_totals):
    document_totals(MATCHING_TOTALS)
    result = functions.validate_totals("doc.pdf", CLAIMS)

    assert result["passed"] is True
    assert result["mismatches"] == []
    assert result["duplicate_claim_numbers"] == []
    assert result["open_claim_count"] == 2
    assert all(c["status"] == "match" for c in result["checks"].values())


def test_missing_claim_fails_count_and_amounts(document_totals):
    document_totals(MATCHING_TOTALS)
    result = functions.validate_totals("doc.pdf", CLAIMS[:2])

    assert result["passed"] is False
    assert result["mismatches"] == ["total_claims", "total_reserve", "total_incurred"]
    assert result["checks"]["total_claims"]["difference"] == -1
    assert result["checks"]["total_reserve"]["difference"] == -2500.25
    assert result["checks"]["total_paid"]["status"] == "match"


def test_amount_within_tolerance_passes(document_totals):
    document_totals(MATCHING_TOTALS.model_copy(update={"total_paid": 6200.51}))
    result = functions.validate_totals("doc.pdf", CLAIMS)

    assert result["passed"] is True
    assert result["checks"]["total_paid"]["status"] == "match"


def test_amount_outside_tolerance_fails(document_totals):
    document_totals(MATCHING_TOTALS.model_copy(update={"total_paid": 6201.00}))
    result = functions.validate_totals("doc.pdf", CLAIMS)

    assert result["passed"] is False
    assert result["mismatches"] == ["total_paid"]
    assert result["checks"]["total_paid"]["difference"] == -0.5


def test_duplicate_claim_numbers_fail(document_totals):
    claims = CLAIMS + [make_claim("WC-002", "Closed", 0.00, 0.00, 0.00)]
    document_totals(MATCHING_TOTALS.model_copy(update={"total_claims": 4}))
    result = functions.validate_totals("doc.pdf", claims)

    assert result["passed"] is False
    assert result["mismatches"] == []
    assert result["duplicate_claim_numbers"] == ["WC-002"]


def test_missing_document_totals_are_unverified(document_totals):
    document_totals(DocumentTotals(total_claims=3))
    result = functions.validate_totals("doc.pdf", CLAIMS)

    assert result["passed"] is True
    assert result["checks"]["total_claims"]["status"] == "match"
    for field in ("total_paid", "total_reserve", "total_incurred"):
        assert result["checks"][field]["status"] == "unverified"


def test_outstanding_used_when_reserve_missing(document_totals):
    document_totals(MATCHING_TOTALS.model_copy(update={"total_reserve": None, "total_outstanding": 3300.25}))
    result = functions.validate_totals("doc.pdf", CLAIMS)

    assert result["checks"]["total_reserve"]["status"] == "match"
    assert result["checks"]["total_reserve"]["document"] == 3300.25


def test_null_amounts_count_as_zero(document_totals):
    claims = [make_claim("WC-001", "Open", None, None, None)]
    document_totals(DocumentTotals(total_claims=1, total_paid=0, total_reserve=0, total_incurred=0))
    result = functions.validate_totals("doc.pdf", claims)

    assert result["passed"] is True
