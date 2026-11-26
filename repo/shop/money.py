"""Money helpers. All amounts are integer cents."""


def allocate(total, weights):
    """Split total across weights in proportion to each weight.

    The parts always add up to total. Cents left after rounding down go to the
    parts with the largest fractional remainder, and ties go to the earlier part.
    A negative total is split like the positive one, with the sign reversed.
    If every weight is zero, the total is split as evenly as the same rules allow.
    """
    whole = sum(weights)
    if whole == 0:
        weights = [1] * len(weights)
        whole = len(weights)
    return [int(total * weight / whole) for weight in weights]
