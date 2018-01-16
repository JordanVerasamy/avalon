import random
import string
import uuid

from channels import Group
from django.db import models

from app.avalon import assign_roles, gen_role_list
from .util import lobby_json


class GameManager(models.Manager):
    def create_game(self, num_players, has_mordred, has_oberon):
        joinable_id = ''.join(random.choices(string.ascii_uppercase, k=4))
        # For the set of all unstarted games joinable ID must be unique
        while self.filter(is_started=False, joinable_id=joinable_id):
            joinable_id = ''.join(random.choices(string.ascii_uppercase, k=4))

        if not gen_role_list(num_players, has_mordred, has_oberon):
            return False

        game = self.model(joinable_id=joinable_id,
                          num_players=num_players,
                          has_mordred=has_mordred,
                          has_oberon=has_oberon)
        game.save(using=self._db)
        return game


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    joinable_id = models.CharField(max_length=4)
    is_started = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    has_mordred = models.BooleanField(default=False)
    has_oberon = models.BooleanField(default=False)
    num_players = models.PositiveIntegerField(default=5)

    games = GameManager()

    def start(self):
        self.is_started = True
        assign_roles(self)
        self.save()
        self.message_players()

    def players(self):
        return self.player_set.filter(is_kicked=False).order_by('created_at').all()

    def message_players(self):
        Group(str(self.id)).send({
            'text': lobby_json(self),
        })

    def to_dict(self):
        return {
            'id': str(self.id),
            'joinable_id': self.joinable_id,
            'is_started': self.is_started,
            'num_players': self.num_players,
            'has_mordred': self.has_mordred,
            'has_oberon': self.has_oberon,
        }
