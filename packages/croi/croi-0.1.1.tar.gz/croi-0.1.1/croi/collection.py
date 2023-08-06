import copy


def updated(left, right, join=lambda l, r: r):
    result = copy.copy(left)

    for k, v in right.iteritems():
        try:
            result[k] = join(left[k], v)
        except KeyError:
            result[k] = v

    return result
