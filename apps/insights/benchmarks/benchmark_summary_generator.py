import time
import json
from pathlib import Path
from apps.insights.services.openai.summary_generator import generate_summary

# Path to the dummy statistical overview file
TEST_DATA_FILE = Path("apps/insights/tests/data/overview_2024-01-01.json")


def benchmark_summary_generator():
    """
    Benchmarks the `generate_summary` function using dummy data.
    Measures and prints the execution time.
    """
    # Load the test data from JSON file
    with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
        statistical_overview = json.load(f)

    # Convert the overview to the string format expected by `generate_summary`
    overview_lines = []
    headers = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    for column, stats in statistical_overview.items():
        if column != "start_date":  # Exclude the start_date
            row = [f"{stats.get(header, '')}" for header in headers]
            overview_lines.append(f"{column:<20} {' '.join(row)}")
    statistical_overview_str = "\n".join(overview_lines)

    print("\n=== Benchmarking `generate_summary` ===")
    print("Input to `generate_summary`:\n")
    print(statistical_overview_str)

    # Measure the execution time of `generate_summary`
    start_time = time.perf_counter()
    try:
        response = generate_summary(statistical_overview_str)
        end_time = time.perf_counter()

        # Print execution time
        print(f"\nExecution Time: {(end_time - start_time) * 1000:.3f} ms")
        print("\n=== Generated Summary ===")
        print(response.dict())

    except Exception as e:
        print(f"Error during benchmark: {e}")


if __name__ == "__main__":
    benchmark_summary_generator()
