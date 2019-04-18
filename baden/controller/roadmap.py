# -*-coding:UTF-8 -*
import logging
import os
import tempfile

import pyqrcode
from docx import Document as Document_compose
from docx.shared import Mm
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, InlineImage
from mailmerge import MailMerge

from model import service, properties
from model.game import Game
from model.team import Team

log = logging.getLogger('default')

LOOP_TEMPLATE = os.path.join(properties.DATA_DIR, "loop_template.docx")
TEAM_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "team_roadmap_template.docx")
GAME_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "game_roadmap_template.docx")
QR_SCALE = 4
QUIET_ZONE = 1
QR_COLOR = (43, 114, 84)
QR_VERSION = 4
QR_ERROR = 'Q'


def _combine_docx(target_file, files):
    master = Document_compose(files[0])
    composer = Composer(master)
    for i in range(1, len(files)):
        doc_temp = Document_compose(files[i])
        composer.append(doc_temp)
    composer.save(target_file)


def generate_team_roadmaps(target_file):
    files_to_merge = list()
    with tempfile.TemporaryDirectory() as tmpdir:
        for team in Team.objects():
            tpl = DocxTemplate(TEAM_ROADMAP_TEMPLATE)

            qr = pyqrcode.create(team.hash, error=QR_ERROR, version=QR_VERSION)
            qr_file = os.path.join(tmpdir, "team.png")
            qr.png(qr_file, scale=QR_SCALE, module_color=QR_COLOR, quiet_zone=QUIET_ZONE)

            context = dict(
                section=team.section,
                teamCode=team.code,
                qrCode=InlineImage(tpl, qr_file, width=Mm(37))
            )
            games = service.get_games(team.code)
            for i, game in enumerate(games, 1):
                context["game{}".format(i)] = games.name
                context["gId{}".format(i)] = str(games.number)

            tpl.render(context)
            team_file = os.path.join(tmpdir, "team{}.docx".format(team.code))
            tpl.save(team_file)
            files_to_merge.append(team_file)

        _combine_docx(target_file, files_to_merge)


def generate_game_roadmaps(target_file):
    files_to_merge = list()
    with tempfile.TemporaryDirectory() as tmpdir:
        game_names = Game.objects().distinct('name')
        for name in game_names:
            game = Game.objects(name=name).first()
            tpl = DocxTemplate(GAME_ROADMAP_TEMPLATE)

            qr = pyqrcode.create(game.hash, error=QR_ERROR, version=QR_VERSION)
            qr_file = os.path.join(tmpdir, "game.png")
            qr.png(qr_file, scale=QR_SCALE, module_color=QR_COLOR, quiet_zone=QUIET_ZONE)

            context = dict(
                gameName=name,
                gID=str(game.number),
                circuit=game.circuit,
                qrCode=InlineImage(tpl, qr_file, width=Mm(37))
            )

            for i, players in enumerate(service.get_players(game.number), 1):
                context["teams{}".format(i)] = "{} - {}".format(players[0].code, players[1].code)

            tpl.render(context)
            game_file = os.path.join(tmpdir, "team{}.docx".format(team.code))
            tpl.save(game_file)
            files_to_merge.append(game_file)

        _combine_docx(target_file, files_to_merge)
