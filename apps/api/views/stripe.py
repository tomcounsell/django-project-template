"""
Stripe API views for handling webhook events from Stripe.
"""

import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.integration.stripe.webhook import handle_stripe_webhook

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook_view(request):
    """
    Handle webhook events from Stripe.
    
    This endpoint is called by Stripe when events occur in your Stripe account.
    The endpoint verifies the event signature, processes the event, and returns
    an appropriate response.
    
    Args:
        request: The HTTP request from Stripe
        
    Returns:
        HTTP response indicating success or failure
    """
    try:
        # Get payload and signature
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            logger.error("No Stripe signature header in request")
            return Response({"error": "No Stripe signature header"}, status=400)
        
        # Process the webhook
        result = handle_stripe_webhook(payload, sig_header)
        
        if not result.get("success"):
            logger.error(f"Error processing Stripe webhook: {result.get('error')}")
            # Still return 200 to avoid Stripe retrying failed events that may cause errors
            return Response({"success": False, "error": result.get("error")}, status=200)
        
        # Return success response
        return Response(
            {
                "success": True,
                "status": result.get("status", "processed"),
                "event_type": result.get("event_type", "unknown")
            },
            status=200
        )
    except Exception as e:
        # Log the error but still return 200 to prevent retries from Stripe
        logger.exception(f"Unhandled error in Stripe webhook: {str(e)}")
        return Response({"success": False, "error": "Internal server error"}, status=200)