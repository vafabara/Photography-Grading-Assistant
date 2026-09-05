"""
Score calculation for the PhotoGrade Rule Engine (spec sections 4, 5,
9, 11). This is the only module that:

  - splits the System Score evenly across the active Rules
  - evaluates each Rule against a student's converted metadata
  - decides GREEN / YELLOW / RED and the resulting deduction
  - produces the final Technical Score

No CustomTkinter or GUI dependency here (spec section 8) — app.py
calls grade_student() and hands the result to the GUI to render.
"""

from dataclasses import dataclass, field

from .converters import to_comparable
from .rules import FACTORS
from .tolerance import tolerance_bounds

GREEN = "green"
YELLOW = "yellow"
RED = "red"

# Not in the original spec: a rule was defined for a factor, but this
# particular photo has no value for it (e.g. missing EXIF data). The
# spec doesn't cover this case, so as a design choice I'm treating it
# as "can't verify" with no deduction (benefit of the doubt) rather
# than an automatic RED. Flag me if you'd rather it counted as RED.
MISSING = "missing"


@dataclass
class RuleResult:
    factor: str
    value: float | None
    status: str
    rule_score: float
    deduction: float


@dataclass
class GradingResult:
    technical_score: float
    system_score: float
    rule_results: list = field(default_factory=list)


def split_score(system_score, rules):
    """
    Split `system_score` evenly across `rules` (spec section 4).
    Returns {factor: score_per_rule}. Empty dict if there are no rules.
    """

    if not rules:
        return {}

    share = system_score / len(rules)

    return {rule.factor: share for rule in rules}


def evaluate_rule(rule, raw_metadata):
    """
    Evaluate one Rule against a student's raw metadata dict (the dict
    returned by core.image.load_image / metadata.extract_metadata).

    Returns (status, comparable_value).
    """

    metadata_key = FACTORS[rule.factor]["metadata_key"]
    raw_value = raw_metadata.get(metadata_key)

    value = to_comparable(rule.factor, raw_value)

    if value is None:
        return MISSING, None

    if rule.minimum <= value <= rule.maximum:
        return GREEN, value

    lower, upper = tolerance_bounds(rule)

    if lower <= value <= upper:
        return YELLOW, value

    return RED, value


def grade_student(raw_metadata, rules, system_score):
    """
    Run the full Rule Engine over one student's metadata.

    `rules` — list of Rule objects (core.rules.Rule).
    `system_score` — points (out of 100) assigned to the system.

    Returns a GradingResult with the Technical Score and one
    RuleResult per rule, ready for the GUI to render.
    """

    scores = split_score(system_score, rules)
    rule_results = []
    total_deduction = 0.0

    for rule in rules:

        rule_score = scores[rule.factor]
        status, value = evaluate_rule(rule, raw_metadata)

        if status in (GREEN, MISSING):
            deduction = 0.0
        elif status == YELLOW:
            deduction = rule_score / 2
        else:  # RED
            deduction = rule_score

        total_deduction += deduction

        rule_results.append(
            RuleResult(
                factor=rule.factor,
                value=value,
                status=status,
                rule_score=rule_score,
                deduction=deduction,
            )
        )

    # Rounded here since this is the final result stage (spec section 11)
    technical_score = round(system_score - total_deduction, 1)

    return GradingResult(
        technical_score=technical_score,
        system_score=system_score,
        rule_results=rule_results,
    )
