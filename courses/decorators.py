from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from .models import UserProfile


def verified_required(view_func):
    """
    Decorator that checks if the authenticated user has a verified UserProfile.
    Unverified users are redirected to a 'Pending Verification' warning page.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        if not profile.is_verified:
            return HttpResponseRedirect(reverse('verification_pending'))

        return view_func(request, *args, **kwargs)
    return _wrapped_view