import operator
import json
from django.shortcuts import render, redirect
from app.models import Game, Player
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


def index_view(request):
    return render(request, 'index.html')


def lobby_view(request, game_id, player_id):
    game = Game.games.get(pk=game_id)

    player = Player.players.get(pk=player_id)
    if player.is_kicked:
        messages.add_message(request, messages.ERROR, 'You\'ve been kicked')
        return redirect('index')

    players = sorted(game.players(), key=operator.attrgetter('created_at'))

    return render(request, 'lobby.html', {
        'game': game,
        'self': player,
        'json': json.dumps({
            'self': player.to_dict(),
            'game': game.to_dict(),
            'players': list(map(lambda p: p.to_dict(), players)),
        })
    })


def kick_view(request, game_id, player_id, player_token):
    game = Game.games.get(pk=game_id)
    if game.is_started:
        return redirect('lobby', game_id=game_id, player_id=player_id)
    player = Player.players.get(pk=player_id)
    if not player.is_host:
        messages.add_message(request, messages.ERROR, 'Only the host can kick players')
        return redirect('lobby', game_id=game_id, player_id=player_id)

    kicked_player = Player.players.get(token=player_token)
    kicked_player.kick()
    return redirect('lobby', game_id=game_id, player_id=player_id)


def game_view(request, game_id, player_id):
    game = Game.games.get(pk=game_id)
    if len(game.players()) < 5:
        messages.add_message(request, messages.ERROR, 'Cannot start a game with less than 5 players')
        return redirect('lobby', game_id=game_id, player_id=player_id)

    player = Player.players.get(pk=player_id)
    if not game.is_started:
        if not player.is_host:
            messages.add_message(request, messages.ERROR, 'Only the host can start the game')
            return redirect('lobby', game_id=game_id, player_id=player_id)

        game.start() # should assign roles etc

    # should give list of who they saw
    return render(request, 'game.html', {
        'game': game,
        'player': player,
        'is_host': player.is_host,
    })


def create_game_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.add_message(request, messages.ERROR, 'Name cannot be blank')
            return render(request, 'create_game.html')

        game = Game.games.create_game(
            request.POST.get('has_mordred', 'off') == 'on',
            request.POST.get('has_oberon', 'off') == 'on',
        )
        player = Player.players.create_guest_player(
            game=game, name=name.title(), is_host=True)
        return redirect('lobby', game_id=game.id, player_id=player.id)

    return render(request, 'create_game.html')


def join_game_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.add_message(request, messages.ERROR, 'Name cannot be blank')
            return render(request, 'join_game.html')

        try:
            game = Game.games.get(
                joinable_id=request.POST.get('joinable_id').upper(), is_started=False)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'Could not find a game with that ID')
            return render(request, 'join_game.html')

        player = Player.players.create_guest_player(
            game=game, name=name.title(), is_host=False
        )
        return redirect('lobby', game_id=game.id, player_id=player.id)

    return render(request, 'join_game.html')
