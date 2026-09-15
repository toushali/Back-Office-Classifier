from pathlib import Path

import pytest

from classifier import extract_text, classify_document, route_document, process_document

SAMPLE_DIR = Path(__file__).parent / "sample"


def test_extract_text_returns_nonempty_string():
    text = extract_text(SAMPLE_DIR / "invoice_1.pdf")
    assert isinstance(text, str)
    assert len(text) > 0


def test_route_document_known_labels():
    assert route_document("Invoice") == "Accounts Payable"
    assert route_document("Purchase Order") == "Procurement"
    assert route_document("Contract") == "Legal"


def test_route_document_unknown_label_falls_back():
    assert route_document("Gibberish") == "Manual Review"


@pytest.mark.parametrize(
    "filename,expected_label",
    [
        ("invoice_1.pdf", "Invoice"),
        ("purchase_order_1.pdf", "Purchase Order"),
        ("contract_1.pdf", "Contract"),
    ],
)
def test_classify_document_matches_expected_label(filename, expected_label):
    text = extract_text(SAMPLE_DIR / filename)
    result = classify_document(text)
    assert result["label"] == expected_label
    assert 0.0 <= result["confidence"] <= 1.0


def test_process_document_full_pipeline():
    result = process_document(str(SAMPLE_DIR / "invoice_1.pdf"))
    assert result["label"] == "Invoice"
    assert result["routing_department"] == "Accounts Payable"
    assert "key_fields" in result
    assert result["source_file"].endswith("invoice_1.pdf")