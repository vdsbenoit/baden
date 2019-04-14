# -*-coding:UTF-8 -*
import logging
import os

from mailmerge import MailMerge

from model.game import Game
from model.team import Team
from model import service, properties

log = logging.getLogger('default')

TEAM_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "team_roadmap_template.docx")
GAME_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "game_roadmap_template.docx")


def generate_team_roadmaps():
    tb_merging = []
    for team in Team.objects():
        team_dict = dict(sectionName=team.section,
                         teamCode=team.code)
        games = service.get_games(team.code)
        for i in range(len(games)):
            team_dict["game{}".format(i+1)] = games[i].name
            team_dict["gameID{}".format(i+1)] = str(games[i].number)
        tb_merging.append(team_dict)

    with MailMerge(TEAM_ROADMAP_TEMPLATE) as document:
        document.merge_pages(tb_merging)
        document.write(os.path.join(properties.PROJECT_ROOT, "team_roadmaps.docx"))


def generate_game_roadmaps():
    tb_merging = []
    game_names = Game.objects().distinct('name')
    for name in game_names:
        game = Game.objects(name=name).first()
        game_dict = dict(gameName=name,
                         gameID=str(game.number),
                         circuit=game.circuit)
        i = 1
        for players in service.get_players(game.number):
            game_dict["teams{}".format(i)] = "{} - {}".format(players[0].code, players[1].code)
            i += 1
        tb_merging.append(game_dict)

    with MailMerge(GAME_ROADMAP_TEMPLATE) as document:
        document.merge_pages(tb_merging)
        document.write(os.path.join(properties.PROJECT_ROOT, "game_roadmaps.docx"))


