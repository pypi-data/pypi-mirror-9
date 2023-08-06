"""
Middleware for enforcing lowercased URLs.
"""
from django.shortcuts import redirect


class LowerCased(object):

    def handle_request(self, request):
        if request.path == request.path.lower():
            return None
        return redirect(request.path.lower())
