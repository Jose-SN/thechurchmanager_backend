"""Checklist auth — IAM bypass enabled by default until separate IAM service is wired."""

from app.api.auth_context import AuthContext, get_checklist_context

# Alias for router imports
get_auth_context = get_checklist_context

__all__ = ["AuthContext", "get_auth_context", "get_checklist_context"]
