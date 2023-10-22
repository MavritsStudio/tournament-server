from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from match.models import Match
from tournament.models import Tournament, Round
from tournament.generate_bracket import generate_bracket, RoundMatches


def initialize_bracket(tournament: Tournament) -> list[Round]:
    if Round.objects.filter(tournament=tournament).exists():
        raise ValidationError(
            _('The "%(name)s" tournament bracket already exists.'),
            params={'name': tournament.name},
        )

    light_matches: RoundMatches = {}
    generate_bracket(tournament.teams.all(), light_matches)

    matches = Match.objects.bulk_create(
        Match(
            status=match.status,
            participant1=match.teams[0] if len(match.teams) > 0 else None,
            participant2=match.teams[1] if len(match.teams) == 2 else None,
        ) for match in light_matches.keys()
    )

    rounds = Round.objects.bulk_create(
        Round(
            tournament=tournament,
            number=child.round,
            match=matches[child.id],
            next_match=matches[parent.id] if parent else None,
        ) for child, parent in light_matches.items()
    )

    return rounds
