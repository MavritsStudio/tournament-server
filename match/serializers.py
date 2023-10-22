from rest_framework import serializers

from account.serializers import TeamSerializer
from match.models import Match


class UpdateMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('code', 'status', 'score1', 'score2')
        read_only_fields = ('code',)


class MatchWithParticipantSerializer(serializers.ModelSerializer):
    participant1 = TeamSerializer()
    participant2 = TeamSerializer()
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Match
        fields = (
            'code', 'status', 'finish',
            'participant1', 'participant2',
            'score1', 'score2',
        )
        read_only_fields = fields

