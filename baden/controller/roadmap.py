# -*-coding:UTF-8 -*
import logging
import os
import tempfile

import pyqrcode
from mailmerge import MailMerge

from model.game import Game
from model.team import Team
from model import service, properties

log = logging.getLogger('default')

TEAM_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "team_roadmap_template.docx")
GAME_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "game_roadmap_template.docx")
QR_SCALE = 4
QUIET_ZONE = 1
QR_COLOR = (43, 114, 84)
QR_VERSION = 4
QR_ERROR = 'Q'


def generate_team_roadmaps():
    tb_merging = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for team in Team.objects():
            team_dict = dict(section=team.section,
                             teamCode=team.code,
                             )
            qr = pyqrcode.create(team.hash, error=QR_ERROR, version=QR_VERSION)
            qr_file = os.path.join(tmpdir, "team.png")
            qr.png(qr_file, scale=QR_SCALE, module_color=QR_COLOR, quiet_zone=QUIET_ZONE)
            with open(qr_file, 'r', encoding='ANSI') as f:
                img_data = f.read()
            team_dict['IMAGE:qrCode'] = img_data
            games = service.get_games(team.code)
            for i in range(len(games)):
                team_dict["game{}".format(i+1)] = games[i].name
                team_dict["gID{}".format(i+1)] = str(games[i].number)
            tb_merging.append(team_dict)

        with MailMerge(TEAM_ROADMAP_TEMPLATE) as document:
            document.merge_templates(tb_merging, separator='page_break')
            document.write(os.path.join(properties.PROJECT_ROOT, "team_roadmaps.docx"))


def generate_game_roadmaps():
    tb_merging = []
    with tempfile.TemporaryDirectory() as tmpdir:
        game_names = Game.objects().distinct('name')
        for name in game_names:
            game = Game.objects(name=name).first()
            game_dict = dict(gameName=name,
                             gID=str(game.number),
                             circuit=game.circuit)
            qr = pyqrcode.create(game.hash, error=QR_ERROR, version=QR_VERSION)
            qr_file = os.path.join(tmpdir, "game.png")
            qr.png(qr_file, scale=QR_SCALE, module_color=QR_COLOR, quiet_zone=QUIET_ZONE)
            with open(qr_file, 'r') as f:
                img_data = f.read()
            game_dict['IMAGE:qrCode'] = img_data

            i = 1
            for players in service.get_players(game.number):
                game_dict["teams{}".format(i)] = "{} - {}".format(players[0].code, players[1].code)
                i += 1
            tb_merging.append(game_dict)

        with MailMerge(GAME_ROADMAP_TEMPLATE) as document:
            document.merge_pages(tb_merging)
            document.write(os.path.join(properties.PROJECT_ROOT, "game_roadmaps.docx"))


