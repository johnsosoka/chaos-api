#!/usr/bin/env python3
"""Example client for the Chaos API.

This script demonstrates various ways to interact with the Chaos API,
including different HTTP methods, content types, and endpoints.
"""

import argparse
import json
import sys
from urllib.parse import urljoin

import requests


def make_request(
    base_url: str,
    method: str,
    path: str,
    headers: dict | None = None,
    data: dict | None = None,
) -> requests.Response:
    """Make a request to the Chaos API.

    Args:
        base_url: Base URL of the Chaos API.
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        path: API path.
        headers: Optional request headers.
        data: Optional request body data.

    Returns:
        The response from the API.
    """
    url = urljoin(base_url, path)
    headers = headers or {}

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def example_json_api(base_url: str) -> None:
    """Demonstrate JSON API interactions.

    Args:
        base_url: Base URL of the Chaos API.
    """
    print("=== JSON API Examples ===\n")

    # GET request for list of users
    print("1. GET /users (list users)")
    response = make_request(base_url, "GET", "/users")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}\n")
    except json.JSONDecodeError:
        print(f"Body: {response.text}\n")

    # GET request for a specific user
    print("2. GET /users/42 (get specific user)")
    response = make_request(base_url, "GET", "/users/42")
    print(f"Status: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}\n")
    except json.JSONDecodeError:
        print(f"Body: {response.text}\n")

    # POST request to create a resource
    print("3. POST /orders (create order)")
    response = make_request(
        base_url,
        "POST",
        "/orders",
        data={"product_id": "abc123", "quantity": 2, "customer_email": "test@example.com"},
    )
    print(f"Status: {response.status_code}")
    try:
        print(f"Body: {json.dumps(response.json(), indent=2)}\n")
    except json.JSONDecodeError:
        print(f"Body: {response.text}\n")


def example_xml_api(base_url: str) -> None:
    """Demonstrate XML API interactions.

    Args:
        base_url: Base URL of the Chaos API.
    """
    print("=== XML API Examples ===\n")

    print("1. GET /weather/london (XML weather data)")
    response = make_request(
        base_url,
        "GET",
        "/weather/london",
        headers={"Accept": "application/xml"},
    )
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Body:\n{response.text}\n")


def example_html_api(base_url: str) -> None:
    """Demonstrate HTML API interactions.

    Args:
        base_url: Base URL of the Chaos API.
    """
    print("=== HTML API Examples ===\n")

    print("1. GET /products (HTML product page)")
    response = make_request(
        base_url,
        "GET",
        "/products",
        headers={"Accept": "text/html"},
    )
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Body (truncated): {response.text[:500]}...\n")


def example_health_check(base_url: str) -> None:
    """Demonstrate health and metrics endpoints.

    Args:
        base_url: Base URL of the Chaos API.
    """
    print("=== Health & Metrics Examples ===\n")

    print("1. GET /health")
    response = make_request(base_url, "GET", "/health")
    print(f"Status: {response.status_code}")
    print(f"Body: {json.dumps(response.json(), indent=2)}\n")

    print("2. GET /metrics")
    response = make_request(base_url, "GET", "/metrics")
    print(f"Status: {response.status_code}")
    print(f"Body: {json.dumps(response.json(), indent=2)}\n")


def example_custom_headers(base_url: str) -> None:
    """Demonstrate custom headers and request ID tracing.

    Args:
        base_url: Base URL of the Chaos API.
    """
    print("=== Custom Headers & Tracing ===\n")

    print("1. GET /api/resource with custom request ID")
    custom_request_id = "my-custom-request-123"
    response = make_request(
        base_url,
        "GET",
        "/api/resource",
        headers={"X-Request-ID": custom_request_id},
    )
    print(f"Status: {response.status_code}")
    print(f"Request ID (sent): {custom_request_id}")
    print(f"Request ID (received): {response.headers.get('x-request-id')}")
    print()


def main() -> None:
    """Parse arguments and run examples."""
    parser = argparse.ArgumentParser(
        description="Example client for the Chaos API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client.py                    # Run all examples
  python client.py --url http://api.example.com
  python client.py --example json     # Run only JSON examples
        """,
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the Chaos API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--example",
        choices=["json", "xml", "html", "health", "headers", "all"],
        default="all",
        help="Which example to run (default: all)",
    )

    args = parser.parse_args()

    # Ensure URL doesn't end with /
    base_url = args.url.rstrip("/")

    print(f"Chaos API Client - Connecting to {base_url}\n")

    try:
        # Health check first
        response = make_request(base_url, "GET", "/health")
        print(f"API is healthy: {response.json()['status']}\n")
    except Exception as e:
        print(f"Warning: Could not connect to API: {e}\n")
        return

    # Run requested examples
    if args.example in ("json", "all"):
        example_json_api(base_url)

    if args.example in ("xml", "all"):
        example_xml_api(base_url)

    if args.example in ("html", "all"):
        example_html_api(base_url)

    if args.example in ("health", "all"):
        example_health_check(base_url)

    if args.example in ("headers", "all"):
        example_custom_headers(base_url)

    print("Done!")


if __name__ == "__main__":
    main()
