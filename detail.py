from selenium import webdriver, common
from bs4 import BeautifulSoup
from time import sleep
from collections import defaultdict
from datetime import datetime

atr = "html.parser"


class Detail:
    def __init__(self, driver, link, count=7):
        self.driver = driver
        self.link = link
        self.count = count

        self.path = ""

        self.team_1_name = ""
        self.team_2_name = ""
        self.team_1_id = ""
        self.team_2_id = ""

        self.home_links = []
        self.away_links = []

        self.home_results = []
        self.away_results = []

    def run(self):
        self.get_names()

        self.get_links()

        print()
        for home_link in self.home_links:
            self.home_results.append(self.check(home_link, self.team_1_name))
        print()
        for away_link in self.away_links:
            self.away_results.append(self.check(away_link, self.team_2_name))

    def get_names(self):
        self.driver.get(self.link)
        sleep(0.5)

        home_info = self.driver.find_element_by_css_selector(".home-box").get_attribute("innerHTML")
        home_soup = BeautifulSoup(home_info, atr)
        self.team_1_name = home_soup.find("div", "tname__text").a.text
        self.team_1_id = home_soup.find("span", "toggleMyTeam")["class"][-1].split('_')[-1]
        print(self.team_1_name, self.team_1_id)

        away_info = self.driver.find_element_by_css_selector(".away-box").get_attribute("innerHTML")
        away_soup = BeautifulSoup(away_info, atr)
        self.team_2_name = away_soup.find("div", "tname__text").a.text
        self.team_2_id = away_soup.find("span", "toggleMyTeam")["class"][-1].split('_')[-1]
        print(self.team_2_name, self.team_2_id)

    def get_links(self):
        h2h_btn = self.driver.find_element_by_css_selector("#a-match-head-2-head")
        h2h_btn.click()
        sleep(0.5)

        home_info = self.driver.find_element_by_css_selector(".h2h_home").get_attribute("innerHTML")
        home_soup = BeautifulSoup(home_info, atr)
        self.home_links = self.links(home_soup)
        # print(self.home_links)
        away_info = self.driver.find_element_by_css_selector(".h2h_away").get_attribute("innerHTML")
        away_soup = BeautifulSoup(away_info, atr)
        self.away_links = self.links(away_soup)
        # print(self.home_links)

    def links(self, soup):
        full_urls = []
        urls = soup.find_all("tr", "highlight")[:self.count]
        for url in urls:
            id = url["onclick"].split(',')[0].split('(')[-1].strip('\'').split('_')[-1]
            full_url = "https://www.flashscore.com.ua/match/{}/#match-summary".format(id)
            full_urls.append(full_url)
        return full_urls

    def check(self, link, name):
        self.driver.get(link)
        sleep(0.5)
        try:
            sleep(.05)
            statistic_btn = self.driver.find_element_by_css_selector("#a-match-statistics")
            sleep(0.15)
            statistic_btn.click()
        except common.exceptions.NoSuchElementException:
            return

        home_info = self.driver.find_element_by_css_selector(".home-box").get_attribute("innerHTML")
        home_soup = BeautifulSoup(home_info, atr)
        home_name = home_soup.find("div", "tname__text").a.text
        home_id = home_soup.find("span", "toggleMyTeam")["class"][-1].split('_')[-1]

        away_info = self.driver.find_element_by_css_selector(".away-box").get_attribute("innerHTML")
        away_soup = BeautifulSoup(away_info, atr)
        away_name = away_soup.find("div", "tname__text").a.text
        away_id = away_soup.find("span", "toggleMyTeam")["class"][-1].split('_')[-1]

        id_ = [home_id, away_id]

        index = -1
        r_index = -1
        if name == home_name:
            index = 0
            r_index = 1
        elif name == away_name:
            index = 1
            r_index = 0

        score_info = self.driver.find_element_by_css_selector(".current-result").get_attribute("innerHTML")
        score_soup = BeautifulSoup(score_info, atr)
        score_ = score_soup.find_all("span", "scoreboard")
        score = [score_[0].text, score_[1].text]
        scored = score[index]
        missed = score[r_index]

        print('\n' + " - ".join(["/".join([home_name, home_id]), "/".join([away_name, away_id])]))
        print(" - ".join(score))

        sleep(0.40)
        statistics_info = self.driver.find_element_by_css_selector(".statContent").get_attribute("innerHTML")
        statistics = BeautifulSoup(statistics_info, atr)

        result_dict = {}
        d = self.get_statistic(statistics)
        if "Красные карточки" not in d:
            d["Красные карточки"] = ['0', '0']
        if "Желтые карточки" not in d:
            d["Желтые карточки"] = ['0', '0']

        for k in d:
            if k != "Красные карточки" or k != "Желтые карточки":
                # print(k, d[k][index])
                result_dict[k] = d[k][index]
            else:
                if int(d[k][index]) == 0:
                    # print(k, -int(d[k][r_index]))
                    result_dict[k] = -int(d[k][r_index])
                else:
                    # print(k, d[k])
                    result_dict[k] = d[k]

        sleep(0.2)
        try:
            table_btn = self.driver.find_element_by_css_selector("#a-match-standings")
            table_btn.click()
            sleep(0.35)
            info = self.driver.find_element_by_css_selector(".glib-participant-{}".format(id_[r_index])).get_attribute("innerHTML")
            info_soup = BeautifulSoup(info, atr)
            position = info_soup.find("div", "table__cell--rank").text.strip().strip('.')
        except common.exceptions.NoSuchElementException:
            position = '-Кубок-'

        return home_name, away_name, "--".join(score), scored, missed, position, result_dict

    def get_statistic(self, soup):
        keys = ["Владение мячом", "Офсайды", "Удары в створ", "Штрафные", "Фолы", "Угловые", "Сэйвы", "Красные карточки",
                "Желтые карточки", "Завершено передач", "Всего передач", "Опасные атаки"]
        rows = soup.find_all("div", "statRow")
        d = defaultdict(list)
        for row in rows:
            key = row.find("div", "statText--titleValue").text
            home_value = row.find("div", "statText--homeValue").text
            away_value = row.find("div", "statText--awayValue").text
            if key in keys:
                d[key] = [home_value, away_value]
        return d

    def write_in_file(self):
        self.path = self.team_1_name + ' - ' + self.team_2_name + '.csv'
        f = open(self.path, "w")
        header_names = [self.team_1_name, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', self.team_2_name]
        f.write(";".join(header_names) + '\n')
        header_info = ['Команди', 'Місце', 'Результат', 'Забито', 'Пропущено', '% володіння', 'Офсайди', 'Удари в площину',
                       'Штрафні', 'Кутові', 'Сейви', 'Передачі', 'Небезпечні атаки', 'Жовті', 'Червоні']
        f.write(";".join(header_info) + '; ; ' + ";".join(header_info) + '\n')
        length = self.home_results.__len__()
        for i in range(length):
            string1 = ''
            string2 = ''
            try:
                tmp1 = self.home_results[i][6]["Завершено передач"]
            except KeyError:
                try:
                    tmp1 = self.home_results[i][6]["Всего передач"]
                except KeyError:
                    tmp1 = '0'
                except TypeError:
                    tmp1 = '0'
            except TypeError:
                tmp1 = '0'

            try:
                tmp3 = self.home_results[i][6]["Штрафные"]
            except KeyError:
                try:
                    tmp3 = self.home_results[i][6]["Фолы"]
                except KeyError:
                    tmp3 = '0'
                except TypeError:
                    tmp3 = '0'
            except TypeError:
                tmp3 = '0'

            try:
                tmp5 = self.home_results[i][6]["Офсайды"]
            except KeyError:
                tmp5 = '0'
            except TypeError:
                tmp5 = '0'

            try:
                string1 = ";".join([self.home_results[i][0] + ' - ' + self.home_results[i][1], self.home_results[i][5],
                                   self.home_results[i][2], self.home_results[i][3], self.home_results[i][4],
                                    self.home_results[i][6]["Владение мячом"], tmp5,
                                    self.home_results[i][6]["Удары в створ"], tmp3,
                                    self.home_results[i][6]["Угловые"], self.home_results[i][6]["Сэйвы"],
                                    tmp1, self.home_results[i][6]["Опасные атаки"],
                                    self.home_results[i][6]["Желтые карточки"], self.home_results[i][6]["Красные карточки"]])
            except TypeError:
                pass
            try:
                tmp2 = self.away_results[i][6]["Завершено передач"]
            except KeyError:
                try:
                    tmp2 = self.away_results[i][6]["Всего передач"]
                except KeyError:
                    tmp2 = '0'
                except TypeError:
                    tmp2 = '0'
            except TypeError:
                tmp2 = '0'

            try:
                tmp4 = self.away_results[i][6]["Штрафные"]
            except KeyError:
                try:
                    tmp4 = self.away_results[i][6]["Фолы"]
                except KeyError:
                    tmp4 = '0'
                except TypeError:
                    tmp4 = '0'
            except TypeError:
                tmp4 = '0'

            try:
                tmp6 = self.away_results[i][6]["Офсайды"]
            except KeyError:
                tmp6 = '0'
            except TypeError:
                tmp6 = '0'

            try:
                string2 = ";".join([self.away_results[i][0] + ' - ' + self.away_results[i][1], self.away_results[i][5],
                                    self.away_results[i][2], self.away_results[i][3], self.away_results[i][4],
                                    self.away_results[i][6]["Владение мячом"], tmp6,
                                    self.away_results[i][6]["Удары в створ"], tmp4,
                                    self.away_results[i][6]["Угловые"], self.away_results[i][6]["Сэйвы"],
                                    tmp2, self.away_results[i][6]["Опасные атаки"],
                                    self.away_results[i][6]["Желтые карточки"],
                                    self.away_results[i][6]["Красные карточки"]])
            except TypeError:
                pass
            print(string1 + '; ; ' + string2)
            f.write(string1 + '; ; ' + string2 + '\n')
        f.close()

    def get_path(self):
        return self.path


def main():
    timer1 = datetime.now()
    driver = webdriver.Chrome()
    links = []
    # links.append("https://www.flashscore.com.ua/match/MBQA4rQ1/#match-summary")
    # links.append("https://www.flashscore.com.ua/match/f5lV1Nuh/#match-summary")
    links.append("https://www.flashscore.com.ua/match/f9rCTs9P/#match-summary")
    links.append("https://www.flashscore.com.ua/match/S2jQ5vHI/#match-summary")
    links.append("https://www.flashscore.com.ua/match/t6fU4bWO/#match-summary")
    pathes = []
    for link in links:
        detail = Detail(driver, link)
        detail.run()
        detail.write_in_file()
        path = detail.get_path()
        pathes.append(path)
    for path in pathes:
        print("\"" + path + '\" has done!')
    timer2 = datetime.now()
    print(timer2 - timer1)


if __name__ == '__main__':
    main()