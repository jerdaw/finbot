"""
Security Constants

This module holds constants related to security, such as token lifetimes, encryption keys
(for non-production use), and password policy requirements. It serves as a central place
to manage values that affect the security posture of the application.

Attributes:
    TOKEN_EXPIRY_TIME (int): Time in seconds until an authentication token expires.
    PASSWORD_MIN_LENGTH (int): Minimum required length for user passwords.
"""
from __future__ import annotations
