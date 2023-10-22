from rest_framework import serializers

from account.serializers import TeamSerializer
from match.serializers import MatchWithParticipantSerializer
from tournament.models import Tournament, Round, Place


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            'name', 'description', 'organizer',
            'contact', 'limit', 'start',
        )
        read_only_fields = ('code',)


class RetrieveTournamentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Tournament
        fields = ('code', 'name', 'status', 'description', 'finish')
        read_only_fields = fields


class TournamentRoundSerializer(serializers.ModelSerializer):
    match = MatchWithParticipantSerializer()

    class Meta:
        model = Round
        fields = ('tournament', 'number', 'match', 'next_match')
        read_only_fields = fields


class PlaceSerializer(serializers.ModelSerializer):
    tournament = RetrieveTournamentSerializer(read_only=True)

    class Meta:
        model = Place
        fields = ('tournament', 'team', 'place')


class PlaceWithTeamSerializer(PlaceSerializer):
    team = TeamSerializer(read_only=True)

    class Meta(PlaceSerializer.Meta):
        pass
