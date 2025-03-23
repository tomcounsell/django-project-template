# Communication App

## Purpose

The Communication app handles all outbound communications from the application to users and external systems. It provides a standardized interface for sending emails, SMS messages, and other notifications.

> **Note**: As per the TODO list, this app will be merged into the Common app in the future.

## Features

### Email

- **Email Models**: Templates and tracking for email communications
- **Email Sending**: Interfaces with email delivery services

### SMS

- **SMS Models**: Templates and tracking for SMS communications
- **SMS Sending**: Interfaces with SMS delivery services

## Technical Approach

The Communication app follows these principles:

1. **Template-Based**: Communications use templates for consistency
2. **Delivery Tracking**: Records of all sent communications
3. **Service Abstraction**: Abstracts underlying delivery services
4. **Async Processing**: Non-blocking communication sending

## Usage

```python
from apps.communication.models import Email

# Create and send an email
email = Email(
    to_address="user@example.com",
    subject="Welcome to our service",
    html_content="<p>Welcome!</p>",
    text_content="Welcome!",
)
email.send()
```

## Development Guidelines

- All communication types should have tracking models
- Use templates for message content
- Implement proper error handling and retries
- Add appropriate logging
- Test with mock delivery services