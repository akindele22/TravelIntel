"""
Simple unit tests for InsightAnalyzer's grading logic.
"""
from ai_predictor import InsightAnalyzer


def test_risk_grade_boundaries():
    ia = InsightAnalyzer()
    # integer scores
    assert ia._risk_grade_from_score(1) == "A"
    assert ia._risk_grade_from_score(2) == "B"
    assert ia._risk_grade_from_score(3) == "C"
    assert ia._risk_grade_from_score(4) == "E"  # highest risk

    # fractional values check midpoints
    assert ia._risk_grade_from_score(1.5) == "B"
    assert ia._risk_grade_from_score(2.5) == "C"
    assert ia._risk_grade_from_score(3.5) == "D"

    # values outside range get clamped
    assert ia._risk_grade_from_score(0) == "A"
    assert ia._risk_grade_from_score(5) == "E"

    # None and invalid
    assert ia._risk_grade_from_score(None) == "U"
    assert ia._risk_grade_from_score("foo") == "U"


if __name__ == "__main__":
    test_risk_grade_boundaries()
    print("risk grade tests passed")
