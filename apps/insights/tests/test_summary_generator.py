import pandas as pd
from apps.insights.services.openai.summary_generator import generate_summary


def test_summary_generator():
    """
    Tests the generate_summary function with a Pandas statistical summary.
    """
    # Create a sample DataFrame
    data = {
        "Sales": [100, 200, 300, 400, 500],
        "Profit": [20, 50, 70, 100, 150],
        "Expenses": [80, 150, 230, 300, 350],
    }
    df = pd.DataFrame(data)

    # Generate the Pandas statistical summary
    pandas_summary = df.describe().to_string()

    print("\nPandas Statistical Summary:")
    print(pandas_summary)

    # Generate the LLM-based summary
    try:
        result = generate_summary(pandas_summary)

        print("\nGenerated LLM Summary:")
        print(result.dataset_summary)

        print("\nKey Metrics:")
        for metric in result.key_metrics:
            print(f"- {metric.name}: {metric.value} ({metric.description})")

    except Exception as e:
        print(f"Error during summary generation: {e}")


if __name__ == "__main__":
    test_summary_generator()
