"""
Dashboard context callback for Google Material 3 Admin panel.
Provides player analytics and gameplay metrics.
"""

from django.db.models import Avg
from apps.users.models import User


def dashboard_callback(request, context):
    """Calculates statistics for the dashboard view."""
    total_players = User.objects.count()
    active_players = User.objects.filter(is_active=True).count()
    avg_lives_val = User.objects.aggregate(Avg('lives'))['lives__avg']
    avg_lives = round(avg_lives_val, 1) if avg_lives_val is not None else 5.0
    zero_lives = User.objects.filter(lives=0).count()
    recent_players = User.objects.order_by('-created_at')[:8]

    context.update({
        'total_players': total_players,
        'active_players': active_players,
        'avg_lives': avg_lives,
        'zero_lives': zero_lives,
        'recent_players': recent_players,
    })
    return context
