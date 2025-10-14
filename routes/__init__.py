"""
Routes module for MitoMate application.
Contains Flask route handlers organized by functionality.
"""

from routes.landing import register_landing_routes

__all__ = [
    'register_landing_routes'
]
