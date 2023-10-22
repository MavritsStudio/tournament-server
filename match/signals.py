from django.dispatch import receiver
from django.db.models import signals

from match.models import Match
from tournament.models import Place


@receiver(
    signal=signals.post_save, sender=Match,
    dispatch_uid='direct_winner_and_loser_on_match_finish',
)
def direct_winner_and_loser_on_match_finish(instance, created, **kwargs):
    if created:
        return []

    if instance.status == Match.StatusChoice.FINISHED:
        winner, loser = instance.winner_loser
        tournament = instance.round.tournament
        next_match = instance.round.next_match

        if next_match is None:
            places = []

            for mate in winner.mates:
                places.append(Place(
                    tournament=tournament, team=winner,
                    user=mate, place='1'
                ))

            for mate in loser.mates:
                places.append(Place(
                    tournament=tournament, team=loser,
                    user=mate, place='2'
                ))

            return Place.objects.bulk_create(places)

        # Get next match childs
        # Get winners and save them as participants
        childs = next_match.childs.all()

        participant1, _ = childs[0].match.winner_loser
        participant2, _ = childs[1].match.winner_loser

        next_match.participant1 = participant1
        next_match.participant2 = participant2

        next_match.save()

        # loser append to Places
        round = instance.round
        if next_match.status == Match.StatusChoice.WALK_OVER:
            round += 1

        place = tournament.get_place_by_round_lose(round)
        return Place.objects.bulk_create(
            Place(
                tournament=tournament, team=loser,
                user=mate, place=place,
            ) for mate in loser.mates
        )
