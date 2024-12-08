# apps/insights/benchmarks/benchmark_comparison_generator.py
import time
import json
import traceback
from apps.insights.services.openai.comparison_generator import generate_comparison

# Path to save the LLM output
OUTPUT_FILE = "apps/insights/benchmarks/generated_comparison_output.json"


def benchmark_comparison_generator():
    """
    Benchmarks the `generate_comparison` function using hardcoded summaries.
    Measures and prints the execution time.
    Saves the LLM structured output to a file.
    """
    # Hardcoded summaries for benchmarking
    summary1 = """
    The dataset covers a 7-day period and encapsulates web analytics data, reflecting user engagement on a website.
    Key metrics include the total number of sessions, users, new users, pageviews, as well as specific engagement metrics 
    such as pages per session, average session duration, bounce rate, conversion rate, transactions, and revenue.
    Overall, the dataset provides an overview of user interaction, revealing patterns in website traffic and user activity
    over the specified time frame.

    Key Metrics:
    - Average Sessions: 1543.43
    - Average Users: 1265.14
    - Average New Users: 427.29
    - Average Pageviews: 6225.86
    - Pages per Session: 4.01
    - Average Session Duration: 163.1
    - Bounce Rate: 0.2
    - Conversion Rate: 0.028
    - Average Transactions: 34.14
    - Average Revenue: 1622.53
    """

    summary2 = """
    The dataset provides a statistical overview of a website's user interaction over a period of seven days in January 2024,
    from the 8th to the 14th. It includes metrics related to sessions, users, new users, pageviews, pages per session, 
    average session duration, bounce rate, conversion rate, transactions, and revenue. The average daily sessions were 
    approximately 1683, with an average of about 1238 users and around 424 new users daily. The website generated an average 
    of 6891.71 pageviews per day, with each session lasting around 154 seconds on average. The average bounce rate was about 
    16.06%, and the conversion rate stood at about 4.25%. The site recorded an average of 49 transactions per day, resulting
    in a daily revenue averaging $2087.17.

    Key Metrics:
    - Average Sessions: 1682.57
    - Average Users: 1237.86
    - Average New Users: 424.14
    - Average Pageviews: 6891.71
    - Pages per Session: 4.07
    - Average Session Duration: 153.88
    - Bounce Rate: 0.1606
    - Conversion Rate: 0.0425
    - Average Transactions: 49.43
    - Average Revenue: 2087.17
    """

    print("\n=== Benchmarking `generate_comparison` ===")
    print("Input Summaries:")
    print(f"Summary 1:\n{summary1}")
    print(f"\nSummary 2:\n{summary2}")

    # Measure the execution time of `generate_comparison`
    start_time = time.perf_counter()
    try:
        print("\nCalling `generate_comparison`...")
        response = generate_comparison(summary1, summary2)
        end_time = time.perf_counter()

        # Print execution time
        print(f"\nExecution Time: {(end_time - start_time) * 1000:.3f} ms")
        print("\n=== Generated Comparison ===")

        # Convert response to a dictionary
        response_dict = response.model_dump()

        # Save the structured output to a JSON file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
            json.dump(response_dict, output_file, indent=4)
        print(f"Structured output saved to {OUTPUT_FILE}")

    except Exception as e:
        print("\nError during benchmark:")
        traceback.print_exc()


if __name__ == "__main__":
    benchmark_comparison_generator()
