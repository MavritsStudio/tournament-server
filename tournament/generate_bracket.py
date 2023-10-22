from typing import Optional, TypeVar, NamedTuple
from django.utils.translation import gettext_lazy as _

from match.models import Match


T = TypeVar("T")

class TournamentRoundMatch(NamedTuple):
    id: int
    status: int
    teams: tuple[T]
    round: int

RoundMatches = dict[TournamentRoundMatch, Optional[TournamentRoundMatch]]


def generate_bracket(
    teams: list[T],
    matches: RoundMatches,
) -> TournamentRoundMatch:
    """
    Generate tournament bracket with scheduled and walk_over matches for the
    given teams.

    Notes:
        For tournament bracket generation has been used playoff format
        (without Third place match). For more details:
        https://en.wikipedia.org/wiki/Playoff_format

    Attributes:
        teams: tournament participant team codes list, order of given list
            affects the result tournament bracket.
        matches: collection of the lighted `Match` model, key-value relation
            means match -> next match relation. None value of some key key
            means that match is final.  
    """
    length = len(teams)

    if length == 0:
        raise ValueError(_('Teams list can not be an empty.'))

    # If meets two teams, then create scheduled match
    # One teams means that match is walk over
    if length < 3:
        match = TournamentRoundMatch(
            len(matches),
            (
                Match.StatusChoice.SCHEDULED
                if length == 2
                else Match.StatusChoice.WALK_OVER
            ),
            tuple(teams),
            round=1
        )

        matches[match] = None
        return match

    middle = length // 2 + length % 2

    upper_match = generate_bracket(teams[:middle], matches)
    lower_match = generate_bracket(teams[middle:], matches)

    # Synch matches round number and create walk over match if needed
    if upper_match.round != lower_match.round:
        prev_match = lower_match

        lower_match = TournamentRoundMatch(
            len(matches),
            Match.StatusChoice.WALK_OVER, tuple(),
            lower_match.round + 1,
        )

        matches[prev_match] = lower_match
        matches[lower_match] = None

    # Create 'result' match for upper and lower matches
    match = TournamentRoundMatch(
        len(matches),
        Match.StatusChoice.SCHEDULED, tuple(),
        upper_match.round + 1,
    )

    matches[upper_match] = match
    matches[lower_match] = match
    matches[match] = None

    return match
