from django.http import QueryDict
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)
from django.utils.translation import gettext_lazy as _

from match.models import Match
from match.permissions import IsMatchOrganizerOrReadOnlyPermission
from match.serializers import (
    MatchWithParticipantSerializer,
    UpdateMatchSerializer,
)


class MatchViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = (
        Match.objects.all()
        .select_related('round__tournament')
        .prefetch_related( 'participant1', 'participant2')
    )
    serializer_class = MatchWithParticipantSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsMatchOrganizerOrReadOnlyPermission,
    )

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateMatchSerializer

        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['status'] = Match.StatusChoice.FINISHED

        return super().update(request, *args, **kwargs)
