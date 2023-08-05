from hypothesis.internal.utils.tracker import Tracker


def multi_minimize(
    values,
    interesting,
    simplify,
    complexity,
):
    """
    param:
        values: a collection of values of any type
        interesting: a function that takes values and returns a set of
            hashable features saying why they might be interesting.
        simplify: a function that takes a value and returns a list of possibly
            simpler values
        complexity: a function such that if complexity(x) < complexity(y) then
            x is simpler than y

    Returns a list of values that are in some sense "minimal" and "interesting"
    according to these. There's no real specification as to what these means.
    It's really a best effort game.
    """

    considered = Tracker()

    def better(x, y):
        if complexity(y) < complexity(x):
            return y
        return x

    def update_minteresting(f, v):
        if f not in minteresting:
            minteresting[f] = v
            return False
        else:
            minteresting[f] = better(minteresting[f], v)
            return True

    minteresting = {}

    it = iter(values)
    stack = []
    while True:
        if stack:
            v = stack.pop()
        else:
            try:
                v = next(it)
            except StopIteration:
                break

        if considered.track(v) > 1:
            continue

        updated_features = [
            f
            for f in interesting(v)
            if update_minteresting(f, v)
        ]
        if updated_features:
            for s in simplify(v):
                stack.push(s)
        yield minteresting
