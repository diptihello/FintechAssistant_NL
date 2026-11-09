"""
Unit tests for Query Classifier.
"""

from src.guardrails.classifier import QueryClassifier, QueryType


def test_classify_advisory_invest():
    classifier = QueryClassifier()
    assert classifier.classify("Should I invest in HDFC Small Cap Fund?") == QueryType.ADVISORY


def test_classify_advisory_compare():
    classifier = QueryClassifier()
    assert classifier.classify("Compare HDFC Small Cap vs Large Cap fund") == QueryType.ADVISORY


def test_classify_advisory_best():
    classifier = QueryClassifier()
    assert classifier.classify("Which is the best fund to get maximum returns?") == QueryType.ADVISORY


def test_classify_factual_expense_ratio():
    classifier = QueryClassifier()
    assert classifier.classify("What is the expense ratio of HDFC Small Cap Fund?") == QueryType.FACTUAL


def test_classify_factual_exit_load():
    classifier = QueryClassifier()
    assert classifier.classify("What is the exit load for HDFC Large Cap Fund?") == QueryType.FACTUAL


def test_classify_pii():
    classifier = QueryClassifier()
    assert classifier.classify("My PAN is ABCDE1234F, what is my balance?") == QueryType.PII_DETECTED


def test_classify_out_of_scope():
    classifier = QueryClassifier()
    assert classifier.classify("What is the weather in Mumbai today?") == QueryType.OUT_OF_SCOPE

