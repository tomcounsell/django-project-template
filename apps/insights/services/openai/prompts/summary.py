# apps/insights/services/openai/prompts/summary.py

SUMMARY_PROMPT_TEMPLATE = """
You are a data analyst tasked with summarizing a dataset. The following is a statistical summary of the dataset:

{statistical_summary}

Think step-by-step to explain how you arrived at your summary and key metrics, and include this reasoning in the field `chain_of_thought`.

Please provide the summary in the following JSON format:

{{
    "dataset_summary": "A concise, insightful summary highlighting significant findings, trends, or patterns observed in the data. Mention any notable data or anomalies in the key metrics, providing context by referencing the actual values and what they indicate about user behavior or performance metrics.",
    "key_metrics": [
        {{
            "name": "Name of Metric",
            "value": Numeric value
        }}
        // Repeat for each key metric
    ],
    "chain_of_thought": "Step-by-step reasoning explaining how the summary and key metrics were derived."
}}

Ensure that:
- All numeric values are provided as numbers (not strings).
- The key_metrics include the following metrics in this order:
    - "Average Sessions"
    - "Average Users"
    - "Average New Users"
    - "Average Pageviews"
    - "Pages per Session"
    - "Average Session Duration"
    - "Bounce Rate"
    - "Conversion Rate"
    - "Average Transactions"
    - "Average Revenue"
- Focus on delivering specific insights derived from the data and explain your reasoning.
- Avoid generic statements or repeating information without analysis.
"""
