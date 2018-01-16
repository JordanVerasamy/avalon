from enum import Enum as PyEnum
from enum import auto
from random import shuffle

from enumfields import Enum


class Role(Enum):
    # Good
    VANILLA_GOOD = 'vanilla_good'
    MERLIN = 'merlin'
    PERCIVAL = 'percival'
    # Bad
    VANILLA_BAD = 'vanilla_bad'
    MORGANA = 'morgana'
    ASSASSIN = 'assassin'
    MORDRED = 'mordred'
    OBERON = 'oberon'


VISIBLE_BAD = [Role.VANILLA_BAD, Role.MORGANA, Role.ASSASSIN, Role.OBERON]
NOT_OBERON = [Role.VANILLA_BAD, Role.MORGANA, Role.ASSASSIN, Role.MORDRED]


class Interaction(PyEnum):
    SEE_THUMB = auto()
    SEE_EYES = auto()


SEE_THUMB = Interaction.SEE_THUMB
SEE_EYES = Interaction.SEE_EYES

ROLE_MECHANICS = {
    # Good
    Role.VANILLA_GOOD: {
        SEE_THUMB: [],
        SEE_EYES: [],
    },
    Role.MERLIN: {
        SEE_THUMB: VISIBLE_BAD,
        SEE_EYES: [],
    },
    Role.PERCIVAL: {
        SEE_THUMB: [Role.MERLIN, Role.MORGANA],
        SEE_EYES: [],
    },
    # Bad
    Role.VANILLA_BAD: {
        SEE_THUMB: [],
        SEE_EYES: NOT_OBERON,
    },
    Role.MORGANA: {
        SEE_THUMB: [],
        SEE_EYES: NOT_OBERON,
    },
    Role.ASSASSIN: {
        SEE_THUMB: [],
        SEE_EYES: NOT_OBERON,
    },
    Role.MORDRED: {
        SEE_THUMB: [],
        SEE_EYES: NOT_OBERON,
    },
    Role.OBERON: {
        SEE_THUMB: [],
        SEE_EYES: [],
    },
}


def gen_default(n):
    if n == 5:
        # 3 good 2 bad
        return [Role.MERLIN, Role.PERCIVAL, Role.VANILLA_GOOD, Role.MORGANA, Role.ASSASSIN]
    if n == 6:
        # 4 good 2 bad
        return gen_default(5) + [Role.VANILLA_GOOD]
    if n == 7:
        # 4 good 3 bad
        return gen_default(6) + [Role.VANILLA_BAD]
    if n == 8:
        # 5 good 3 bad
        return gen_default(7) + [Role.VANILLA_GOOD]
    if n == 9:
        # 5 good 4 bad
        return gen_default(8) + [Role.VANILLA_BAD]
    if n == 10:
        # 6 good 4 bad
        return gen_default(9) + [Role.VANILLA_GOOD]


def gen_role_list(num_players, mordred, oberon):
    roles = gen_default(num_players)
    if mordred:
        if Role.VANILLA_BAD in roles:
            roles.remove(Role.VANILLA_BAD)
        else:
            roles.remove(Role.ASSASSIN)
        roles.append(Role.MORDRED)

    if oberon:
        if Role.VANILLA_BAD in roles:
            roles.remove(Role.VANILLA_BAD)
        elif Role.ASSASSIN in roles:
            roles.remove(Role.ASSASSIN)
        else:
            return None
        roles.append(Role.OBERON)

    return roles


def player_info(game, player):
    players = game.players()
    eyes_seen = ROLE_MECHANICS[player.role][SEE_EYES]
    thumbs_seen = ROLE_MECHANICS[player.role][SEE_THUMB]
    player_thumbs_seen = []
    player_eyes_seen = []
    for p in players:
        if p == player:
            continue

        if p.role in thumbs_seen:
            player_thumbs_seen.append(p)
        if p.role in eyes_seen:
            player_eyes_seen.append(p)

    return player_thumbs_seen, player_eyes_seen

def assign_roles(game):
    players = game.players()
    roles = gen_role_list(game.num_players, game.has_mordred, game.has_oberon)
    shuffle(roles)
    for player, role in zip(players, roles):
        player.set_role(role)
