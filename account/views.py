from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.authtoken.models import Token

from tournament.serializers import PlaceWithTeamSerializer, PlaceSerializer
from utils.pagination import PageNumberPagination

from account.models import Team
from account.permissions import (
    IsPersonalOrReadOnlyPermission,
    IsTeamMateOrReadOnlyPermission,
)
from account import serializers


class Signup(APIView):
    """Provide signup functionality."""

    permission_classes = (AllowAny,)
    serializer_class = serializers.SignupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            first_name = serializer.data['first_name']
            last_name = serializer.data['last_name']
            middle_name = serializer.data['middle_name']

            try:
                user = get_user_model().objects.get(email=email)
                content = {'detail': _('Email address already taken.')}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(email=email)

            # Set user fields provided
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.middle_name = middle_name

            user.save()

            return Response({
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'middle_name': middle_name,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']
            user = authenticate(email=email, password=password)

            if user:
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key},
                                    status=status.HTTP_200_OK)
                else:
                    content = {'detail': _('User account not active.')}
                    return Response(content,
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                content = {'detail':
                           _('Unable to login with provided credentials.')}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Remove all auth tokens owned by request.user.
        """
        tokens = Token.objects.filter(user=request.user)
        for token in tokens:
            token.delete()
        content = {'success': _('User logged out.')}
        return Response(content, status=status.HTTP_200_OK)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = get_user_model().objects.all()
    permission_classes = (IsPersonalOrReadOnlyPermission, AllowAny,)
    serializer_class = serializers.UserSerializer

    def get_object(self):
        if (
            self.request
            and self.kwargs.get(self.lookup_field, '') == 'me'
            and self.request.user
            and self.request.user.is_authenticated
        ):
            return self.request.user

        return super().get_object()

    @action(
        methods=['GET'], detail=True,
        url_name='teams', url_path='teams',
        serializer_class=serializers.TeamWithMatesSerializer,
        pagination_class=PageNumberPagination,
    )
    def get_teams(self, request, *args, **kwargs):
        instance = self.get_object()

        teams = (
            Team.objects
            .filter_by_user(instance)
            .order_by('name')
            .prefetch_related('mate1', 'mate2')
        )

        page = self.paginate_queryset(teams)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)

    @action(
        methods=['GET'], detail=True,
        url_name='tournaments', url_path='tournaments',
        serializer_class=PlaceWithTeamSerializer,
        pagination_class=PageNumberPagination,
    )
    def get_tournaments(self, request, *args, **kwargs):
        instance = self.get_object()

        queryset = (
            instance.places.all()
            .prefetch_related('tournament', 'team')
            .order_by('tournament__status')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TeamViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = (
        Team.objects.all()
        .select_related('mate1', 'mate2')
        .order_by('name')
    )
    serializer_class = serializers.TeamWithMatesSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsTeamMateOrReadOnlyPermission,
    )
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.TeamSerializer

        return super().get_serializer_class()

    @action(
        methods=['GET'], detail=True,
        url_name='tournaments', url_path='tournaments',
        serializer_class=PlaceSerializer,
    )
    def get_tournaments(self, request, *args, **kwargs):
        instance = self.get_object()

        queryset = (
            instance.places.all()
            .select_related('tournament')
            .order_by('tournament__status')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)