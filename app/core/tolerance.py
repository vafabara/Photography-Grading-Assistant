"""
Automatic tolerance calculation (spec section 6).

The professor never sets Tolerance directly. For each Rule, the
system widens the Minimum/Maximum range by a percentage of the
range's own width, capped at MAX_TOLERANCE_PERCENT. A value inside
that widened range but outside the original range is YELLOW;
anything further out is RED.

Because the widening is a percentage of each Rule's own width, two
different factors (e.g. ISO 200-600 vs. Aperture f/4-f/8) each get a
tolerance proportional to their own range — not one shared constant.
"""

MAX_TOLERANCE_PERCENT = 0.15


def compute_tolerance(rule):
    """
    Return the tolerance amount (in the factor's own units) for a
    single Rule — an absolute value added/subtracted from the range,
    not a percentage.
    """

    range_width = rule.maximum - rule.minimum

    if range_width <= 0:
        # A zero-width rule (min == max) would otherwise get zero
        # tolerance, making it impossible to ever score YELLOW.
        # Fall back to a tolerance based on the value itself.
        reference = rule.maximum if rule.maximum else 1
        return abs(reference) * MAX_TOLERANCE_PERCENT

    return range_width * MAX_TOLERANCE_PERCENT


def tolerance_bounds(rule):
    """
    Return the (lower, upper) bounds of the tolerance zone — the
    widened range that separates YELLOW from RED.
    """

    tolerance = compute_tolerance(rule)

    return (
        rule.minimum - tolerance,
        rule.maximum + tolerance,
    )
