from .money import allocate


def refund_lines(lines, refund):
    """Returns the negative adjustment for each line, adding up to -refund."""
    parts = allocate(-refund, [cents for _, cents in lines])
    return [(name, part) for (name, _), part in zip(lines, parts)]
