from evaluation import results

LOG_FILE = "test_log.txt"

def pytest_sessionfinish(session, exitstatus):
    if not results:
        print("\nNo evaluation data.")
        return

    avg_f1 = sum(results) / len(results)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "="*40)
        f.write("\n" + f"F1 SCORE (average): {avg_f1:.4f}")
        f.write("\n" + "="*40)
        
    print("\n" + "=" * 40)
    print(f"F1 SCORE (average): {avg_f1:.4f}")
    print("=" * 40)
