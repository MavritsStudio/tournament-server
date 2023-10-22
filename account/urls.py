from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from account import views


router = SimpleRouter()
router.register('accounts', views.UserViewSet)
router.register('teams', views.TeamViewSet)

urlpatterns = [
    *format_suffix_patterns([
            path('signup/', views.Signup.as_view(), name='account-signup'),
            path('login/', views.Login.as_view(), name='account-login'),
            path('logout/', views.Logout.as_view(), name='account-logout'),
    ]),

    path('', include(router.urls))
]
