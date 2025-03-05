"""
Display components for literator package.

This module provides functionality for displaying query and request results
in various formats, primarily focused on console output.

Functions:
    display_query_results: Display the results of database queries
    display_request_results: Display the results of API requests

See Also:
    literator.display.console: Module containing the actual display implementations
"""

# Expose module
from literator.display.console import display_request_results, display_query_results

__all__ = ["display_query_results", "display_request_results"]
