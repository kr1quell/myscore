from parse import Parser
from match import Match
from selenium import webdriver
from time import sleep
from datetime import datetime

top_leagues = ['БЕЛЬГИЯ: Высшая лига', 'ФРАНЦИЯ: Первая лига', 'РОССИЯ: Премьер-лига', 'АНГЛИЯ: Премьер-лига', 'ИСПАНИЯ: Примера',
               'ИТАЛИЯ: Серия А', 'ГЕРМАНИЯ: Бундеслига', 'УКРАИНА: Премьер-лига', 'УКРАИНА: Кубок Украины', 'ЕВРОПА: Лига Европы', 'ЕВРОПА: Лига чемпионов']


def write_match(match, g):
    # if match.Errors.__len__() != 0 or (not match.k_1 and not match.k_2) or (
    #         not match.points_team_1 and not match.points_team_2 and match.description.split(':')[0].lower() != 'европа'):
    #     pass
    if match.Errors.__len__() != 0 or (not match.k_1 and not match.k_2) or (
            match.points_team_1 is None and match.points_team_2 is None):
        pass
    else:
        record1 = [match.description, match.date, match.name_team_1,
                   str(match.k_1).replace('.', ','), str(match.position_team_1),
                   str(match.games_team_1), ", ".join(match.missing_players_1),
                   ", ".join(match.missing_players_q_1), str(match.points_team_1),
                   str(match.top_point_delta_1), str(match.departure_point_delta_1),
                   str(match.europe_point_delta_1), ", ".join(match.team_1_home),
                   ", ".join(match.form_team_1), str(match.scored_team_1), str(match.missed_team_1),
                   ", ".join(match.bombers_team_1), match.resource]
        sleep(.05)
        try:
            g.write(";".join(record1))
        except UnicodeEncodeError:
            pass
        record2 = [match.description, match.date, match.name_team_2,
                   str(match.k_2).replace('.', ','), str(match.position_team_2),
                   str(match.games_team_2), ", ".join(match.missing_players_2),
                   ", ".join(match.missing_players_q_2), str(match.points_team_2),
                   str(match.top_point_delta_2), str(match.departure_point_delta_2),
                   str(match.europe_point_delta_2), ", ".join(match.team_2_home),
                   ", ".join(match.form_team_2), str(match.scored_team_2), str(match.missed_team_2),
                   ", ".join(match.bombers_team_2), match.resource]
        sleep(.05)
        try:
            g.write(";".join(record2))
        except UnicodeEncodeError:
            pass


def filtered_matches(match, g):
    try:
        if (match.k_1 is not None and match.k_2 is not None and abs(float(match.k_1) - float(match.k_2)) >= 3) \
                or (match.games_team_1 is not None and match.games_team_2 is not None and int(match.games_team_1) > 6
                    and int(match.games_team_2) > 6) or match.description.split(' -')[0] in top_leagues:
            record1 = [match.description, match.date, match.name_team_1,
                       str(match.k_1).replace('.', ','), str(match.position_team_1),
                       str(match.games_team_1), ", ".join(match.missing_players_1),
                       ", ".join(match.missing_players_q_1), str(match.points_team_1),
                       str(match.top_point_delta_1), str(match.departure_point_delta_1),
                       str(match.europe_point_delta_1), ", ".join(match.team_1_home),
                       ", ".join(match.form_team_1), str(match.scored_team_1), str(match.missed_team_1),
                       ", ".join(match.bombers_team_1), match.resource]
            sleep(.05)
            record2 = [match.description, match.date, match.name_team_2,
                       str(match.k_2).replace('.', ','), str(match.position_team_2),
                       str(match.games_team_2), ", ".join(match.missing_players_2),
                       ", ".join(match.missing_players_q_2), str(match.points_team_2),
                       str(match.top_point_delta_2), str(match.departure_point_delta_2),
                       str(match.europe_point_delta_2), ", ".join(match.team_2_home),
                       ", ".join(match.form_team_2), str(match.scored_team_2), str(match.missed_team_2),
                       ", ".join(match.bombers_team_2), match.resource]
            sleep(.05)
            try:
                g.write(";".join(record1))
                g.write(";".join(record2))
            except UnicodeEncodeError:
                pass
        else:
            pass
    except ValueError:
        pass


def all_write(path, matches):
    g = open(path.split('.')[0] + ".csv", "w")
    header = ['Лига', 'Дата', 'Команда', 'Кф.', 'Місце', 'Ігри', 'Не гратиме', 'Під питанням', 'Очок', 'До 1  місця',
              'До зони виліта', 'До кубків', 'Очні зустрічі(дома)', 'Форма', 'Забиті', 'Пропущені', 'Бомбардири', 'url']

    g.write(";".join(header) + '\n')
    i = 0
    for match in matches:
        write_match(match, g)
        i += 1

    g.close()

    print("\'" + path.split('.')[0] + ".csv\"" + 'was created!')


def only_filtered(path, matches):
    g = open(path.split('.')[0] + " FILTERED.csv", "w")
    header = ['Лига', 'Дата', 'Команда', 'Кф.', 'Місце', 'Ігри', 'Не гратиме', 'Під питанням', 'Очок', 'До 1  місця',
              'До зони виліта', 'До кубків', 'Очні зустрічі(дома)', 'Форма', 'Забиті', 'Пропущені', 'Бомбардири', 'url']

    g.write(";".join(header) + '\n')
    i = 0
    for match in matches:
        filtered_matches(match, g)
        i += 1

    g.close()
    print("\'" + path.split('.')[0] + " FILTERED.csv\"" + 'was created!')


def main():
    timer1 = datetime.now()
    driver = webdriver.Chrome()
    regimes = ["today", "calendar", "live", "tomorrow"]
    parser = Parser(driver, regime=regimes[0])
    parser.check_all_matches(False)
    parser.info()
    parser.get_matches()
    path = parser.get_path()
    length = parser.get_file_len()
    matches = []

    driver = webdriver.Chrome()
    f = open(path, "r")

    count = 0
    i = 0
    for url in f:
        sleep(1)
        matches.append(Match(driver, url))
        matches[-1].execute()
        if count > 0 and i == count - 1:
            break
        i += 1

    f.close()
    driver.close()
    matches.sort(key=lambda m: m.date)
    sleep(0.05)
    ####################
    # all_write(path, matches)
    only_filtered(path, matches)
    ####################
    timer2 = datetime.now()
    print(timer2 - timer1)


if __name__ == '__main__':
    main()
