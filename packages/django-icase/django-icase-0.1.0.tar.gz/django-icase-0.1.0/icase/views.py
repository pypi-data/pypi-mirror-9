"""
Custom 404 handler view for catching 404 responses due solely to
different casing.
"""

from django.shortcuts import redirect
from django.views.defaults import page_not_found


def icase_404_handler(request, **kwargs):
    """
    Checks that the URL is not a case-variance of itself. If it is, redirect
    to the lowercased version. Otherwise return a normal 404 response.
    """
    if request.path != request.path.lower():
        return redirect(request.path.lower())
    return page_not_found(request, **kwargs)
