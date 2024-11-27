import logging
from django.db import transaction
from apps.insights.models.summary import Summary
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.services.openai.schemas import ComparisonOutput

logger = logging.getLogger(__name__)


def save_comparison_to_database(
    summary1_id: int, summary2_id: int, comparison_result: ComparisonOutput
):
    """
    Saves the LLM comparison result to the database.

    Args:
        summary1_id (int): ID of the first summary (Week 1).
        summary2_id (int): ID of the second summary (Week 2).
        comparison_result (ComparisonOutput): The structured comparison result from LLM.
    """
    try:
        with transaction.atomic():
            # Fetch the summaries
            summary1 = Summary.objects.get(id=summary1_id)
            summary2 = Summary.objects.get(id=summary2_id)

            logging.info(
                f"Saving comparison for summaries {summary1_id} and {summary2_id}..."
            )

            # Create the Comparison object
            comparison = Comparison.objects.create(
                summary1=summary1,
                summary2=summary2,
                comparison_summary=comparison_result.comparison_summary,
            )

            # Create KeyMetricComparison objects
            for metric in comparison_result.key_metrics_comparison:
                KeyMetricComparison.objects.create(
                    comparison=comparison,
                    name=metric.name,
                    value1=metric.value1,
                    value2=metric.value2,
                    description=metric.description,
                )

            logging.info(
                f"Comparison saved successfully for summaries {summary1_id} and {summary2_id}."
            )

    except Summary.DoesNotExist as e:
        logging.error(f"Summary not found: {e}")
        raise ValueError(f"Summary not found: {e}")
    except Exception as e:
        logging.error(f"Failed to save comparison to the database: {e}")
        raise
