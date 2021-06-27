from parse import Parser
from datetime import datetime
from selenium import webdriver, common
from bs4 import BeautifulSoup
import time

time_to_sleep = .6


class Match:

    def __init__(self, driver, resource):
        self.driver = driver
        self.resource = resource

        self.Errors = []

        self.name_team_1 = ""
        self.id_team_1 = ""

        self.name_team_2 = ""
        self.id_team_2 = ""

        self.description = ""
        self.date = ""
        self.k_1 = ""
        self.k_2 = ""

        # форма команд(результаты последних матчей)
        self.form_team_1 = []
        self.form_team_2 = []

        self.team_1_home = []
        self.team_2_home = []

        # місце в таблиці
        self.position_team_1 = None
        self.position_team_2 = None

        # очки
        self.points_team_1 = None
        self.points_team_2 = None

        # к-сть ігор
        self.games_team_1 = None
        self.games_team_2 = None

        # забиті голи
        self.scored_team_1 = None
        self.scored_team_2 = None

        # пропущені голи
        self.missed_team_1 = None
        self.missed_team_2 = None

        self.top_point = -1
        self.europe_point = -1
        self.departure_point = -1

        self.top_point_delta_1 = None
        self.top_point_delta_2 = None

        self.europe_point_delta_1 = None
        self.europe_point_delta_2 = None

        self.departure_point_delta_1 = None
        self.departure_point_delta_2 = None

        self.missing_players_1 = []
        self.missing_players_2 = []
        self.missing_players_q_1 = []
        self.missing_players_q_2 = []

        self.bombers_team_1 = []
        self.bombers_team_2 = []

    def execute(self):
        self.driver.get(self.resource)
        time.sleep(time_to_sleep / 2)

        # айди команд
        self.id_teams()

        # инфа с главной страницы
        self.statistic()

        # игроки под вопросом, или которые не сыграют
        self.missing_players()

        # block with h2h
        try:
            h2h_btn = self.driver.find_element_by_css_selector("#a-match-head-2-head")
            h2h_btn.click()
            time.sleep(time_to_sleep)
            # h2h_info = self.driver.find_element_by_css_selector("#tab-h2h-overall").get_attribute("innerHTML")
            h2h_info = self.driver.find_element_by_css_selector("#tab-h2h-overall")
            # h2h_soup = BeautifulSoup(h2h_info, "html.parser")
            self.h2h(h2h_info)
        except common.exceptions.NoSuchElementException:
            pass
        except common.exceptions.ElementNotInteractableException:
            pass

        # block with table
        try:
            table_btn = self.driver.find_element_by_css_selector("#a-match-standings")
            table_btn.click()
            time.sleep(time_to_sleep)
            # table_info = self.driver.find_element_by_css_selector(".table__body").get_attribute("innerHTML") # rows___1vntYow
            table_info = self.driver.find_element_by_css_selector(".rows___1vntYow").get_attribute("innerHTML")
            table_soup = BeautifulSoup(table_info, "html.parser")
            self.table(table_soup)
        except common.exceptions.NoSuchElementException:
            pass
        except common.exceptions.ElementNotInteractableException:
            pass

    def statistic(self):
        # team1 name
        try:
            name1_info = self.driver.find_element_by_css_selector(".tname-home").get_attribute("innerHTML")
            name1_soup = BeautifulSoup(name1_info, "html.parser")
            self.name_team_1 = name1_soup.text.strip()
        except common.exceptions.NoSuchElementException:
            pass

        # team2 name
        try:
            name2_info = self.driver.find_element_by_css_selector(".tname-away").get_attribute("innerHTML")
            name2_soup = BeautifulSoup(name2_info, "html.parser")
            self.name_team_2 = name2_soup.text.strip()
        except common.exceptions.NoSuchElementException:
            pass

        print(self.name_team_1 + ' - ' + self.name_team_2)

        # description, league
        try:
            description_info = self.driver.find_element_by_css_selector(".description__country").get_attribute("innerHTML")
            description_soup = BeautifulSoup(description_info, "html.parser")
            self.description = description_soup.text
        except common.exceptions.NoSuchElementException:
            pass
        print(self.description)

        # description
        try:
            date_info = self.driver.find_element_by_css_selector("#utime").get_attribute("innerHTML")
            date_soup = BeautifulSoup(date_info, "html.parser")
            self.date = date_soup.text
        except common.exceptions.NoSuchElementException:
            pass
        print(self.date)

        # coefficients
        time.sleep(time_to_sleep / 4)
        try:
            k_info = self.driver.find_element_by_css_selector("#default-odds").get_attribute("innerHTML")
            k_soup = BeautifulSoup(k_info, "html.parser")
            k_list = k_soup.find_all("span", "odds-wrap")
            self.k_1 = k_list[0].text
            self.k_2 = k_list[2].text
        except common.exceptions.NoSuchElementException:
            pass
        print(self.k_1, self.k_2)

    def h2h(self, info):  # таблица очных встреч
        print("=====h2h start=====")
        time.sleep(time_to_sleep/2)

        home = info.find_element_by_css_selector(".h2h_home").get_attribute("innerHTML")
        home_soup = BeautifulSoup(home, "html.parser")
        home_matches = home_soup.select(".highlight")
        self.form_team_1 = self.each_match_h2h(home_matches)

        away = info.find_element_by_css_selector(".h2h_away").get_attribute("innerHTML")
        away_soup = BeautifulSoup(away, "html.parser")
        away_matches = away_soup.select(".highlight")
        self.form_team_2 = self.each_match_h2h(away_matches)

        head_to_head = info.find_element_by_css_selector(".h2h_mutual").get_attribute("innerHTML")
        head_to_head_soup = BeautifulSoup(head_to_head, "html.parser")

        rows = head_to_head_soup.find_all("tr", "highlight")
        for row in rows:
            names_html = row.find_all("td", "name")
            names = [names_html[0].span.text, names_html[1].span.text]
            if names[0] == self.name_team_1 and names[1] == self.name_team_2:
                self.team_1_home.append(row.find("span", "score").strong.text.replace(' ', '').replace(':', '-'))
            elif names[0] == self.name_team_2 and names[1] == self.name_team_1:
                self.team_2_home.append(row.find("span", "score").strong.text.replace(' ', '').replace(':', '-'))
        self.team_1_home = self.team_1_home[:5]
        self.team_2_home = self.team_2_home[:5]

        print("Форма " + self.name_team_1 + ': ' + ", ".join(self.form_team_1))
        print("Форма " + self.name_team_2 + ': ' + ", ".join(self.form_team_2))

        print("Результаты очных встреч (" + self.name_team_1 + " дома): " + ", ".join(self.team_1_home))
        print("Результаты очных встреч (" + self.name_team_2 + " дома): " + ", ".join(self.team_2_home))

        print("=====h2h end=====")

    def table(self, soup):  # таблица чемпионата(если не кубок)
        print("=====table start=====")
        time.sleep(time_to_sleep / 5)
        try:
            teams = soup.find_all('div', 'selected___2YWEk7U')
            # team1 = soup.find("div", "glib-participant-{}".format(self.id_team_1))
            name1 = teams[0].find('a', 'rowCellParticipantName___2pCMCKl').text.strip('')
            name2 = teams[1].find('a', 'rowCellParticipantName___2pCMCKl').text.strip('')
            team1 = None
            team2 = None
            if name1 == self.name_team_1 and name2 == self.name_team_2:
                team1 = teams[0]
                team2 = teams[1]
            elif name1 == self.name_team_2 and name2 == self.name_team_1:
                team1 = teams[1]
                team2 = teams[0]
        # team2 = soup.find("div", "glib-participant-{}".format(self.id_team_2))

            self.position_team_1 = int(team1.find("div", "rowCell___1QFnPje").text.strip().strip('.'))
            team1_fields = team1.find_all('span', 'rowCell___1QFnPje')
            self.games_team_1 = int(team1_fields[0].text.strip(''))
            self.scored_team_1 = int(team1_fields[4].text.strip('').split(':')[0])
            self.missed_team_1 = int(team1_fields[4].text.strip('').split(':')[1])
            self.points_team_1 = int(team1_fields[5].text.strip(''))

            # self.position_team_1 = int(team1.find("div", "table__cell--col_rank").text.strip().strip('.'))
            # self.points_team_1 = int(team1.find("div", "table__cell--points").text.strip())
            # self.games_team_1 = int(team1.find("div", "table__cell--matches_played").text.strip())
            # self.scored_team_1 = int(team1.find("div", "table__cell--goals").text.strip().split(':')[0])
            # self.missed_team_1 = int(team1.find("div", "table__cell--goals").text.strip().split(':')[1])

            self.position_team_2 = int(team2.find("div", "rowCell___1QFnPje").text.strip().strip('.'))
            team2_fields = team2.find_all('span', 'rowCell___1QFnPje')
            self.games_team_2 = int(team2_fields[0].text.strip(''))
            self.scored_team_2 = int(team2_fields[4].text.strip('').split(':')[0])
            self.missed_team_2 = int(team2_fields[4].text.strip('').split(':')[1])
            self.points_team_2 = int(team2_fields[5].text.strip(''))

            # self.position_team_2 = int(team2.find("div", "table__cell--col_rank").text.strip().strip('.'))
            # self.points_team_2 = int(team2.find("div", "table__cell--points").text.strip())
            # self.games_team_2 = int(team2.find("div", "table__cell--matches_played").text.strip())
            # self.scored_team_2 = int(team2.find("div", "table__cell--goals").text.strip().split(':')[0])
            # self.missed_team_2 = int(team2.find("div", "table__cell--goals").text.strip().split(':')[1])
        except AttributeError:
            err = "Another table"
            self.Errors.append(err)
            print(err)
        except IndexError:
            err = "Another table"
            self.Errors.append(err)
            print(err)

        self.additional_points(soup)

        try:
            if self.top_point != -1:
                self.top_point_delta_1 = self.top_point - self.points_team_1
                self.top_point_delta_2 = self.top_point - self.points_team_2
            if self.europe_point != -1:
                self.europe_point_delta_1 = self.europe_point - self.points_team_1
                self.europe_point_delta_2 = self.europe_point - self.points_team_2
            if self.departure_point != -1:
                self.departure_point_delta_1 = self.departure_point - self.points_team_1
                self.departure_point_delta_2 = self.departure_point - self.points_team_2
        except TypeError:
            err = "Error with calculating points"
            self.Errors.append(err)
            print(err)

        print(self.name_team_1 + ': место - ' + str(self.position_team_1) + ', игры - ' + str(self.games_team_1)
              + ', очки - ' + str(self.points_team_1) + ', забитых - ' + str(self.scored_team_1) + ', пропущенных - ' + str(self.missed_team_1) + ', ДО 1 МЕСТА: '
              + str(self.top_point_delta_1) + ', ДО ЕВРОКУБКОВ: ' + str(self.europe_point_delta_1) + ', ДО ВЫЛЕТА: ' +
              str(self.departure_point_delta_1))
        print(self.name_team_2 + ': место - ' + str(self.position_team_2) + ', игры - ' + str(self.games_team_2)
              + ', очки - ' + str(self.points_team_2) + ', забитых - ' + str(self.scored_team_2) + ', пропущенных - ' + str(self.missed_team_2) + ', ДО 1 МЕСТА: '
              + str(self.top_point_delta_2) + ', ДО ЕВРОКУБКОВ: ' + str(self.europe_point_delta_2) + ', ДО ВЫЛЕТА: ' +
              str(self.departure_point_delta_2))

        time.sleep(time_to_sleep / 4)
        try:
            self.bombers()
        finally:
            print("=====table end=====")

    def id_teams(self):
        try:
            id_info = self.driver.find_elements_by_css_selector(".tomyteams")
            id_1 = BeautifulSoup(id_info[0].get_attribute("innerHTML"), "html.parser")
            id_2 = BeautifulSoup(id_info[1].get_attribute("innerHTML"), "html.parser")
            self.id_team_1 = id_1.span["class"][1].split('_')[1]
            self.id_team_2 = id_2.span["class"][1].split('_')[1]
        except common.exceptions.NoSuchElementException:
            pass
        print('"' + self.id_team_1 + '" - "' + self.id_team_2 + '"')

    def missing_players(self):
        missing_players_info = self.driver.find_elements_by_css_selector("#missing-players")
        try:
            missing_players_soup = None
            if missing_players_info.__len__() > 0:
                for item in missing_players_info:
                    if BeautifulSoup(item.get_attribute("innerHTML"), "html.parser").tr.td.text == "Не сыграют":
                        missing_players_soup = BeautifulSoup(item.get_attribute("innerHTML"), "html.parser")
                        break

            missing_players_l = missing_players_soup.find_all("td", "fl")
            for mpl in missing_players_l:
                tmp = str(mpl.text).split("(")[0].split(' ')[0]
                if tmp:
                    self.missing_players_1.append(tmp)

            missing_players_r = missing_players_soup.find_all("td", "fr")
            for mpr in missing_players_r:
                tmp = str(mpr.text).split("(")[0].split(' ')[0]
                if tmp:
                    self.missing_players_2.append(tmp)
        except IndexError:
            pass
        except AttributeError:
            pass
        except common.exceptions.NoSuchElementException:
            pass

        print('Не сыграют в ' + self.name_team_1 + ':', ", ".join(self.missing_players_1))
        print('Не сыграют в ' + self.name_team_2 + ':', ", ".join(self.missing_players_2))

        try:
            missing_players_q_soup = None
            if missing_players_info.__len__() > 0:
                for item in missing_players_info:
                    if BeautifulSoup(item.get_attribute("innerHTML"), "html.parser").tr.td.text == "Под вопросом":
                        missing_players_q_soup = BeautifulSoup(item.get_attribute("innerHTML"), "html.parser")
                        break

            missing_players_q_l = missing_players_q_soup.find_all("td", "fl")
            for mpql in missing_players_q_l:
                tmp = str(mpql.text).split("(")[0].split(' ')[0]
                if tmp:
                    self.missing_players_q_1.append(tmp)

            missing_players_q_r = missing_players_q_soup.find_all("td", "fr")
            for mpqr in missing_players_q_r:
                tmp = str(mpqr.text).split("(")[0].split(' ')[0]
                if tmp:
                    self.missing_players_q_2.append(tmp)
        except IndexError:
            pass
        except AttributeError:
            pass
        except common.exceptions.NoSuchElementException:
            pass

        print('Под вопросом ' + self.name_team_1 + ':', ", ".join(self.missing_players_q_1))
        print('Под вопросом ' + self.name_team_2 + ':', ", ".join(self.missing_players_q_2))

    def each_match_h2h(self, matches):
        if matches.__len__() > 5:
            matches = matches[:5]
        form = []
        for match in matches:
            form.append(match.find("td", "winLose").a.text)
            # print(match["class"])
        return form

    def additional_points(self, soup):
        # matches = soup.find_all("div", "table__row") # row___3Gv59rA
        matches = soup.find_all("div", "row___3Gv59rA")
        time.sleep(.15)
        try:
            top_fields = matches[0].find_all('span', 'rowCell___1QFnPje')
            self.top_point = int(top_fields[5].text.strip(''))
        except ValueError:
            pass

        for match in matches:
            try:
                title = match.find("div", "rowCell___1QFnPje")['title']
                fields = match.find_all('span', 'rowCell___1QFnPje')
                if title.split('-')[0].strip() == "Проход дальше":
                    self.europe_point = int(fields[5].text.strip(''))
                    # self.europe_point = int(match.find("div", "table__cell--points").text.strip())
                if title.split('-')[0].strip() == "Зона вылета":
                    self.departure_point = int(fields[5].text.strip(''))
                    # self.departure_point = int(match.find("div", "table__cell--points").text.strip())
                    break
            except KeyError:
                continue
            except ValueError:
                pass
        print("1 место: " + str(self.top_point) + ", еврокубки: " + str(self.europe_point) + ", зона вылета: " + str(self.departure_point))

    def bombers(self):
        time.sleep(time_to_sleep)
        list_btn = self.driver.find_elements_by_css_selector('.tabs__tab')
        active_btm_bombers = None
        for item in list_btn:
            text = item.get_attribute("innerHTML")
            if text == 'Бомбардиры':
                active_btm_bombers = item
                break

        if not active_btm_bombers:
            return
        active_btm_bombers.click()
        time.sleep(time_to_sleep)

        bombers_info = self.driver.find_element_by_css_selector(".rows___1vntYow").get_attribute("innerHTML")
        bombers_soup = BeautifulSoup(bombers_info, "html.parser")
        time.sleep(time_to_sleep)
        bombers = bombers_soup.find_all('div', 'selected___2cSh0eE')
        bombers_1 = []
        bombers_2 = []
        for b in bombers:
            team_name = b.find('a', 'rowCellParticipant___1M24eEZ')
            if team_name.text == self.name_team_1:
                bombers_1.append(b)
            elif team_name.text == self.name_team_2:
                bombers_2.append(b)
        for bomber_1 in bombers_1[:4]:
            name1 = bomber_1.find('div', 'rowCellParticipant___1M24eEZ').a.text.split(' ')[0]
            goals1 = bomber_1.find('span', 'rowCellGoals___i4lkQZM').text.strip()
            result1 = goals1 + ' - ' + name1
            self.bombers_team_1.append(result1)
        for bomber_2 in bombers_2[:4]:
            name2 = bomber_2.find('div', 'rowCellParticipant___1M24eEZ').a.text.split(' ')[0]
            goals2 = bomber_2.find('span', 'rowCellGoals___i4lkQZM').text.strip()
            result2 = goals2 + ' - ' + name2
            self.bombers_team_2.append(result2)

        print('Бомбардиры в ' + self.name_team_1 + ': ' + ", ".join(self.bombers_team_1))
        print('Бомбардиры в ' + self.name_team_2 + ': ' + ", ".join(self.bombers_team_2))


def test():
    timer1 = datetime.now()

    driver = webdriver.Chrome()
    path = []

    path.append("https://www.flashscore.com.ua/match/rooY26WO/#match-summary")
    path.append("https://www.flashscore.com.ua/match/bNQG6onE/#match-summary")
    path.append("https://www.flashscore.com.ua/match/rJWZEPIS/#match-summary")
    path.append("https://www.flashscore.com.ua/match/0GI5SrmS/#match-summary")
    path.append("https://www.flashscore.com.ua/match/hhM98Ned/#match-summary")

    match1 = Match(driver, path[0])
    match1.execute()

    match2 = Match(driver, path[1])
    match2.execute()

    match3 = Match(driver, path[2])
    match3.execute()

    match4 = Match(driver, path[3])
    match4.execute()

    driver.close()

    timer2 = datetime.now()
    timer = timer2 - timer1
    return str(timer).split(':')[-1]


def main():
    timer1 = datetime.now()

    driver = webdriver.Chrome()
    path = ['https://www.flashscore.com.ua/match/faslqRU7/#match-summary',
            'https://www.flashscore.com.ua/match/ttobio9E/#match-summary',
            'https://www.flashscore.com.ua/match/lSaZA0w0/#match-summary',
            'https://www.flashscore.com.ua/match/IwMjJOVJ/#match-summary']
    # fXjuUeOt
    # path.append("https://www.flashscore.com.ua/match/fXjuUeOt/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/z3p2j5OK/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/ttobio9E/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/lSaZA0w0/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/veHBeLwD/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/804dWQm3/#match-summary")
    # path.append("https://www.flashscore.com.ua/match/fc0hX6Yd/#match-summary")
    match1 = Match(driver, path[0])
    match1.execute()

    # match2 = Match(driver, path[1])
    # match2.execute()
    #
    # match3 = Match(driver, path[2])
    # match3.execute()
    #
    # match4 = Match(driver, path[3])
    # match4.execute()

    driver.close()

    timer2 = datetime.now()
    print(timer2-timer1)
    # timer = []
    # for i in range(3):
    #     timer.append(test())
    # print(timer)


if __name__ == '__main__':
    main()