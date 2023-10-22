from django.urls import path, include
from rest_framework.routers import SimpleRouter

from tournament.views import TournamentViewSet


router = SimpleRouter()
router.register('tournaments', TournamentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
