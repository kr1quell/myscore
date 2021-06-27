from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import common, webdriver

hp = "html.parser"
league = ["РОССИЯ: КХЛ", "США: НХЛ"]


class Period:
    def __init__(self):
        self.scored = []
        self.missed = []
        self.sum_scored = 0
        self.sum_missed = 0
        self.average_scored = 0
        self.average_missed = 0

    def add_goals(self, scored, missed):
        self.scored.append(scored)
        self.missed.append(missed)

    def get_average(self):
        self.sum_scored = sum(self.scored)
        self.average_scored = self.sum_scored / len(self.scored)
        self.sum_missed = sum(self.missed)
        self.average_missed = self.sum_missed / len(self.missed)


class Match:
    def __init__(self, driver, link):
        self.driver = driver
        self.link = link
        self.home_name = ""
        self.away_name = ""
        self.home_id = ""
        self.away_id = ""
        self.home_k = None
        self.away_k = None
        self.lg = ""
        self.data = ""

        self.home_links = []
        self.away_links = []
        # форма
        self.home_winLose = []
        self.away_winLose = []
        # результаты
        self.home_results = []
        self.away_results = []

        self.home_dict = dict()
        self.away_dict = dict()

    def execute(self):
        description = self.driver.find_element_by_css_selector('.description').get_attribute("innerHTML")
        description_soup = BeautifulSoup(description, hp)
        description__country = description_soup.find('span', 'description__country')
        d_text = description__country.text
        self.lg = d_text.split(':')[0] + ': ' + d_text.split(':')[1].split('-')[0].strip(' ')
        self.data = description_soup.find('div', 'description__time').text

        # teams main info
        sleep(.2)
        home_box = self.driver.find_element_by_css_selector('.home-box').get_attribute("innerHTML")
        away_box = self.driver.find_element_by_css_selector('.away-box').get_attribute("innerHTML")

        home_soup = BeautifulSoup(home_box, hp)
        self.home_name = home_soup.find('a', 'participant-imglink').img['alt']
        self.home_id = home_soup.find('span', 'toggleMyTeam')['class'][1].split('_')[1]

        away_soup = BeautifulSoup(away_box, hp)
        self.away_name = away_soup.find('a', 'participant-imglink').img['alt']
        self.away_id = away_soup.find('span', 'toggleMyTeam')['class'][1].split('_')[1]

        sleep(.1)
        k = self.driver.find_element_by_css_selector("#default-odds").get_attribute("innerHTML")
        k_soup = BeautifulSoup(k, hp)
        kk = k_soup.find_all("span", "odds-wrap")
        self.home_k = kk[0].text
        self.away_k = kk[2].text

        print(self.lg + ' | ' + self.data + ' | ' + self.home_name + '(' + self.home_id + ')[' + self.home_k + '] - ' + self.away_name + '(' + self.away_id + ')[' + self.away_k + ']')
        sleep(.05)
        h2h_btn = self.driver.find_element_by_css_selector('#li-match-head-2-head')
        h2h_btn.click()
        sleep(.25)
        h2h = self.driver.find_elements_by_css_selector('.h2h-wrapper')
        sleep(.15)
        h2h_home_info = h2h[0].get_attribute("innerHTML")
        h2h_home_soup = BeautifulSoup(h2h_home_info, hp)
        h2h_away_info = h2h[1].get_attribute("innerHTML")
        h2h_away_soup = BeautifulSoup(h2h_away_info, hp)

        self.h2h(h2h_home_soup, h2h_away_soup, 5)
        team1_periods = self.each_team(self.home_links, 'home')
        team2_periods = self.each_team(self.away_links, 'away')
        team1_p_1 = Period()
        team1_p_2 = Period()
        team1_p_3 = Period()
        team2_p_1 = Period()
        team2_p_2 = Period()
        team2_p_3 = Period()

        # отримання середніх значень забитих і пропущених голів по періодам за останні ігри
        for item in team1_periods:
            count = 0
            for it in item:
                if count == 0:  # period 1
                    team1_p_1.add_goals(it.scored[0], it.missed[0])
                elif count == 1:  # period 2
                    team1_p_2.add_goals(it.scored[0], it.missed[0])
                elif count == 2:  # period 3
                    team1_p_3.add_goals(it.scored[0], it.missed[0])
                count += 1
        team1_p_1.get_average()
        team1_p_2.get_average()
        team1_p_3.get_average()
        self.home_dict = {
            'scored_1': team1_p_1.average_scored,
            'missed_1': team1_p_1.average_missed,

            'scored_2': team1_p_2.average_scored,
            'missed_2': team1_p_2.average_missed,

            'scored_3': team1_p_3.average_scored,
            'missed_3': team1_p_3.average_missed,

            'scored': (team1_p_1.sum_scored + team1_p_2.sum_scored + team1_p_3.sum_scored) / len(team1_p_1.scored),
            'missed': (team1_p_1.sum_missed + team1_p_2.sum_missed + team1_p_3.sum_missed) / len(team1_p_1.missed)
        }

        for item in team2_periods:
            count = 0
            for it in item:
                if count == 0:  # period 1
                    team2_p_1.add_goals(it.scored[0], it.missed[0])
                elif count == 1:  # period 2
                    team2_p_2.add_goals(it.scored[0], it.missed[0])
                elif count == 2:  # period 3
                    team2_p_3.add_goals(it.scored[0], it.missed[0])
                count += 1
        team2_p_1.get_average()
        team2_p_2.get_average()
        team2_p_3.get_average()
        self.away_dict = {
            'scored_1': team2_p_1.average_scored,
            'missed_1': team2_p_1.average_missed,

            'scored_2': team2_p_2.average_scored,
            'missed_2': team2_p_2.average_missed,

            'scored_3': team2_p_3.average_scored,
            'missed_3': team2_p_3.average_missed,

            'scored': (team2_p_1.sum_scored + team2_p_2.sum_scored + team2_p_3.sum_scored) / len(team2_p_1.scored),
            'missed': (team2_p_1.sum_missed + team2_p_2.sum_missed + team2_p_3.sum_missed) / len(team2_p_1.missed)
        }

    def h2h(self, h2h_home, h2h_away, n):
        rows_home = h2h_home.find_all('tr', 'highlight')[:n]
        rows_away = h2h_away.find_all('tr', 'highlight')[:n]
        for r_h in rows_home:
            match_id = r_h['onclick'].split('\'g_0_')[1].split(',')[0].strip('\'')
            url = "https://www.flashscore.com.ua/match/{}/#match-summary".format(match_id)
            self.home_links.append(url)

            win_lose = r_h.find('td', 'winLose').text
            self.home_winLose.append(win_lose)

            res = str(r_h.find('span', 'score').text).replace(' : ', '-').split('(')[0]
            self.home_results.append(res)

        for r_a in rows_away:
            match_id = r_a['onclick'].split('\'g_0_')[1].split(',')[0].strip('\'')
            url = "https://www.flashscore.com.ua/match/{}/#match-summary".format(match_id)
            self.away_links.append(url)

            win_lose = r_a.find('td', 'winLose').text
            self.away_winLose.append(win_lose)

            res = str(r_a.find('span', 'score').text).replace(' : ', '-').split('(')[0]
            self.away_results.append(res)

        for i in range(n):
            print('[' + self.home_winLose[i] + '] ' + self.home_results[i] + ' | [' + self.away_winLose[i] + '] ' + self.away_results[i])

    def each_team(self, links, place):
        lst = []
        for link in links:
            self.driver.get(link)
            sleep(.5)
            page = self.driver.find_element_by_css_selector('#content-all').get_attribute("innerHTML")
            page_soup = BeautifulSoup(page, hp)
            ids = page_soup.find_all('span', 'toggleMyTeam')
            id1 = ids[0]['class'][1].split('_')[1]
            id2 = ids[1]['class'][1].split('_')[1]
            index = ''
            if id1 == self.home_id or id1 == self.away_id:
                index = 'home'
            elif id2 == self.home_id or id2 == self.away_id:
                index = 'away'

            index_back = ''
            if index == 'home':
                index_back = 'away'
            elif index == 'away':
                index_back = 'home'

            sleep(.15)
            try:
                core = page_soup.find('div', 'detailMS')
                sleep(.1)
                rows = core.find_all('div', recursive=False)
                scored = 0
                missed = 0
                period_1 = Period()
                period_2 = Period()
                period_3 = Period()
                for row in rows:
                    if 'stage-15' in row['class']:
                        period_1.add_goals(scored, missed)
                        scored = 0
                        missed = 0
                    elif 'stage-16' in row['class']:
                        period_2.add_goals(scored, missed)
                        scored = 0
                        missed = 0
                    elif 'stage-6' in row['class']:
                        period_3.add_goals(scored, missed)
                        break
                    if rows.index(row) == len(rows) - 1:
                        if 'incidentRow--{}'.format(index) in row['class']:
                            goal = row.find('span', 'hockey-ball')
                            if goal:
                                scored += 1
                        if 'incidentRow--{}'.format(index_back) in row['class']:
                            goal = row.find('span', 'hockey-ball')
                            if goal:
                                missed += 1
                        period_3.add_goals(scored, missed)
                        break
                    if 'incidentRow--{}'.format(index) in row['class']:
                        goal = row.find('span', 'hockey-ball')
                        if goal:
                            scored += 1
                    if 'incidentRow--{}'.format(index_back) in row['class']:
                        goal = row.find('span', 'hockey-ball')
                        if goal:
                            missed += 1
                print("_I_     Забито: {} | Пропущено: {}".format(period_1.scored[0], period_1.missed[0]))
                print("_II_    Забито: {} | Пропущено: {}".format(period_2.scored[0], period_2.missed[0]))
                print("_III_   Забито: {} | Пропущено: {}".format(period_3.scored[0], period_3.missed[0]))
                lst.append([period_1, period_2, period_3])
            except AttributeError:
                pass
            except IndexError:
                pass
            print('')
        return lst


class Hockey:
    def __init__(self, driver, n=0):
        self.driver = driver
        self.n = n
        self.resource = 'https://www.flashscore.com.ua/hockey/'
        self.current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.path = self.current_date.split(' ')[0] + "_HOCKEY.csv"
        self.links = []
        self.matches = []

    def get_matches(self):
        self.driver.get(self.resource)
        sleep(1)
        scheduled_click = self.driver.find_elements_by_css_selector(".tabs__tab")
        scheduled_click[-1].click()

        ################################################################
        for i in range(self.n):
            try:
                sleep(.75)
                click_btn = self.driver.find_element_by_css_selector(".calendar__direction--tomorrow")
                click_btn.click()
                sleep(.5)
            except common.exceptions.ElementClickInterceptedException:
                pass
            except common.exceptions.StaleElementReferenceException:
                pass
            except common.exceptions.NoSuchElementException:
                break
        ################################################################

        table = self.driver.find_element_by_css_selector(".sportName.hockey").get_attribute("innerHTML")
        table_soup = BeautifulSoup(table, "html.parser")
        games = table_soup.find_all('div', 'event__match--scheduled')
        for game in games:
            id = game['id'].split('_')[-1]
            self.links.append("https://www.flashscore.com.ua/match/{}/#match-summary".format(id))

    def check_all_matches(self):
        for link in self.links:
            self.driver.get(link)
            sleep(.3)
            description = self.driver.find_element_by_css_selector('.description').get_attribute("innerHTML")
            description_soup = BeautifulSoup(description, hp)
            description__country = description_soup.find('span', 'description__country')
            d_text = description__country.text
            d_text = d_text.split(':')[0] + ': ' + d_text.split(':')[1].split('-')[0].strip(' ')

            if d_text == "ГЕРМАНИЯ: ДЕЛ":
                continue

            if d_text not in league:
                break

            match = Match(self.driver, link)
            match.execute()
            self.matches.append(match)

    def write_matches(self):
        self.matches.sort(key=lambda m: m.data)
        header = ['Ліга', 'Дата', 'Команда', 'Кф', 'Форма', 'Рез-ти', 'I забито', 'I проп', 'II забито', 'II проп', 'III забито', 'III проп', 'ЗАБИТО', 'ПРОП', 'url']
        f = open(self.path, 'w')
        f.write(';'.join(header) + '\n')
        # home_name | away_name
        # home_id | away_id
        # home_k | away_k
        # lg | data
        # home_links | away_links
        # home_winLose | away_winLose
        # home_results | away_results
        # home_dict | away_dict  ( scored_1 : missed_1 )
        for match in self.matches:
            lg = match.lg
            data = match.data
            link = match.link
            team1 = match.home_name
            team2 = match.away_name
            k_1 = str(match.home_k).replace('.', ',')
            k_2 = str(match.away_k).replace('.', ',')
            f_1 = ', '.join(match.home_winLose)
            f_2 = ', '.join(match.away_winLose)
            res_1 = ', '.join(match.home_results)
            res_2 = ', '.join(match.away_results)
            # 1 period 1 team
            t1_g1 = str(match.home_dict['scored_1']).replace('.', ',')
            t1_m1 = str(match.home_dict['missed_1']).replace('.', ',')
            # 1 period 2 team
            t2_g1 = str(match.away_dict['scored_1']).replace('.', ',')
            t2_m1 = str(match.away_dict['missed_1']).replace('.', ',')
            # 2 period 1 team
            t1_g2 = str(match.home_dict['scored_2']).replace('.', ',')
            t1_m2 = str(match.home_dict['missed_2']).replace('.', ',')
            # 2 period 2 team
            t2_g2 = str(match.away_dict['scored_2']).replace('.', ',')
            t2_m2 = str(match.away_dict['missed_2']).replace('.', ',')
            # 3 period 1 team
            t1_g3 = str(match.home_dict['scored_3']).replace('.', ',')
            t1_m3 = str(match.home_dict['missed_3']).replace('.', ',')
            # 3 period 2 team
            t2_g3 = str(match.away_dict['scored_3']).replace('.', ',')
            t2_m3 = str(match.away_dict['missed_3']).replace('.', ',')

            t1_scored = str(match.home_dict['scored']).replace('.', ',')
            t2_scored = str(match.away_dict['scored']).replace('.', ',')

            t1_missed = str(match.home_dict['missed']).replace('.', ',')
            t2_missed = str(match.away_dict['missed']).replace('.', ',')

            record1 = [lg, data, team1, k_1, f_1, res_1, t1_g1, t1_m1, t1_g2, t1_m2, t1_g3, t1_m3, t1_scored, t1_missed, link]
            record2 = [lg, data, team2, k_2, f_2, res_2, t2_g1, t2_m1, t2_g2, t2_m2, t2_g3, t2_m3, t2_scored, t2_missed, link]

            try:
                f.write(';'.join(record1) + '\n')
                f.write(';'.join(record2) + '\n\n')
            except UnicodeEncodeError:
                pass
        f.close()


def main():
    timer1 = datetime.now()
    driver = webdriver.Chrome()
    hockey = Hockey(driver, 1)
    print(hockey.current_date)
    hockey.get_matches()
    hockey.check_all_matches()
    driver.close()
    hockey.write_matches()
    timer2 = datetime.now()
    print('Файл \'{}\' створено! Пройшло {}'.format(hockey.path, timer2-timer1))


if __name__ == '__main__':
    main()
