import random

"""Quelle: https://stackoverflow.com/questions/25200220/generate-a-random-derangement-of-a-list"""


def swap(xs, a, b):
    xs[a], xs[b] = xs[b], xs[a]


def derange(xs):
    for a in range(1, len(xs)):
        b = random.choice(range(0, a))
        swap(xs, a, b)
    return xs
