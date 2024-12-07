import time
from apps.insights.services.csv.csv_processor import CSVProcessor

# Run: (25.617ms)
# docker-compose exec django sh
# python manage.py shell
# exec(open("apps/insights/benchmarks/benchmark_pandas_csv_processor.py").read())

START_DATE = "2024-01-01"


def benchmark_pandas_csv_processor(start_date: str):
    """
    Benchmarks the Pandas CSVProcessor with a given start date.
    """
    processor = CSVProcessor()
    total_start_time = time.perf_counter()  # Start total timing

    # Timing load
    start_time = time.perf_counter()
    processor.load()
    end_time = time.perf_counter()
    print(f"Load time: {(end_time - start_time) * 1000:.3f} ms")

    # Timing validate
    start_time = time.perf_counter()
    processor.validate()
    end_time = time.perf_counter()
    print(f"Validation time: {(end_time - start_time) * 1000:.3f} ms")

    # Timing clean
    start_time = time.perf_counter()
    processor.clean()
    end_time = time.perf_counter()
    print(f"Cleaning time: {(end_time - start_time) * 1000:.3f} ms")

    # Timing filter
    start_time = time.perf_counter()
    filtered_df = processor.filter(start_date)
    end_time = time.perf_counter()
    print(f"Filtering time: {(end_time - start_time) * 1000:.3f} ms")

    # Ensure filtered data is not empty
    if filtered_df.empty:
        print("Filtered DataFrame is empty. Ensure the start date is valid.")

    # Timing generate_overview
    start_time = time.perf_counter()
    processor.df = filtered_df  # Update processor's df with filtered data
    end_time = time.perf_counter()
    print(f"Overview generation time: {(end_time - start_time) * 1000:.3f} ms")

    # Total time
    total_end_time = time.perf_counter()
    print(f"Total processing time: {(total_end_time - total_start_time) * 1000:.3f} ms")

    print("Benchmark complete.")


if __name__ == "__main__":
    benchmark_pandas_csv_processor(START_DATE)
