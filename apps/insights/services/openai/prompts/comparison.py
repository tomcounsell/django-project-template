COMPARISON_PROMPT = """
You are a data analyst tasked with comparing two dataset summaries. Here are the summaries:

{summary1} is the current week.

{summary2} is the week prior.

Think step-by-step to explain your reasoning for the comparison, and include this explanation in the field `chain_of_thought`.

Please provide the comparison in the following JSON format:

{{
    "comparison_summary": "A comprehensive summary of differences and similarities between the current week and previous week, including notable trends and observations.
    Ensure that:
        - Maximum length is 180 words.
        - Refer to the summaries as 'this week' and 'the previous week' in your summary.
        - Use precise verbal descriptions to describe the observed differences or trends between the current week and the previous week data in your summary.
        - Mention up to three salient numerical values in your summary.
        - Commas should be used in numerical values to separate thousands in your summary.",
    "key_metrics_comparison": [
        {{
            "name": "Name of Metric",
            "value1": Value from current week,
            "value2": Value from previous week,
            "description": "Description of observed difference or trend between the previous week and the current week, including specific figures and percentages where appropriate."
        }}
        // Repeat for each key metric
    ],
    "chain_of_thought": "Step-by-step reasoning explaining how the comparison summary and key metrics were derived."
}}

Ensure that:
- Numerical values for value1 and value2 are provided as numbers (not strings) for each metric.
- The key_metrics_comparison includes the following metrics in this order:
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
- The description for each metric explains the difference or trend observed between the current week and one week prior, using precise figures (e.g., differences, statistics, percentages).
- Refer to the summaries as "this week" and "the previous week" in your descriptions.
"""
