========================
Third-Party Integrations
========================

.. contents:: Table of Contents
   :depth: 3
   :local:

Overview
========

The Integration app provides a standardized, isolated approach to connecting with external services. Unlike typical Django projects that scatter integration code throughout the codebase, this template centralizes all external service connections with consistent patterns for error handling, testing, and configuration.

Design Philosophy
-----------------

**Why Integrations are Isolated**

Each integration is self-contained in its own module within ``apps/integration/``. This isolation provides:

- **Testability**: Mock external services without affecting other parts of the application
- **Maintainability**: Changes to one integration don't impact others
- **Reusability**: Easy to copy integration modules to other projects
- **Security**: Centralized credential management and validation

**Common Integration Structure**

Each integration follows a consistent pattern:

.. code-block:: text

    apps/integration/<service>/
    ├── __init__.py
    ├── client.py          # API client class
    ├── shortcuts.py       # Helper functions for common operations
    ├── README.md          # Integration-specific documentation
    └── tests/             # Isolated tests with mocking
        ├── __init__.py
        ├── test_client.py
        └── test_shortcuts.py

Configuration Management
------------------------

All integrations use environment variables for configuration, accessed through Django settings:

- **Development**: Debug mode automatically enabled, no real API calls made
- **Production**: Full API integration with proper error handling
- **Testing**: Simulated responses for CI/CD pipelines

Error Handling Strategy
-----------------------

All integrations follow these error handling principles:

1. **Graceful Degradation**: Applications continue to function when external services are unavailable
2. **Detailed Logging**: All API calls and errors are logged for debugging
3. **Debug Mode**: Development environments simulate API calls without making real requests
4. **Consistent Response Format**: All integration functions return dictionaries with ``success`` flag and error details

Loops Integration (Email)
==========================

Overview
--------

Loops is a transactional email service used for sending password resets, login codes, notifications, and team invitations. The Loops integration provides a clean API for sending transactional emails without managing email templates in Django.

**Use Cases:**

- Password reset emails
- Magic link authentication
- Team membership notifications
- Transactional notifications

Configuration
-------------

**Required Environment Variables:**

.. code-block:: bash

    # .env
    LOOPS_API_KEY=your_loops_api_key_here

**Django Settings:**

The integration automatically reads from ``settings.LOOPS_API_KEY``. In development mode (``DEBUG=True``), emails are logged but not sent.

.. code-block:: python

    # settings/third_party.py
    LOOPS_API_KEY = os.environ.get("LOOPS_API_KEY", "")

Client Reference
----------------

LoopsClient Class
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.loops.client import LoopsClient

    # Initialize with default settings
    client = LoopsClient()

    # Or with custom settings
    client = LoopsClient(
        api_key="your_api_key",
        debug_mode=False  # Set to True to simulate without sending
    )

**Methods:**

``transactional_email(to_email, transactional_id, data_variables=None, **kwargs)``
    Send a transactional email using a Loops template.

    :param str to_email: Recipient email address. If no contact exists, one will be created.
    :param str transactional_id: The ID of the transactional email template in Loops.
    :param dict data_variables: Template variables to populate in the email.
    :param kwargs: Additional parameters like ``bcc``.
    :returns: Dictionary with ``success`` flag and response data.
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.transactional_email(
            to_email="user@example.com",
            transactional_id="welcome_email",
            data_variables={
                "user_name": "John Doe",
                "login_url": "https://example.com/login"
            }
        )

        if result["success"]:
            print("Email sent successfully!")
        else:
            print(f"Error: {result.get('error')}")

``event(to_email, event_name, event_properties=None)``
    Send an event to Loops for trigger-based email campaigns.

    :param str to_email: Contact's email address.
    :param str event_name: Name of the event.
    :param dict event_properties: Event properties/data.
    :returns: Dictionary with ``success`` flag and response data.
    :rtype: dict

``test_api_key()``
    Test if the API key is valid.

    :returns: Dictionary with API key validation result.
    :rtype: dict

Debug Mode
~~~~~~~~~~

In debug mode (``DEBUG=True`` or ``debug_mode=True``), the client:

- Logs all email details to the console
- Returns success responses without making API calls
- Allows testing email flows without consuming API credits

Shortcuts Reference
-------------------

The shortcuts module provides high-level functions for common email operations.

send_password_reset_email
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.loops.shortcuts import send_password_reset_email

    send_password_reset_email(user, reset_url)

Send a password reset email to a user.

:param User user: User model instance
:param str reset_url: URL to redirect the user to reset their password
:returns: None (errors are logged)

**Example:**

.. code-block:: python

    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    # Generate reset token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = f"https://example.com/reset/{uid}/{token}/"

    # Send email
    send_password_reset_email(user, reset_url)

send_login_code_email
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.loops.shortcuts import send_login_code_email

    send_login_code_email(user, next_url=None)

Send a magic link login email to a user.

:param User user: User model instance
:param str next_url: Optional URL to redirect to after successful login
:returns: None (errors are logged)

**Example:**

.. code-block:: python

    # Send magic link for authentication
    send_login_code_email(user, next_url="/dashboard/")

send_team_membership_email
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.loops.shortcuts import send_team_membership_email

    send_team_membership_email(membership)

Send a team membership notification email.

:param Membership membership: Membership model instance
:returns: Boolean indicating success
:rtype: bool

**Example:**

.. code-block:: python

    # After creating a team membership
    membership = TeamMember.objects.create(
        team=team,
        user=new_user,
        role=Role.MEMBER.value
    )

    # Send notification
    send_team_membership_email(membership)

Setup Instructions
------------------

1. **Sign up for Loops**

   Create an account at `loops.so <https://loops.so>`_.

2. **Get your API key**

   Navigate to Settings > API in your Loops dashboard and copy your API key.

3. **Configure environment**

   Add to your ``.env`` file:

   .. code-block:: bash

       LOOPS_API_KEY=your_api_key_here

4. **Create email templates**

   In the Loops dashboard, create transactional email templates with the following IDs:

   - ``__loops_email_id__`` - Password reset template
   - ``__loops_login_code_id__`` - Login code template
   - ``__loops_team_membership_id__`` - Team membership template

   **Note:** Replace these placeholder IDs in the code with your actual template IDs.

5. **Test the integration**

   .. code-block:: python

       from apps.integration.loops.client import LoopsClient

       client = LoopsClient()
       result = client.test_api_key()

       if result["success"]:
           print("Loops integration configured correctly!")

Stripe Integration (Payments)
==============================

Overview
--------

Stripe is a payment processing platform used for handling subscriptions, one-time payments, and billing management. The Stripe integration provides a complete payment workflow including checkout sessions, customer management, and webhook handling.

**Use Cases:**

- Subscription billing
- One-time payments
- Customer management
- Payment method storage
- Webhook event processing

Configuration
-------------

**Required Environment Variables:**

.. code-block:: bash

    # .env
    STRIPE_API_KEY=sk_test_your_stripe_secret_key
    STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
    STRIPE_ENABLED=true

**Django Settings:**

.. code-block:: python

    # settings/third_party.py
    STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_ENABLED = os.environ.get("STRIPE_ENABLED", "False").lower() == "true" or (
        STRIPE_API_KEY and STRIPE_WEBHOOK_SECRET
    )

Client Reference
----------------

StripeClient Class
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.stripe.client import StripeClient

    # Initialize with default settings
    client = StripeClient()

    # Or with custom credentials
    client = StripeClient(
        api_key="sk_test_your_key",
        webhook_secret="whsec_your_secret"
    )

**Methods:**

``create_checkout_session(price_id, success_url, cancel_url, **kwargs)``
    Create a Stripe Checkout Session for payment or subscription.

    :param str price_id: The ID of the Stripe Price object
    :param str success_url: URL to redirect to after successful payment
    :param str cancel_url: URL to redirect to if checkout is canceled
    :param str customer_email: Customer's email address (optional)
    :param str mode: Checkout mode: 'payment', 'subscription', or 'setup' (default: 'payment')
    :param list payment_method_types: Payment methods to accept (optional)
    :param dict metadata: Additional metadata to include (optional)
    :param str customer_id: Existing Stripe customer ID (optional)
    :returns: Dictionary with checkout session data including session URL
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.create_checkout_session(
            price_id="price_1234567890",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            customer_email="user@example.com",
            mode="subscription",
            metadata={"user_id": "123"}
        )

        if result["success"]:
            # Redirect user to checkout
            checkout_url = result["session"]["url"]
            return redirect(checkout_url)

``create_customer(email, name=None, metadata=None, **kwargs)``
    Create a Stripe customer.

    :param str email: Customer's email address
    :param str name: Customer's name (optional)
    :param dict metadata: Additional metadata (optional)
    :returns: Dictionary with customer data
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.create_customer(
            email="user@example.com",
            name="John Doe",
            metadata={"user_id": "123"}
        )

        if result["success"]:
            customer_id = result["customer"]["id"]
            # Store customer_id in your database

``create_subscription(customer_id, price_id, trial_days=None, metadata=None, **kwargs)``
    Create a subscription for a customer.

    :param str customer_id: Stripe customer ID
    :param str price_id: Stripe price ID to subscribe to
    :param int trial_days: Number of trial days (optional)
    :param dict metadata: Additional metadata (optional)
    :returns: Dictionary with subscription data
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.create_subscription(
            customer_id="cus_1234567890",
            price_id="price_monthly",
            trial_days=14,
            metadata={"plan": "pro"}
        )

        if result["success"]:
            subscription_id = result["subscription"]["id"]
            status = result["subscription"]["status"]

``cancel_subscription(subscription_id, at_period_end=False, **kwargs)``
    Cancel a subscription.

    :param str subscription_id: Stripe subscription ID
    :param bool at_period_end: Cancel at end of billing period (default: False)
    :returns: Dictionary with cancellation result
    :rtype: dict

    **Example:**

    .. code-block:: python

        # Cancel at end of billing period
        result = client.cancel_subscription(
            subscription_id="sub_1234567890",
            at_period_end=True
        )

        # Cancel immediately
        result = client.cancel_subscription(
            subscription_id="sub_1234567890",
            at_period_end=False
        )

``verify_webhook_signature(payload, signature)``
    Verify a webhook signature from Stripe.

    :param bytes payload: Raw request payload (body)
    :param str signature: Stripe-Signature header value
    :returns: Dictionary with verification result and event data
    :rtype: dict

    **Example:**

    .. code-block:: python

        # In your webhook view
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')

        result = client.verify_webhook_signature(payload, signature)

        if result["verified"]:
            event_type = result["event"]["type"]
            event_data = result["event"]["data"]
            # Process the event

Shortcuts Reference
-------------------

create_checkout_session
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.stripe.shortcuts import create_checkout_session

    result = create_checkout_session(
        price_id,
        success_url=None,
        cancel_url=None,
        customer_email=None,
        mode="payment",
        metadata=None,
        user=None
    )

Create a Stripe Checkout Session with automatic URL generation and user integration.

:param str price_id: Stripe Price ID
:param str success_url: Success redirect URL (auto-generated if None)
:param str cancel_url: Cancel redirect URL (auto-generated if None)
:param str customer_email: Customer email (uses user.email if user provided)
:param str mode: 'payment', 'subscription', or 'setup'
:param dict metadata: Additional metadata (auto-populated from user if provided)
:param User user: User model instance (optional)
:returns: Dictionary with checkout session data
:rtype: dict

**Example:**

.. code-block:: python

    # Simple checkout with user
    result = create_checkout_session(
        price_id="price_1234567890",
        user=request.user,
        mode="subscription"
    )

    if result["success"]:
        return redirect(result["session"]["url"])

create_subscription_checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Convenience wrapper for creating subscription checkout sessions.

.. code-block:: python

    from apps.integration.stripe.shortcuts import create_subscription_checkout

    result = create_subscription_checkout(
        price_id="price_monthly",
        user=request.user
    )

create_customer_from_user
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.stripe.shortcuts import create_customer_from_user

    result = create_customer_from_user(user)

Create a Stripe customer from a User model instance with automatic metadata.

:param User user: User model instance
:returns: Dictionary with customer data
:rtype: dict

**Example:**

.. code-block:: python

    result = create_customer_from_user(request.user)

    if result["success"]:
        # Store customer ID on user model
        request.user.stripe_customer_id = result["customer"]["id"]
        request.user.save()

cancel_user_subscription
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.stripe.shortcuts import cancel_user_subscription

    result = cancel_user_subscription(
        subscription_id,
        at_period_end=True
    )

Cancel a user's subscription with automatic error handling and logging.

handle_webhook_event
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.stripe.shortcuts import handle_webhook_event

    result = handle_webhook_event(payload, signature)

Verify and parse a Stripe webhook event.

:param bytes payload: Raw request body
:param str signature: Stripe-Signature header
:returns: Dictionary with event data if verified
:rtype: dict

**Example:**

.. code-block:: python

    # In your webhook view
    from django.views.decorators.csrf import csrf_exempt
    from django.http import JsonResponse

    @csrf_exempt
    def stripe_webhook(request):
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')

        result = handle_webhook_event(payload, signature)

        if not result.get("verified"):
            return JsonResponse({"error": "Invalid signature"}, status=400)

        event = result["event"]

        # Handle different event types
        if event["type"] == "checkout.session.completed":
            # Handle successful checkout
            pass
        elif event["type"] == "customer.subscription.deleted":
            # Handle subscription cancellation
            pass

        return JsonResponse({"status": "success"})

Webhook Reference
-----------------

Setting Up Webhooks
~~~~~~~~~~~~~~~~~~~

1. **Create webhook endpoint in Stripe Dashboard**

   - Go to Developers > Webhooks
   - Click "Add endpoint"
   - Enter your webhook URL: ``https://yourdomain.com/api/webhooks/stripe/``
   - Select events to listen for

2. **Copy webhook signing secret**

   After creating the endpoint, copy the signing secret (starts with ``whsec_``) and add to your ``.env``:

   .. code-block:: bash

       STRIPE_WEBHOOK_SECRET=whsec_your_signing_secret

3. **Implement webhook handler**

   Create a view to handle webhook events:

   .. code-block:: python

       from django.views.decorators.csrf import csrf_exempt
       from django.views.decorators.http import require_POST
       from django.http import JsonResponse
       from apps.integration.stripe.shortcuts import handle_webhook_event

       @csrf_exempt
       @require_POST
       def stripe_webhook_view(request):
           payload = request.body
           signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')

           result = handle_webhook_event(payload, signature)

           if not result.get("verified"):
               return JsonResponse(
                   {"error": "Invalid signature"},
                   status=400
               )

           event = result["event"]
           event_type = event["type"]
           event_data = event["data"]

           # Handle events
           if event_type == "checkout.session.completed":
               handle_checkout_completed(event_data)
           elif event_type == "customer.subscription.updated":
               handle_subscription_updated(event_data)
           elif event_type == "customer.subscription.deleted":
               handle_subscription_deleted(event_data)

           return JsonResponse({"status": "success"})

Common Webhook Events
~~~~~~~~~~~~~~~~~~~~~

**Payment Events:**

- ``checkout.session.completed`` - Checkout completed successfully
- ``payment_intent.succeeded`` - Payment succeeded
- ``payment_intent.payment_failed`` - Payment failed

**Subscription Events:**

- ``customer.subscription.created`` - Subscription created
- ``customer.subscription.updated`` - Subscription updated
- ``customer.subscription.deleted`` - Subscription canceled
- ``invoice.paid`` - Invoice paid successfully
- ``invoice.payment_failed`` - Invoice payment failed

Testing Webhooks Locally
~~~~~~~~~~~~~~~~~~~~~~~~~

Use the Stripe CLI to test webhooks locally:

1. **Install Stripe CLI**

   .. code-block:: bash

       # macOS
       brew install stripe/stripe-cli/stripe

       # Or download from https://stripe.com/docs/stripe-cli

2. **Login to Stripe**

   .. code-block:: bash

       stripe login

3. **Forward webhooks to local server**

   .. code-block:: bash

       stripe listen --forward-to localhost:8000/api/webhooks/stripe/

4. **Trigger test events**

   .. code-block:: bash

       stripe trigger checkout.session.completed

Setup Instructions
------------------

1. **Create Stripe account**

   Sign up at `stripe.com <https://stripe.com>`_.

2. **Get API keys**

   Navigate to Developers > API keys and copy your secret key (``sk_test_...`` for test mode).

3. **Create products and prices**

   - Go to Products in the Stripe Dashboard
   - Create products with pricing
   - Copy the Price IDs for use in your code

4. **Configure environment**

   .. code-block:: bash

       # .env
       STRIPE_API_KEY=sk_test_your_secret_key
       STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
       STRIPE_ENABLED=true

5. **Test the integration**

   .. code-block:: python

       from apps.integration.stripe.client import StripeClient

       client = StripeClient()
       result = client.create_customer(
           email="test@example.com",
           name="Test User"
       )

       if result["success"]:
           print("Stripe integration working!")

Security Considerations
-----------------------

**PCI Compliance:**

- Never store card details on your server
- Use Stripe Checkout or Elements for card collection
- Always verify webhook signatures

**API Key Security:**

- Use test keys (``sk_test_``) in development
- Use live keys (``sk_live_``) only in production
- Rotate keys regularly
- Never commit keys to version control

**Webhook Security:**

- Always verify webhook signatures before processing
- Use HTTPS for webhook endpoints
- Implement idempotency for webhook processing
- Log all webhook events for audit trail

Twilio Integration (SMS/WhatsApp)
==================================

Overview
--------

Twilio is a communication platform used for sending SMS messages, phone verification, and two-factor authentication. The Twilio integration provides a simple API for SMS operations with automatic status tracking.

**Use Cases:**

- Phone number verification
- SMS notifications
- Two-factor authentication (2FA)
- Transactional SMS alerts
- Phone number validation

Configuration
-------------

**Required Environment Variables:**

.. code-block:: bash

    # .env
    TWILIO_ENABLED=true
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=+1234567890

**Django Settings:**

.. code-block:: python

    # settings/third_party.py
    TWILIO_ENABLED = os.environ.get("TWILIO_ENABLED", "False").lower() == "true"
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

Client Reference
----------------

TwilioClient Class
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.twilio.client import TwilioClient

    # Initialize with default settings
    client = TwilioClient()

    # Or with custom credentials
    client = TwilioClient(
        account_sid="your_account_sid",
        auth_token="your_auth_token",
        from_number="+1234567890"
    )

**Methods:**

``send_sms(to_number, body, from_number=None, status_callback=None)``
    Send an SMS message.

    :param str to_number: Recipient phone number (E.164 format)
    :param str body: Message content (up to 1600 characters)
    :param str from_number: Sender phone number (optional, uses default if not provided)
    :param str status_callback: URL to receive delivery status updates (optional)
    :returns: Dictionary with message SID and success status
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.send_sms(
            to_number="+12125551234",
            body="Your verification code is: 123456",
            status_callback="https://example.com/webhooks/twilio/"
        )

        if result["success"]:
            message_sid = result["sid"]
            print(f"SMS sent with SID: {message_sid}")
        else:
            print(f"Error: {result['error']}")

``verify_phone_number(phone_number)``
    Verify if a phone number is valid and can receive SMS.

    :param str phone_number: Phone number to verify
    :returns: Dictionary with validation result and carrier information
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.verify_phone_number("+12125551234")

        if result["success"] and result["valid"]:
            carrier = result["data"]["carrier"]
            print(f"Valid number on {carrier['name']}")
        else:
            print("Invalid phone number")

``get_message_status(message_sid)``
    Get the current delivery status of a message.

    :param str message_sid: Message SID from Twilio
    :returns: Dictionary with message status and details
    :rtype: dict

    **Possible Status Values:**

    - ``queued`` - Message queued for sending
    - ``sending`` - Message is being sent
    - ``sent`` - Message sent to carrier
    - ``delivered`` - Message delivered to recipient
    - ``undelivered`` - Message could not be delivered
    - ``failed`` - Message failed to send

    **Example:**

    .. code-block:: python

        result = client.get_message_status("SM1234567890")

        if result["success"]:
            status = result["status"]
            print(f"Message status: {status}")

            if status == "failed":
                error_code = result["data"]["error_code"]
                error_message = result["data"]["error_message"]
                print(f"Error {error_code}: {error_message}")

Shortcuts Reference
-------------------

send_sms
~~~~~~~~

.. code-block:: python

    from apps.integration.twilio.shortcuts import send_sms

    result = send_sms(
        to_number,
        body,
        from_number=None,
        save_to_db=True
    )

Send an SMS with automatic database tracking and status callback handling.

:param str to_number: Recipient phone number
:param str body: Message content
:param str from_number: Sender phone number (optional)
:param bool save_to_db: Whether to save SMS to database (default: True)
:returns: Dictionary with SMS data including database ID
:rtype: dict

**Example:**

.. code-block:: python

    result = send_sms(
        to_number="+12125551234",
        body="Your order has been shipped!"
    )

    if result["success"]:
        sms_id = result["sms_id"]
        # Store sms_id for status tracking

verify_phone_number
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.twilio.shortcuts import verify_phone_number

    result = verify_phone_number(phone_number)

Verify if a phone number is valid.

:param str phone_number: Phone number to verify
:returns: Dictionary with validation result
:rtype: dict

**Example:**

.. code-block:: python

    phone = "+12125551234"
    result = verify_phone_number(phone)

    if result["success"] and result["valid"]:
        print("Phone number is valid")
    else:
        print("Invalid phone number")

send_verification_code
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.twilio.shortcuts import send_verification_code

    result = send_verification_code(phone_number, code)

Send a verification code via SMS.

:param str phone_number: Recipient phone number
:param str code: Verification code to send
:returns: Dictionary with send result
:rtype: dict

**Example:**

.. code-block:: python

    import random

    # Generate verification code
    code = f"{random.randint(100000, 999999)}"

    # Send via SMS
    result = send_verification_code("+12125551234", code)

    if result["success"]:
        # Store code in session or database for verification
        request.session["verification_code"] = code
        request.session["phone_number"] = "+12125551234"

get_sms_status
~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.twilio.shortcuts import get_sms_status

    result = get_sms_status(sms_id)

Get the delivery status of an SMS by its database ID.

:param int sms_id: Database ID of the SMS
:returns: Dictionary with status information
:rtype: dict

**Example:**

.. code-block:: python

    result = get_sms_status(123)

    if result["success"]:
        status = result["status"]
        print(f"SMS status: {status}")

Phone Verification Flow
------------------------

Complete Phone Verification Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import random
    from django.core.cache import cache
    from apps.integration.twilio.shortcuts import send_verification_code, verify_phone_number

    def initiate_phone_verification(phone_number):
        """Step 1: Send verification code to phone number"""

        # Validate phone number format first
        validation = verify_phone_number(phone_number)
        if not validation.get("valid"):
            return {"success": False, "error": "Invalid phone number"}

        # Generate 6-digit code
        code = f"{random.randint(100000, 999999)}"

        # Send code via SMS
        result = send_verification_code(phone_number, code)

        if result["success"]:
            # Store code in cache with 10 minute expiration
            cache_key = f"phone_verification:{phone_number}"
            cache.set(cache_key, code, timeout=600)

            # Track verification attempts to prevent abuse
            attempts_key = f"verification_attempts:{phone_number}"
            attempts = cache.get(attempts_key, 0)
            cache.set(attempts_key, attempts + 1, timeout=3600)

            return {"success": True, "sms_id": result.get("sms_id")}

        return {"success": False, "error": result.get("error")}

    def verify_phone_code(phone_number, user_code):
        """Step 2: Verify the code entered by user"""

        # Get stored code from cache
        cache_key = f"phone_verification:{phone_number}"
        stored_code = cache.get(cache_key)

        if not stored_code:
            return {"success": False, "error": "Code expired or not found"}

        if stored_code == user_code:
            # Code is valid, delete from cache
            cache.delete(cache_key)

            # Clear verification attempts
            cache.delete(f"verification_attempts:{phone_number}")

            return {"success": True, "verified": True}
        else:
            return {"success": False, "error": "Invalid code"}

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

**Rate Limiting:**

Implement rate limiting to prevent abuse:

.. code-block:: python

    from django.core.cache import cache

    def check_verification_rate_limit(phone_number, max_attempts=3, window=3600):
        """Check if phone number has exceeded verification attempts"""
        attempts_key = f"verification_attempts:{phone_number}"
        attempts = cache.get(attempts_key, 0)

        if attempts >= max_attempts:
            return False  # Rate limit exceeded

        return True

**Code Expiration:**

- Use short expiration times (5-10 minutes)
- Delete codes after successful verification
- Generate new codes for each request

**Security Best Practices:**

- Use 6-digit codes (balance between security and usability)
- Implement exponential backoff for repeated attempts
- Log all verification attempts for monitoring
- Consider using Twilio Verify API for production use

Setup Instructions
------------------

1. **Create Twilio account**

   Sign up at `twilio.com <https://www.twilio.com>`_.

2. **Get credentials**

   - Navigate to Console Dashboard
   - Copy Account SID and Auth Token
   - Purchase a phone number with SMS capabilities

3. **Configure environment**

   .. code-block:: bash

       # .env
       TWILIO_ENABLED=true
       TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
       TWILIO_AUTH_TOKEN=your_auth_token
       TWILIO_PHONE_NUMBER=+1234567890

4. **Configure status callbacks (optional)**

   Create a webhook endpoint to receive delivery status updates:

   .. code-block:: python

       from django.views.decorators.csrf import csrf_exempt
       from django.http import JsonResponse

       @csrf_exempt
       def twilio_status_callback(request):
           message_sid = request.POST.get('MessageSid')
           status = request.POST.get('MessageStatus')

           # Update SMS record in database
           try:
               sms = SMS.objects.get(external_id=message_sid)
               sms.status = status
               sms.save()
           except SMS.DoesNotExist:
               pass

           return JsonResponse({"status": "success"})

5. **Test the integration**

   .. code-block:: python

       from apps.integration.twilio.shortcuts import send_sms

       result = send_sms(
           to_number="+1234567890",  # Your verified phone number
           body="Test message from Django!"
       )

       if result["success"]:
           print("SMS sent successfully!")

AWS S3 Integration (Storage)
=============================

Overview
--------

Amazon S3 is an object storage service used for storing files, images, documents, and backups. The S3 integration provides direct browser uploads, pre-signed URLs, and seamless Django model integration for file management.

**Use Cases:**

- User file uploads (images, documents, videos)
- Static file hosting for production
- Backup storage
- Media file storage
- Direct browser uploads without server load

**Alternative:** This integration also supports Cloudflare R2, which is S3-compatible and often more cost-effective.

Configuration
-------------

**Required Environment Variables:**

.. code-block:: bash

    # .env
    AWS_ACCESS_KEY_ID=your_access_key_id
    AWS_SECRET_ACCESS_KEY=your_secret_access_key
    AWS_STORAGE_BUCKET_NAME=your-bucket-name
    AWS_REGION=us-east-1

    # Optional: File upload settings
    AWS_MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
    AWS_UPLOAD_BUCKET=your-bucket-name  # Can be different from main bucket
    AWS_UPLOAD_PREFIX=uploads  # Prefix for uploaded files

**Django Settings:**

.. code-block:: python

    # settings/third_party.py
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    # S3 for static files in production
    if not LOCAL and AWS_S3_BUCKET_NAME:
        STATIC_URL = f"https://{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/"
        DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

**Cloudflare R2 Configuration:**

Cloudflare R2 is S3-compatible. To use R2:

.. code-block:: bash

    # .env
    AWS_ACCESS_KEY_ID=your_r2_access_key
    AWS_SECRET_ACCESS_KEY=your_r2_secret_key
    AWS_STORAGE_BUCKET_NAME=your-r2-bucket
    AWS_REGION=auto  # R2 uses 'auto' region
    AWS_S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com

Client Reference
----------------

S3Client Class
~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.aws.s3 import S3Client

    # Initialize with default settings
    client = S3Client()

    # Or with custom credentials
    client = S3Client(
        aws_access_key_id="your_key",
        aws_secret_access_key="your_secret",
        aws_s3_bucket_name="your-bucket",
        region_name="us-east-1"
    )

**Methods:**

``upload_file(file_path, object_key=None, public=True, extra_args=None)``
    Upload a file to S3 from local filesystem.

    :param str file_path: Path to the local file
    :param str object_key: S3 key for the file (defaults to filename)
    :param bool public: Make file publicly accessible
    :param dict extra_args: Additional boto3 upload arguments
    :returns: Dictionary with upload result and URL
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.upload_file(
            file_path="/tmp/image.jpg",
            object_key="uploads/images/image.jpg",
            public=True
        )

        if result["success"]:
            file_url = result["url"]
            print(f"File uploaded: {file_url}")

``upload_fileobj(file_obj, object_key, public=True, extra_args=None)``
    Upload a file-like object to S3.

    :param file_obj: File-like object (e.g., from Django's UploadedFile)
    :param str object_key: S3 key for the file
    :param bool public: Make file publicly accessible
    :param dict extra_args: Additional boto3 upload arguments
    :returns: Dictionary with upload result and URL
    :rtype: dict

    **Example:**

    .. code-block:: python

        # In a Django view handling file upload
        uploaded_file = request.FILES['file']

        result = client.upload_fileobj(
            file_obj=uploaded_file,
            object_key=f"uploads/{uploaded_file.name}",
            public=True
        )

``download_file(object_key, destination)``
    Download a file from S3 to local filesystem.

    :param str object_key: S3 key of the file
    :param str destination: Local path to save the file
    :returns: Dictionary with download result
    :rtype: dict

``generate_presigned_url(object_key, expiration=3600, http_method='GET')``
    Generate a temporary URL for accessing a private file.

    :param str object_key: S3 key of the file
    :param int expiration: URL expiration in seconds (default: 1 hour)
    :param str http_method: HTTP method (default: 'GET')
    :returns: Dictionary with pre-signed URL
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.generate_presigned_url(
            object_key="private/document.pdf",
            expiration=3600  # 1 hour
        )

        if result["success"]:
            # This URL will work for 1 hour
            temporary_url = result["url"]

``generate_presigned_post(object_key, expiration=3600, conditions=None, fields=None)``
    Generate form data for direct browser upload to S3.

    :param str object_key: S3 key for the uploaded file
    :param int expiration: Form expiration in seconds
    :param list conditions: Upload conditions (e.g., file size limits)
    :param dict fields: Additional form fields
    :returns: Dictionary with form URL and fields
    :rtype: dict

    **Example:**

    .. code-block:: python

        result = client.generate_presigned_post(
            object_key="uploads/user-file.jpg",
            expiration=3600,
            conditions=[
                ["content-length-range", 1, 5242880]  # 5MB max
            ]
        )

        if result["success"]:
            form_url = result["post_url"]
            form_fields = result["form_fields"]
            # Send to frontend for direct upload

``list_objects(prefix='', max_keys=1000)``
    List objects in the bucket.

    :param str prefix: Filter by key prefix
    :param int max_keys: Maximum number of objects to return
    :returns: Dictionary with list of objects
    :rtype: dict

``delete_object(object_key)``
    Delete an object from S3.

    :param str object_key: S3 key of the file to delete
    :returns: Dictionary with deletion result
    :rtype: dict

``get_object_metadata(object_key)``
    Get metadata for an S3 object.

    :param str object_key: S3 key of the file
    :returns: Dictionary with metadata
    :rtype: dict

Shortcuts Reference
-------------------

get_direct_upload_form_data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.aws.shortcuts import get_direct_upload_form_data

    result = get_direct_upload_form_data(
        original_filename,
        content_type=None,
        max_file_size=10485760,
        prefix="uploads",
        success_redirect_url=None,
        metadata=None
    )

Generate form data for direct browser upload with automatic Upload model creation.

:param str original_filename: Original filename
:param str content_type: MIME type (auto-detected if None)
:param int max_file_size: Maximum file size in bytes (default: 10MB)
:param str prefix: S3 key prefix
:param str success_redirect_url: Redirect URL after upload (optional)
:param dict metadata: Additional metadata to store
:returns: Dictionary with form data and Upload ID
:rtype: dict

**Example:**

.. code-block:: python

    # In your API endpoint
    result = get_direct_upload_form_data(
        original_filename="profile-photo.jpg",
        content_type="image/jpeg",
        max_file_size=5 * 1024 * 1024,  # 5MB
        prefix="uploads/profiles"
    )

    if result["success"]:
        return JsonResponse({
            "form_url": result["form_url"],
            "form_fields": result["form_fields"],
            "upload_id": result["upload_id"],
            "file_url": result["file_url"]
        })

complete_upload
~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.aws.shortcuts import complete_upload
    from apps.common.models.upload import Upload

    result = complete_upload(
        upload_id,
        file_size=None,
        status=Upload.STATUS_COMPLETE,
        error=None
    )

Mark an upload as complete and update metadata from S3.

:param int upload_id: Upload model ID
:param int file_size: File size in bytes (optional)
:param str status: Upload status
:param str error: Error message if failed
:returns: Dictionary with updated upload information
:rtype: dict

**Example:**

.. code-block:: python

    # After successful upload callback
    result = complete_upload(
        upload_id=123,
        status=Upload.STATUS_COMPLETE
    )

get_upload_file_url
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.aws.shortcuts import get_upload_file_url

    result = get_upload_file_url(
        upload_id,
        presigned=False,
        expiration=3600
    )

Get the URL for an uploaded file.

:param int upload_id: Upload model ID
:param bool presigned: Generate temporary URL for private files
:param int expiration: URL expiration in seconds (if presigned)
:returns: Dictionary with file URL
:rtype: dict

delete_upload
~~~~~~~~~~~~~

.. code-block:: python

    from apps.integration.aws.shortcuts import delete_upload

    result = delete_upload(upload_id)

Delete an upload from both S3 and database.

:param int upload_id: Upload model ID
:returns: Dictionary with deletion result
:rtype: dict

Direct Browser Upload Pattern
------------------------------

Complete implementation for direct browser uploads to S3:

**Backend API Endpoint:**

.. code-block:: python

    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from apps.integration.aws.shortcuts import get_direct_upload_form_data, complete_upload

    @require_POST
    def get_upload_credentials(request):
        """Generate credentials for direct S3 upload"""
        filename = request.POST.get('filename')
        content_type = request.POST.get('content_type')

        result = get_direct_upload_form_data(
            original_filename=filename,
            content_type=content_type,
            max_file_size=10 * 1024 * 1024,  # 10MB
            prefix="uploads/user-files"
        )

        if result["success"]:
            return JsonResponse({
                "form_url": result["form_url"],
                "form_fields": result["form_fields"],
                "upload_id": result["upload_id"],
                "file_url": result["file_url"]
            })
        else:
            return JsonResponse({"error": result["error"]}, status=400)

    @require_POST
    def confirm_upload(request):
        """Confirm upload completion"""
        upload_id = request.POST.get('upload_id')

        result = complete_upload(upload_id)

        if result["success"]:
            return JsonResponse({"upload": result["upload"]})
        else:
            return JsonResponse({"error": result["error"]}, status=400)

**Frontend Implementation (JavaScript):**

.. code-block:: javascript

    async function uploadFileToS3(file) {
        // Step 1: Get upload credentials from your backend
        const formData = new FormData();
        formData.append('filename', file.name);
        formData.append('content_type', file.type);

        const credentialsResponse = await fetch('/api/uploads/credentials/', {
            method: 'POST',
            body: formData
        });

        const credentials = await credentialsResponse.json();

        // Step 2: Upload directly to S3
        const uploadForm = new FormData();

        // Add all form fields from backend
        for (const [key, value] of Object.entries(credentials.form_fields)) {
            uploadForm.append(key, value);
        }

        // Add the file last
        uploadForm.append('file', file);

        const uploadResponse = await fetch(credentials.form_url, {
            method: 'POST',
            body: uploadForm
        });

        if (uploadResponse.ok) {
            // Step 3: Confirm upload with your backend
            const confirmForm = new FormData();
            confirmForm.append('upload_id', credentials.upload_id);

            await fetch('/api/uploads/confirm/', {
                method: 'POST',
                body: confirmForm
            });

            return {
                success: true,
                url: credentials.file_url,
                upload_id: credentials.upload_id
            };
        } else {
            throw new Error('Upload failed');
        }
    }

    // Usage
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        try {
            const result = await uploadFileToS3(file);
            console.log('File uploaded:', result.url);
        } catch (error) {
            console.error('Upload error:', error);
        }
    });

S3 Bucket Configuration
-----------------------

**CORS Configuration:**

Your S3 bucket needs CORS configuration to allow browser uploads:

.. code-block:: json

    [
        {
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "POST", "PUT"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["ETag"],
            "MaxAgeSeconds": 3000
        }
    ]

**Bucket Policy (Public Read):**

If files should be publicly accessible:

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::your-bucket-name/*"
            }
        ]
    }

**IAM User Permissions:**

Your IAM user needs these permissions:

.. code-block:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::your-bucket-name",
                    "arn:aws:s3:::your-bucket-name/*"
                ]
            }
        ]
    }

Setup Instructions
------------------

1. **Create AWS account**

   Sign up at `aws.amazon.com <https://aws.amazon.com>`_.

2. **Create S3 bucket**

   - Navigate to S3 service
   - Click "Create bucket"
   - Choose a unique bucket name
   - Select a region
   - Configure CORS and bucket policy (see above)

3. **Create IAM user**

   - Navigate to IAM service
   - Create new user with programmatic access
   - Attach S3 permissions policy
   - Copy Access Key ID and Secret Access Key

4. **Configure environment**

   .. code-block:: bash

       # .env
       AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
       AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
       AWS_STORAGE_BUCKET_NAME=my-django-bucket
       AWS_REGION=us-east-1

5. **Test the integration**

   .. code-block:: python

       from apps.integration.aws.s3 import S3Client

       client = S3Client()

       # Test upload
       with open('/tmp/test.txt', 'w') as f:
           f.write('Test content')

       result = client.upload_file(
           file_path='/tmp/test.txt',
           object_key='test.txt'
       )

       if result["success"]:
           print(f"File uploaded: {result['url']}")

Security Considerations
-----------------------

**Access Control:**

- Use IAM policies to restrict access
- Generate pre-signed URLs for temporary access to private files
- Set expiration times on pre-signed URLs
- Use separate buckets for different security levels

**File Upload Security:**

- Validate file types and sizes on the backend
- Scan uploaded files for malware
- Set maximum file size limits
- Use unique filenames to prevent overwrites

**Credentials:**

- Never expose AWS credentials in frontend code
- Use IAM roles for EC2/ECS instead of credentials when possible
- Rotate access keys regularly
- Use separate credentials for development and production

Redis Integration (Caching)
============================

Overview
--------

Redis is an in-memory data store used for caching, session storage, and real-time data. While Redis doesn't have a dedicated integration module like other services, it's configured through Django's caching framework.

**Use Cases:**

- Page and query caching
- Session storage
- Rate limiting
- Temporary data storage
- Real-time features

Configuration
-------------

**Required Environment Variables:**

.. code-block:: bash

    # .env
    REDIS_URL=redis://localhost:6379/0

    # Or for Redis Cloud/managed service
    REDIS_URL=redis://username:password@hostname:port/database

**Django Settings:**

.. code-block:: python

    # settings/database.py
    REDIS_URL = os.environ.get("REDIS_URL")

    if REDIS_URL:
        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                },
            }
        }
    else:
        # Fallback to in-memory cache for development
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        }

Usage Patterns
--------------

Basic Caching
~~~~~~~~~~~~~

.. code-block:: python

    from django.core.cache import cache

    # Set a cache value
    cache.set('my_key', 'my_value', timeout=300)  # 5 minutes

    # Get a cache value
    value = cache.get('my_key')

    # Get with default if not found
    value = cache.get('my_key', default='default_value')

    # Delete a cache value
    cache.delete('my_key')

    # Check if key exists
    if cache.has_key('my_key'):
        value = cache.get('my_key')

Caching Expensive Queries
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.core.cache import cache

    def get_expensive_data(user_id):
        cache_key = f'expensive_data:{user_id}'

        # Try to get from cache
        data = cache.get(cache_key)

        if data is None:
            # Cache miss - compute the data
            data = compute_expensive_operation(user_id)

            # Store in cache for 1 hour
            cache.set(cache_key, data, timeout=3600)

        return data

Caching with Decorators
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.views.decorators.cache import cache_page

    # Cache a view for 15 minutes
    @cache_page(60 * 15)
    def my_view(request):
        # Expensive computation
        data = get_data()
        return render(request, 'template.html', {'data': data})

Cache Template Fragments
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: django

    {% load cache %}

    {% cache 500 sidebar request.user.username %}
        .. expensive sidebar rendering ..
    {% endcache %}

Rate Limiting with Redis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.core.cache import cache
    import time

    def rate_limit(key, max_requests=10, window=60):
        """
        Simple rate limiting using Redis.

        :param key: Unique key for the rate limit (e.g., IP address)
        :param max_requests: Maximum requests allowed in window
        :param window: Time window in seconds
        :returns: True if request is allowed, False if rate limited
        """
        cache_key = f'rate_limit:{key}'

        # Get current request count
        current = cache.get(cache_key, 0)

        if current >= max_requests:
            return False

        # Increment counter
        if current == 0:
            # First request - set counter with expiration
            cache.set(cache_key, 1, timeout=window)
        else:
            # Increment existing counter
            cache.incr(cache_key)

        return True

    # Usage in view
    def api_view(request):
        client_ip = request.META.get('REMOTE_ADDR')

        if not rate_limit(client_ip, max_requests=100, window=3600):
            return JsonResponse(
                {"error": "Rate limit exceeded"},
                status=429
            )

        # Process request
        return JsonResponse({"data": "success"})

Session Storage
~~~~~~~~~~~~~~~

Configure Redis for session storage:

.. code-block:: python

    # settings/base.py
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

Setup Instructions
------------------

**Local Development:**

.. code-block:: bash

    # macOS
    brew install redis
    brew services start redis

    # Linux
    sudo apt-get install redis-server
    sudo systemctl start redis

    # Test connection
    redis-cli ping
    # Should respond with: PONG

**Production:**

Use a managed Redis service:

- **Redis Cloud** (cloud.redis.io)
- **AWS ElastiCache**
- **Heroku Redis**
- **DigitalOcean Managed Redis**

**Environment Configuration:**

.. code-block:: bash

    # .env
    REDIS_URL=redis://localhost:6379/0

    # For Redis with password
    REDIS_URL=redis://:password@hostname:port/0

Best Practices
--------------

**Cache Invalidation:**

.. code-block:: python

    from django.core.cache import cache
    from django.db.models.signals import post_save, post_delete

    def invalidate_cache(sender, instance, **kwargs):
        cache_key = f'user_data:{instance.id}'
        cache.delete(cache_key)

    post_save.connect(invalidate_cache, sender=User)
    post_delete.connect(invalidate_cache, sender=User)

**Cache Key Naming:**

Use descriptive, hierarchical cache keys:

.. code-block:: python

    # Good
    cache.set(f'user:{user_id}:profile', data)
    cache.set(f'team:{team_id}:members', data)
    cache.set(f'api:v1:endpoint:{params_hash}', data)

    # Bad
    cache.set('data', data)
    cache.set('user_profile', data)

**Cache Timeouts:**

Choose appropriate timeouts based on data freshness needs:

- **Static data**: Hours to days
- **User data**: Minutes to hours
- **Real-time data**: Seconds to minutes
- **Session data**: Session duration

Adding New Integrations
========================

This section provides a step-by-step guide for adding new third-party service integrations to your project.

Step-by-Step Guide
------------------

1. **Create Module Directory**

   .. code-block:: bash

       mkdir -p apps/integration/<service_name>
       touch apps/integration/<service_name>/__init__.py
       touch apps/integration/<service_name>/client.py
       touch apps/integration/<service_name>/shortcuts.py
       touch apps/integration/<service_name>/README.md
       mkdir apps/integration/<service_name>/tests

2. **Implement Client Class**

   Create ``client.py`` with a client class:

   .. code-block:: python

       import logging
       from django.conf import settings

       logger = logging.getLogger(__name__)

       class ServiceClient:
           """Client for ServiceName API"""

           def __init__(self, api_key=None):
               self.api_key = api_key or getattr(settings, 'SERVICE_API_KEY', None)
               self.enabled = bool(self.api_key)
               self.debug_mode = getattr(settings, 'DEBUG', False)

           def _validate_client(self):
               """Validate client is properly configured"""
               if not self.enabled:
                   logger.error("Service not enabled")
                   return False
               return True

           def some_operation(self, param):
               """Perform an operation using the service"""
               if self.debug_mode:
                   logger.info(f"[DEBUG] Would call API with {param}")
                   return {"success": True, "simulated": True}

               if not self._validate_client():
                   return {"success": False, "error": "Client not configured"}

               try:
                   # Make actual API call
                   result = self._make_api_call(param)
                   return {"success": True, "data": result}
               except Exception as e:
                   logger.error(f"API error: {str(e)}")
                   return {"success": False, "error": str(e)}

3. **Add Configuration to Settings**

   .. code-block:: python

       # settings/third_party.py
       SERVICE_API_KEY = os.environ.get("SERVICE_API_KEY", "")
       SERVICE_ENABLED = bool(SERVICE_API_KEY)

4. **Create Shortcut Functions**

   Create ``shortcuts.py`` with helper functions:

   .. code-block:: python

       from apps.integration.<service_name>.client import ServiceClient

       def perform_common_task(user, data):
           """
           Perform a common task using the service.

           Args:
               user: User instance
               data: Task data

           Returns:
               dict: Result with success flag
           """
           client = ServiceClient()
           result = client.some_operation(data)

           if result["success"]:
               # Update database or perform follow-up actions
               pass

           return result

5. **Write Tests with Mocking**

   Create ``tests/test_client.py``:

   .. code-block:: python

       import pytest
       from unittest.mock import patch, MagicMock
       from apps.integration.<service_name>.client import ServiceClient

       @pytest.fixture
       def client():
           return ServiceClient(api_key="test_key")

       def test_operation_success(client):
           with patch.object(client, '_make_api_call') as mock_call:
               mock_call.return_value = {"status": "ok"}

               result = client.some_operation("test")

               assert result["success"] is True
               assert "data" in result

       def test_operation_error(client):
           with patch.object(client, '_make_api_call') as mock_call:
               mock_call.side_effect = Exception("API Error")

               result = client.some_operation("test")

               assert result["success"] is False
               assert "error" in result

6. **Document in Module README**

   Create comprehensive documentation in ``README.md``:

   .. code-block:: markdown

       # ServiceName Integration

       ## Overview
       Description of what the service does and use cases.

       ## Configuration
       Required environment variables and settings.

       ## Usage
       Code examples showing how to use the integration.

       ## Testing
       How to run tests and mock the service.

Best Practices
--------------

**Error Handling:**

.. code-block:: python

    class ServiceAPIError(Exception):
        """Custom exception for Service API errors"""
        pass

    def _make_api_call(self, endpoint, **kwargs):
        try:
            response = requests.post(endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ServiceAPIError(f"API call failed: {str(e)}")

**Logging:**

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    # Log different levels appropriately
    logger.debug("Detailed debugging information")
    logger.info("General informational messages")
    logger.warning("Warning messages for potential issues")
    logger.error("Error messages for failures")

**Testing Patterns:**

.. code-block:: python

    import pytest
    from unittest.mock import patch, MagicMock

    @pytest.fixture
    def mock_api_response():
        return {"status": "success", "data": {"id": 123}}

    def test_with_mock(mock_api_response):
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_api_response

            client = ServiceClient()
            result = client.some_operation()

            assert result["success"] is True
            mock_post.assert_called_once()

**Security:**

- Never commit API keys or secrets
- Use environment variables for all credentials
- Validate and sanitize all inputs
- Implement rate limiting for API calls
- Log security-relevant events

Testing Integrations
====================

Mocking External Services
-------------------------

All integrations use mocking to avoid calling real APIs during tests:

.. code-block:: python

    import pytest
    from unittest.mock import patch, MagicMock

    @pytest.fixture
    def mock_stripe():
        with patch('stripe.checkout.Session.create') as mock:
            mock.return_value = MagicMock(
                id='cs_test_123',
                url='https://checkout.stripe.com/pay/cs_test_123'
            )
            yield mock

    def test_create_checkout(mock_stripe):
        from apps.integration.stripe.client import StripeClient

        client = StripeClient()
        result = client.create_checkout_session(
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )

        assert result["success"] is True
        assert "session" in result
        mock_stripe.assert_called_once()

Test Utilities
--------------

The project includes test utilities for integration testing:

.. code-block:: python

    # tests/conftest.py
    import pytest
    from django.conf import settings

    @pytest.fixture
    def integration_test_mode():
        """Enable test mode for all integrations"""
        settings.TESTING = True
        yield
        settings.TESTING = False

    @pytest.fixture
    def mock_all_integrations():
        """Mock all external service calls"""
        with patch('apps.integration.loops.client.LoopsClient.transactional_email'), \
             patch('apps.integration.stripe.client.StripeClient.create_checkout_session'), \
             patch('apps.integration.twilio.client.TwilioClient.send_sms'):
            yield

CI/CD Considerations
--------------------

**Running Tests Without Credentials:**

.. code-block:: yaml

    # .github/workflows/tests.yml
    name: Tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - name: Run tests
            run: |
              # Don't set integration credentials
              # Tests will use mocked responses
              pytest apps/integration/

**Environment Variables for Testing:**

.. code-block:: bash

    # .env.test
    DEBUG=True
    TESTING=True

    # Empty credentials trigger debug mode
    LOOPS_API_KEY=
    STRIPE_API_KEY=
    TWILIO_ENABLED=false

Integration Test Environment
-----------------------------

For testing against real services in a staging environment:

.. code-block:: python

    # settings/staging.py
    INTEGRATION_TESTING = os.environ.get('INTEGRATION_TESTING', 'False').lower() == 'true'

    if INTEGRATION_TESTING:
        # Use test/sandbox credentials
        STRIPE_API_KEY = os.environ.get('STRIPE_TEST_KEY')
        TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_TEST_SID')
    else:
        # Use production credentials
        STRIPE_API_KEY = os.environ.get('STRIPE_LIVE_KEY')

Summary
=======

This Django project template provides production-ready integrations for:

- **Loops**: Transactional email service
- **Stripe**: Payment processing and subscriptions
- **Twilio**: SMS messaging and phone verification
- **AWS S3**: File storage with direct browser uploads
- **Redis**: Caching and session storage

All integrations follow consistent patterns:

- **Debug Mode**: Simulated responses in development
- **Error Handling**: Graceful degradation and detailed logging
- **Testing**: Comprehensive mocking for CI/CD
- **Security**: Environment-based configuration
- **Documentation**: Clear examples and setup instructions

For questions or issues, refer to the individual integration READMEs in ``apps/integration/<service>/``.
