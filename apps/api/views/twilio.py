import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.common.models.sms import SMS

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
@api_view(['POST'])
def twilio_webhook(request):
    """
    Webhook handler for Twilio status callbacks.
    
    Receives status updates for sent SMS messages and updates
    the corresponding SMS record in the database.
    
    Expected parameters from Twilio:
    - MessageSid: Unique ID of the message
    - MessageStatus: Current status (sent, delivered, failed, etc.)
    - ErrorCode: Error code if status is failed
    - ErrorMessage: Error message if status is failed
    
    Returns:
        200 OK response
    """
    try:
        # Log the incoming webhook data
        logger.info(f"Received Twilio webhook: {request.data}")
        
        # Extract data from the webhook
        message_sid = request.data.get('MessageSid')
        message_status = request.data.get('MessageStatus')
        error_code = request.data.get('ErrorCode')
        error_message = request.data.get('ErrorMessage')
        
        if not message_sid or not message_status:
            return Response({"error": "Missing required parameters"}, status=400)
        
        # Look up the SMS by external_id (message_sid)
        try:
            sms = SMS.objects.get(external_id=message_sid)
            
            # Update the SMS status
            sms.update_status(
                status=message_status,
                error_code=error_code,
                error_message=error_message
            )
            
            return Response({"success": True})
            
        except SMS.DoesNotExist:
            logger.error(f"No SMS found with external_id: {message_sid}")
            return Response({"error": "SMS not found"}, status=404)
            
    except Exception as e:
        logger.exception(f"Error processing Twilio webhook: {str(e)}")
        return Response({"error": "Internal server error"}, status=500)