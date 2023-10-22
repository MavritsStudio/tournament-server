from django.urls import path, include
from rest_framework.routers import SimpleRouter

from match import views


router = SimpleRouter()
router.register('matches', views.MatchViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
