# apps/insights/services/utils/db_operations.py
import logging
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from apps.insights.models.summary import Summary, KeyMetric
from apps.insights.services.openai.schemas import SummaryOutput
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.services.openai.schemas import ComparisonOutput

logger = logging.getLogger(__name__)


def save_summary_to_database(start_date: str, llm_summary: SummaryOutput):
    """
    Saves the structured summary result and its key metrics to the database.

    Args:
        start_date (str): Start date for the summary (YYYY-MM-DD).
        llm_summary (SummaryOutput): The structured summary result.

    Returns:
        Summary: The created Summary object.
    """
    try:
        # Pre-save validation: Ensure LLM summary contains necessary data
        if not llm_summary.dataset_summary:
            logger.error("Dataset summary is missing in the LLM output.")
            raise ValidationError("Dataset summary is missing in the LLM output.")
        if not llm_summary.key_metrics:
            logger.error("Key metrics are missing in the LLM output.")
            raise ValidationError("Key metrics are missing in the LLM output.")

        with transaction.atomic():
            logger.info(
                f"Saving summary for start_date={start_date} to the database..."
            )

            # Create the Summary object
            try:
                summary = Summary.objects.create(
                    start_date=start_date,
                    dataset_summary=llm_summary.dataset_summary,
                )
                logger.info(f"Summary created with ID: {summary.id}")
            except IntegrityError as ie:
                logger.error(
                    f"Integrity error while creating Summary for start_date={start_date}: {ie}"
                )
                raise ValidationError(
                    f"Failed to create Summary due to integrity constraints: {ie}"
                ) from ie

            # Create KeyMetric objects
            for metric in llm_summary.key_metrics:
                try:
                    KeyMetric.objects.create(
                        summary=summary,
                        name=metric.name,
                        value=metric.value,
                    )
                    logger.info(
                        f"KeyMetric created for {metric.name} with value {metric.value}"
                    )
                except IntegrityError as ie:
                    logger.error(
                        f"Integrity error while creating KeyMetric for {metric.name}: {ie}"
                    )
                    raise ValidationError(
                        f"Failed to create KeyMetric for {metric.name}."
                    ) from ie

            logger.info(
                f"Saved summary for start_date={start_date} with {len(llm_summary.key_metrics)} key metrics."
            )
            return summary  # Optional: Return the created Summary object

    except ValidationError as ve:
        logger.error(f"Validation error while saving summary: {ve}")
        raise
    except IntegrityError as ie:
        logger.error(f"Database integrity error: {ie}")
        raise ValidationError(
            "A database integrity error occurred while saving."
        ) from ie
    except Exception as e:
        logger.error(f"Unexpected error while saving summary: {e}")
        raise RuntimeError("Failed to save summary and key metrics.") from e


def save_comparison_to_database(
    summary1_id: int, summary2_id: int, comparison_result: ComparisonOutput
):
    """
    Saves the LLM comparison result to the database.

    Args:
        summary1_id (int): ID of the first summary (Week 1).
        summary2_id (int): ID of the second summary (Week 2).
        comparison_result (ComparisonOutput Pydantic model): The structured comparison result from the LLM.
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
