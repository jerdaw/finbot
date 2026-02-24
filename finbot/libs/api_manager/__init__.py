"""Finbot API manager package -- exposes the global ``api_manager`` singleton."""

from finbot.libs.api_manager._utils.api_manager import APIManager

# api_manager is outside _api_manager.py in order to avoid import problems
api_manager: APIManager = APIManager()
