from array import array
# from collections import Counter
from collections import namedtuple


def kevin(str1, str2, max_substitutions, max_insertions):
    """check if it is possible to transform str1 into str2 given limitations

    The limitations are the maximum allowed number of new characters inserted
    and the maximum allowed number of character substitutions.
    """
    # check simple cases which are obviously impossible
    if not len(str1) <= len(str2) <= len(str1) + max_insertions:
        return False

    # # some multi-set math to see if there are too many differing items to make
    # # transformation possible
    # c = Counter(str1)
    # c.subtract(str2)
    # if sum(map(abs, c.values())) > max_substitutions * 2 + max_insertions:
    #     return False

    scores = array('L', [0] * (len(str2) - len(str1) + 1))
    new_scores = scores[:]

    for (str1_idx, char1) in enumerate(str1):
        # make min() always take the other value in the first iteration of the
        # inner loop
        prev_score = len(str2)
        for (n_insertions, char2) in enumerate(
                str2[str1_idx:len(str2)-len(str1)+str1_idx+1]
        ):
            new_scores[n_insertions] = prev_score = min(
                scores[n_insertions] + (0 if char1 == char2 else 1),
                prev_score
            )

        # swap scores <-> new_scores
        scores, new_scores = new_scores, scores

    return min(scores) <= max_substitutions


def super_kevin(str1, str2, max_substitutions, max_insertions, max_deletions):
    """check if it is possible to transform str1 into str2 given limitations

    The limitations are the maximum allowed number of new characters inserted,
    the maximum allowed number of character substitutions and the maximum
    allowed number of character deletions.
    """
    # quick answers for simple scenarios
    if max_deletions == 0:
        if max_insertions == 0:
            return len(str1) == len(str2) and \
                   sum(a != b for a, b in zip(str1, str2)) <= max_substitutions
        else:
            return kevin(str1, str2, max_substitutions, max_insertions)
    elif max_insertions == 0:
        return kevin(str2, str1, max_substitutions, max_deletions)
    else:
        candidates = _super_kevin(str1, str2, max_substitutions,
                                  max_insertions, max_deletions)
        return len(candidates) > 0


SuperKevinCandidate = namedtuple('Candidate', ['subs', 'dels', 'ins'])


def _super_kevin(str1, str2, max_substitutions, max_insertions, max_deletions):
    """internal function implementing the actual algorithm for super_kevin()"""
    candidates = [[SuperKevinCandidate(subs=0, dels=str1_idx, ins=0)]
                  for str1_idx in range(max_deletions+1)] + \
                 [[] for _i in range(len(str1) - max_deletions)]

    for str2_idx, str2_char in enumerate(str2):
        new_candidates = [[c._replace(ins=c.ins+1) for c in candidates[0]]] + [[] for _i in range(len(str1))]
        for str1_idx, str1_char in enumerate(str1):
            for candidate in candidates[str1_idx+1]:
                if candidate.ins < max_insertions:
                    new_candidates[str1_idx+1].append(
                        candidate._replace(ins=candidate.ins + 1)
                    )

            subs_delta = (0 if str1_char == str2_char else 1)
            for candidate in candidates[str1_idx]:
                if candidate.subs + subs_delta <= max_substitutions:
                    new_candidates[str1_idx+1].append(
                        candidate._replace(subs=candidate.subs + subs_delta)
                    )

            for candidate in new_candidates[str1_idx]:
                if candidate.dels < max_deletions:
                    new_candidates[str1_idx+1].append(
                        candidate._replace(dels=candidate.dels + 1)
                    )

        candidates = new_candidates
        # pp(candidates)

    return candidates[-1]
