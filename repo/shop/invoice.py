from .money import allocate


def discounted_lines(lines, discount):
    """lines is a list of (name, cents). Returns the lines after the discount is shared out."""
    shares = allocate(discount, [cents for _, cents in lines])
    return [(name, cents - share) for (name, cents), share in zip(lines, shares)]


def invoice_total(lines, discount):
    return sum(cents for _, cents in discounted_lines(lines, discount))
