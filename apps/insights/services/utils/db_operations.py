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
            return summary

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
        comparison_result (ComparisonOutput): The structured comparison result from LLM.

    Returns:
        Comparison: The created Comparison object.
    """
    try:
        # Pre-save validation: Ensure comparison_result contains necessary data
        if not comparison_result.comparison_summary:
            logger.error("Comparison summary is missing in the LLM output.")
            raise ValidationError("Comparison summary is missing in the LLM output.")
        if not comparison_result.key_metrics_comparison:
            logger.error("Key metrics comparison is missing in the LLM output.")
            raise ValidationError(
                "Key metrics comparison is missing in the LLM output."
            )

        with transaction.atomic():
            logger.info(
                f"Saving comparison for summaries {summary1_id} and {summary2_id}..."
            )

            # Fetch the summaries
            try:
                summary1 = Summary.objects.get(id=summary1_id)
                logger.info(f"Fetched Summary 1 with ID: {summary1_id}")
            except Summary.DoesNotExist as e:
                logger.error(f"Summary with ID {summary1_id} does not exist: {e}")
                raise ValidationError(f"Summary with ID {summary1_id} does not exist.")

            try:
                summary2 = Summary.objects.get(id=summary2_id)
                logger.info(f"Fetched Summary 2 with ID: {summary2_id}")
            except Summary.DoesNotExist as e:
                logger.error(f"Summary with ID {summary2_id} does not exist: {e}")
                raise ValidationError(f"Summary with ID {summary2_id} does not exist.")

            # Validate that summary IDs are not identical
            if summary1_id == summary2_id:
                logger.error(
                    "Validation error: Summary IDs for comparison must be different."
                )
                raise ValidationError("The summaries for comparison must be different.")

            # Create the Comparison object
            try:
                comparison = Comparison.objects.create(
                    summary1=summary1,
                    summary2=summary2,
                    comparison_summary=comparison_result.comparison_summary,
                )
                logger.info(f"Comparison created with ID: {comparison.id}")
            except IntegrityError as ie:
                logger.error(f"Integrity error while creating Comparison: {ie}")
                raise ValidationError(
                    "Failed to create Comparison due to integrity constraints."
                ) from ie

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
                    logger.info(
                        f"KeyMetricComparison created for metric {metric.name}."
                    )
                except IntegrityError as ie:
                    logger.error(
                        f"Integrity error while creating KeyMetricComparison for {metric.name}: {ie}"
                    )
                    raise ValidationError(
                        f"Failed to create KeyMetricComparison for {metric.name}."
                    ) from ie

            logger.info(
                f"Comparison saved successfully for summaries {summary1_id} and {summary2_id}."
            )
            return comparison

    except ValidationError as ve:
        logger.error(f"Validation error while saving comparison: {ve}")
        raise
    except IntegrityError as ie:
        logger.error(f"Database integrity error: {ie}")
        raise ValidationError(
            "A database integrity error occurred while saving the comparison."
        ) from ie
    except Exception as e:
        logger.error(f"Unexpected error while saving comparison: {e}")
        raise RuntimeError("Failed to save comparison and key metrics.") from e
