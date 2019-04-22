# -*-coding:UTF-8 -*
from model import properties, service
from model.game import Game
from model.match import Match
from model.team import Team
import model


def add_cell(file, value=""):
    """
    Add a cell in the output table with the list separator specified in the properties
    :type value: Union[str, int]
    :param file: the output file
    :param value: the value to write in the cell
    """
    file.write("{}{}".format(value, properties.LIST_SEPARATOR))


def generate_games_summary_table(target_file):
    match_quantity = model.match.get_match_quantity()
    with open(target_file, 'w', encoding='ANSI') as f:
        add_cell(f, "Circuit")
        add_cell(f, "Numéro")
        add_cell(f, "Nom")
        add_cell(f, "Responsable")
        for i in range(1, match_quantity + 1):
            add_cell(f, i)
        f.write("\n")
        add_cell(f)
        add_cell(f)
        add_cell(f)
        add_cell(f)
        schedules = service.get_all_schedules()
        for schedule in schedules:
            add_cell(f, schedule)
        f.write("\n")
        for game in Game.objects().order_by('number'):
            add_cell(f, game.circuit)
            add_cell(f, game.number)
            add_cell(f, game.name)
            add_cell(f, game.leader)
            for match in game.matches:
                add_cell(f, "{} - {}".format(*match.players_code))
            f.write("\n")


def generate_sections_summary_table(target_file):
    match_quantity = model.match.get_match_quantity()
    sections = Team.objects().distinct('section')
    with open(target_file, 'w', encoding='ANSI') as f:
        add_cell(f, "ID")
        add_cell(f, "Section")
        for i in range(1, match_quantity + 1):
            add_cell(f, i)
        f.write("\n")
        add_cell(f)
        add_cell(f)
        schedules = service.get_all_schedules()
        for schedule in schedules:
            add_cell(f, schedule)
        f.write("\n")
        for section in sections:
            team_codes = list()
            teams = Team.objects(section=section).order_by('code')
            for team in teams:
                team_codes.append(team.code)
            add_cell(f, "{} - {}".format(team_codes[0], team_codes[-1]))
            add_cell(f, section)
            for i in range(1, match_quantity + 1):
                games = list()
                for team in teams:
                    for match in team.matches:
                        if match.time == i:
                            games.append(match.game_number)
                add_cell(f, ', '.join(str(x) for x in sorted(games)))
            f.write("\n")
