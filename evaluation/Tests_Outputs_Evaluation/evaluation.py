import pprint

LOG_FILE = "test_log.txt"

results = []

def f1_score(expected: set, actual: set):
    tp = len(expected & actual)
    fp = len(actual - expected)
    fn = len(expected - actual)

    if tp == 0 and fp == 0 and fn == 0:
        return 1.0

    if tp == 0:
        return 0.0

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    return 2 * precision * recall / (precision + recall)


def evaluate_state(expected, actual):
    f1_scores = {}

    for key in expected:
        exp = expected[key]
        act = actual.get(key, set())

        f1_scores[key] = f1_score(exp, act)

    overall = sum(f1_scores.values()) / len(f1_scores)
    results.append(overall)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n============================\n")

        if expected == actual:
            f.write("TEST PASSED\n")
        else:
            f.write("TEST FAILED\n")

        f.write("\nEXPECTED:\n")
        f.write(pprint.pformat(expected) + "\n")

        f.write("\nACTUAL:\n")
        f.write(pprint.pformat(actual) + "\n")

        f.write("\nF1 DETAILS:\n")
        for key, score in f1_scores.items():
            f.write(f"{key}_f1 = {score:.3f}\n")

        f.write("\nOVERALL F1:\n")
        formula = " + ".join([f"{v:.3f}" for v in f1_scores.values()])
        f.write(f"({formula}) / {len(f1_scores)} = {overall:.3f}\n")

    return overall
