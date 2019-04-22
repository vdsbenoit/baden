# -*-coding:UTF-8 -*
import logging
import os
import tempfile

import pyqrcode
from docx import Document as Document_compose
from docx.shared import Mm
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, InlineImage

from model import service, properties
from model.game import Game
from model.team import Team

log = logging.getLogger('default')

LOOP_TEMPLATE = os.path.join(properties.DATA_DIR, "loop_template.docx")
TEAM_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "team_roadmap_template.docx")
GAME_ROADMAP_TEMPLATE = os.path.join(properties.DATA_DIR, "game_roadmap_template.docx")
QR_SCALE = 4
QR_SIZE = 37  # in mm
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
                qrCode=InlineImage(tpl, qr_file, width=Mm(QR_SIZE))
            )
            for i, match in enumerate(team.matches, 1):
                game_number = match.game_number
                context["game{}".format(i)] = Game.objects(number=game_number).get().name
                context["gId{}".format(i)] = str(game_number)

            tpl.render(context)
            team_file = os.path.join(tmpdir, "team{}.docx".format(team.code))
            tpl.save(team_file)
            files_to_merge.append(team_file)

        _combine_docx(target_file, files_to_merge)


def generate_game_roadmaps(target_file):
    files_to_merge = list()
    with tempfile.TemporaryDirectory() as tmpdir:
        for game in Game.objects():
            tpl = DocxTemplate(GAME_ROADMAP_TEMPLATE)

            qr = pyqrcode.create(game.hash, error=QR_ERROR, version=QR_VERSION)
            qr_file = os.path.join(tmpdir, "game.png")
            qr.png(qr_file, scale=QR_SCALE, module_color=QR_COLOR, quiet_zone=QUIET_ZONE)

            context = dict(
                gameName=game.name,
                gId=str(game.number),
                circuit=game.circuit,
                leader=game.leader,
                qrCode=InlineImage(tpl, qr_file, width=Mm(QR_SIZE))
            )

            for i, match in enumerate(game.matches, 1):
                context["players{}".format(i)] = "{} - {}".format(match.players_code[0], match.players_code[1])

            tpl.render(context)
            game_file = os.path.join(tmpdir, "game{}.docx".format(game.number))
            tpl.save(game_file)
            files_to_merge.append(game_file)

        _combine_docx(target_file, files_to_merge)
