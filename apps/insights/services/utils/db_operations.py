# apps/insights/services/utils/db_operations.py
import logging
from django.db import transaction, IntegrityError
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
            try:
                summary1 = Summary.objects.get(id=summary1_id)
                summary2 = Summary.objects.get(id=summary2_id)
                logger.info(
                    f"Found summaries {summary1_id} and {summary2_id} for comparison."
                )
            except Summary.DoesNotExist as e:
                logger.error(f"Summary not found: {e}")
                raise ValueError(f"Summary not found: {e}")

            # Create the Comparison object
            try:
                comparison = Comparison.objects.create(
                    summary1=summary1,
                    summary2=summary2,
                    comparison_summary=comparison_result.comparison_summary,
                )
                logger.info(f"Comparison object created successfully.")
            except IntegrityError as e:
                logger.error(f"Integrity error while creating Comparison: {e}")
                raise ValueError(
                    "Failed to create Comparison due to constraint violation."
                )

            # Create KeyMetricComparison objects
            for metric in comparison_result.key_metrics_comparison:
                try:
                    KeyMetricComparison.objects.create(
                        comparison=comparison,
                        name=metric.name,
                        value1=metric.value1,
                        value2=metric.value2,
                        description=metric.description,
                    )
                except IntegrityError as e:
                    logger.error(
                        f"Integrity error while creating KeyMetricComparison for metric {metric.name}: {e}"
                    )
                    raise ValueError(
                        f"Failed to create KeyMetricComparison for metric {metric.name}."
                    )

            logger.info(
                f"Comparison saved successfully for summaries {summary1_id} and {summary2_id}."
            )

    except IntegrityError as e:
        logger.error(f"Database constraint error: {e}")
        raise ValueError(
            "A database constraint error occurred during the save operation."
        )

    except Exception as e:
        logger.error(f"Failed to save comparison to the database: {e}")
        raise RuntimeError(
            "An unexpected error occurred while saving the comparison."
        ) from e
