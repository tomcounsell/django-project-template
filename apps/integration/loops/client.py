from typing import Dict, Optional

from icecream import ic
import requests

from settings import LOOPS_API_KEY


class LoopsClient:
    BASE_URL = "https://app.loops.so/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or LOOPS_API_KEY

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> dict:
        """
        Make an API request to Loops.so

        :param method: HTTP method for the request
        :param endpoint: API endpoint
        :param params: Query parameters for the request
        :param json: JSON data for the request body
        :return: Parsed JSON response
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        ic(method, url, params, json)

        try:
            response = requests.request(
                method, url, headers=headers, params=params, json=json
            )
            # response.raise_for_status()
            response_dict = response.json()
            if response_dict.get("success", False):
                return response_dict
            else:
                ic(response_dict)
                raise LoopsAPIError(
                    f"API request failed: {response_dict.get('message', 'unknown')}"
                )

        except requests.RequestException as e:
            raise LoopsAPIError(f"API request failed: {str(e)}")

    def test_api_key(self) -> Dict:
        """
        Test the API key

        :return: API response
        """
        response = self._make_request(method="GET", endpoint="/api-key")
        ic(response)
        return response

    def transactional_email(
        self, to_email: str, transactional_id: str, data_variables: dict = None
    ) -> dict:
        """
        Send a transactional email

        :param str to_email: The contact’s email address. If there is no contact
                          with this email, one will be created.
        :param str transactional_id: The ID of the transactional email to send.
        :param str data_variables: An object containing contact data as defined
                                  by the data variables added to the
                                  transactional email template.
        """
        return self._make_request(
            method="POST",
            endpoint="/transactional",
            json={
                "email": to_email,
                "transactionalId": transactional_id,
                "dataVariables": data_variables or {},
            },
        )

    def event(self, to_email: str, event_name: str) -> dict:
        """
        Send an event to Loops

        :param str to_email: The contact’s email address. If there is no contact
                          with this email, one will be created.
        :param str event_name: The name of the event
        """

        return self._make_request(
            method="POST",
            endpoint="/events/send",
            json={
                "email": to_email,
                "eventName": event_name,
            },
        )


class LoopsAPIError(Exception):
    """Custom exception for Loops API errors"""

    pass
