import logging
import pprint
import json

logger = logging.getLogger("apps.insights")


def log_completion_kwargs(*args, **kwargs) -> None:
    """Log the arguments passed to the completion function."""
    logger.info("## Completion kwargs:")
    logger.info(pprint.pformat({"args": args, "kwargs": kwargs}))


def log_completion_response(response) -> None:
    """Log the raw response object from the LLM."""
    try:
        # Use model_dump for Pydantic models
        response_dict = (
            response.model_dump() if hasattr(response, "model_dump") else response
        )
        logger.info("## Completion response:")
        logger.info(json.dumps(response_dict, indent=4))
    except Exception as e:
        logger.error("Failed to format response for logging: %s", e)


def log_completion_error(error) -> None:
    """Log errors during completion."""
    logger.error("## Completion error:")
    logger.error(str(error))


def log_parse_error(error) -> None:
    """Log errors during parsing of the response."""
    logger.error("## Parse error:")
    logger.error(str(error))
