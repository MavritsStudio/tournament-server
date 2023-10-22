from django.http import QueryDict, Http404
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from utils.pagination import PageNumberPagination
from account.serializers import TeamSerializer
from account.models import Team

from tournament.models import Tournament
from tournament.permissions import IsOrganizerOrReadOnlyPermission
from tournament import serializers


class TournamentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Tournament.objects.all()
    serializer_class = serializers.RetrieveTournamentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOrganizerOrReadOnlyPermission,
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.TournamentSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['organizer'] = request.user.code

        return super().create(request, *args, **kwargs)

    @action(
        methods=['GET'], detail=True,
        url_name='teams', url_path='teams',
        serializer_class=TeamSerializer,
    )
    def get_teams(self, request, *args, **kwargs):
        instance = self.get_object()

        return Response(
            self.get_serializer(instance.teams.all(), many=True).data,
        )

    @action(
        methods=['POST'], detail=True,
        url_name='team-register', url_path='register',
        permission_classes=(IsAuthenticated,)
    )
    def register_team(self, request, *args, **kwargs):
        instance = self.get_object()

        team = Team.objects.filter(code=request.data.get('team')).first()
        if team is None:
            return Response({
                'details': _('Team does not exist.')
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance.append_team(team)
        except ValidationError as err:
            return Response({
                'details': err,
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=['PUT'], detail=True,
        url_name='activate', url_path='activate',
    )
    def activate_tournament(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            instance.activate()
        except ValidationError as err:
            return Response({
                'details': err,
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(instance).data)

    @action(
        methods=['GET'], detail=True,
        url_name='matches', url_path='matches',
        serializer_class=serializers.TournamentRoundSerializer,
    )
    def get_matches(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status == Tournament.StatusChoice.OPENED:
            raise Http404

        queryset = (
            instance.round_set.all()
            .order_by('number')
            .prefetch_related(
                'match',
                'match__participant1',
                'match__participant2',
            )
        )

        return Response(self.get_serializer(queryset, many=True).data)
