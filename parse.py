import time
import datetime
from bs4 import BeautifulSoup
from selenium import common


class Parser:
    resource = "https://www.flashscore.com.ua/"
    urls = []
    path = ""

    current_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def __init__(self, driver, regime="today", time_to_sleep=1, is_all=True, mode="scheduled", links_path="links.txt"):
        self.driver = driver  # инициализация драйвера
        self.time_to_sleep = time_to_sleep  # время задержки
        self.is_all = is_all  # открывать стрелки или нет

        if regime in ["today", "calendar", "live", "tomorrow"]:
            self.regime = regime
        else:
            self.regime = None

        if mode in ["scheduled", "live"]:  # расписание или лайв
            self.mode = mode
        else:
            self.mode = None

        if self.regime == "live":
            self.mode = "live"

        if self.regime == "calendar":
            self.check_all_matches(False)

        self.links_path = links_path  # файл с ссылками

    def check_all_matches(self, is_all):
        self.is_all = is_all

    def set_mode(self, mode):
        if mode in ["scheduled", "live"]:
            self.mode = mode
        else:
            self.mode = None

    def get_matches(self):  # получить все матчи (сегодня / на неделю)
        self.driver.get(self.resource)
        time.sleep(self.time_to_sleep*2)

        scheduled_click = self.driver.find_elements_by_css_selector(".tabs__tab")
        if self.regime == "today" or self.regime == "calendar" or self.regime == "tomorrow":
            scheduled_click[-1].click()  # кликнуть Расписание
        elif self.regime == "live":
            scheduled_click[1].click()  # кликнуть Live

        if self.regime == "today" or self.regime == "calendar":
            self.one_page_parse()  # парсинг одной страницы

        if self.regime == "tomorrow":
            try:
                next_btn = self.driver.find_element_by_css_selector(
                    ".calendar__direction.calendar__direction--tomorrow")
                next_btn.click()
                time.sleep(self.time_to_sleep / 2)
                self.one_page_parse()
            except common.exceptions.NoSuchElementException as err:
                pass

        if self.regime == "calendar":
            while True:
                try:
                    next_btn = self.driver.find_element_by_css_selector(".calendar__direction.calendar__direction--tomorrow")
                    next_btn.click()
                    time.sleep(self.time_to_sleep / 2)
                    self.one_page_parse()
                except common.exceptions.NoSuchElementException as err:
                    break

        if self.regime == "today":
            self.path = self.current_date.split(' ')[0] + " TODAY.txt"
        elif self.regime == "calendar":
            self.path = self.current_date.split(' ')[0] + " SCHEDULED.txt"
        elif self.regime == "tomorrow":
            self.path = self.current_date.split(' ')[0] + " TOMORROW.txt"
        elif self.regime == "live":
            self.path = self.current_date.split(' ')[0] + " " + self.current_date.split(' ')[1].replace(':', '-') + " LIVE.txt"
        self.write_urls(self.path)  # запись всех ссылок на матчи в файл
        self.driver.close()

    def one_page_parse(self):  # парсинг одной страницы
        if self.is_all:  # открывает стрелочки
            self.clicks_on_arrows(self.driver)
        time.sleep(self.time_to_sleep)

        table = self.driver.find_element_by_css_selector(".sportName.soccer").get_attribute("innerHTML")
        soup = BeautifulSoup(table, "html.parser")
        time.sleep(self.time_to_sleep / 10)

        # получает "коды" всех игр
        games = soup.select(".event__match.event__match--{}.event__match--oneLine".format(self.mode))
        # event__match event__match--live  event__match--oneLine

        for game in games:
            id_match = game['id'].split('_')[-1]  # id матча
            url = "https://www.flashscore.com.ua/match/{}/#match-summary".format(id_match)  # ссылка на матч
            self.urls.append(url)

    def write_urls(self, path):
        f = open(path, "w")  # запись в файл
        i = 0
        for url in self.urls:
            if i != self.urls.__len__() - 1:
                f.write(url + '\n')
            else:
                f.write(url)
            i += 1
        f.close()
        print("Ссылки({}) записаны в файл \"".format(self.urls.__len__()) + path + "\"")

    def clicks_on_arrows(self, browser):
        while True:
            try:
                click_btn = browser.find_element_by_css_selector(".event__expander.icon--expander.expand")
                click_btn.click()
                time.sleep(self.time_to_sleep / 4)
            except common.exceptions.ElementClickInterceptedException:
                continue
            except common.exceptions.StaleElementReferenceException:
                continue
            except common.exceptions.NoSuchElementException:
                break

    def info(self):
        print("Current date: " + self.current_date)
        print("Regime: " + self.regime)
        print("Mode: " + self.mode)
        if self.is_all:
            print("Check All: YES")
        else:
            print("Check All: NO")

    def get_path(self):
        return self.path

    def get_file_len(self):
        return self.urls.__len__()


# def main():
#     driver = webdriver.Chrome()
#     parser = Parser(driver, regime="calendar")
#     parser.info()
#     parser.get_matches()
#     path = parser.get_path()
#
#
# if __name__ == '__main__':
#     main()

