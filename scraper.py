# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random


class Scraper(object):
    def __init__(self,
                 headless: bool = True,
                 type_propositions: str = 'ecologie'):
        if type_propositions == 'ecologie':
            self.url = ('https://granddebat.fr/project/la-transition-ecologique/'
                        'collect/participez-a-la-recherche-collective-de-solutions-1')
        elif type_propositions == 'fiscalite':
            self.url = ('https://granddebat.fr/project/la-fiscalite-et-les-depenses-publiques/'
                        'collect/participez-a-la-recherche-collective-de-solutions-2')
        elif type_propositions == 'citoyennete':
            self.url = ('https://granddebat.fr/project/democratie-et-citoyennete-1/'
                        'collect/participez-a-la-recherche-collective-de-solutions')
        elif type_propositions == 'organisation':
            self.url = ('https://granddebat.fr/project/lorganisation-de-letat-et-des-services-publics/'
                        'collect/participez-a-la-recherche-collective-de-solutions-3')

        self.path_chromedriver = '/usr/local/bin/chromedriver'
        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        self.options = options

    def run(self, i=1):
        time.sleep(random.randint(1, 20)/10)
        driver = webdriver.Chrome(options=self.options)
        driver.get(self.url)
        soup = BeautifulSoup(self.driver.page_source)
        proposals = soup.select('div[class*="proposal-preview"]')
        infos = [Scraper.extract_proposal_info(x) for x in proposals]
        driver.close()
        return infos

    @staticmethod
    def extract_proposal_info(proposal: BeautifulSoup):
        ellipsis = proposal.find('div', {'class': 'ellipsis'})
        user_url = ellipsis.a['href']
        username = ellipsis.a.text
        date = ellipsis.find_all('span')[-1].text
        proprosal_a = proposal.find_all('a')[-1]
        proposal_url = proprosal_a['href']
        proposal_title = proprosal_a.text
        return {'username': username,
                'user_url': user_url,
                'date': date,
                'url': proposal_url,
                'title': proposal_title}

    def run_scroll(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)

        self.driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        self.scroll_down()
        while True:
            self.scroll_down()
            button = self.get_button()
            if button is None:
                break
            button.click()
            print('button text: {}'.format(button.text))
            button_text = button.text
            while button_text == 'Chargement...':
                self.scroll_down()
                button = self.get_button()
                if button is None:
                    break
                time.sleep(.1)
                try:
                    button_text = button.text
                except:
                    break
            if button_text == 'Voir plus de propositions':
                continue
            else:
                break
        soup = BeautifulSoup(self.driver.page_source)
        proposals = soup.select('div[class*="proposal-preview"]')
        infos = [Scraper.extract_proposal_info(x) for x in proposals]
        self.driver.close()
        return infos

    def scroll_down(self):
        self.driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        return None

    def get_button(self):
        buttons = self.driver.find_elements_by_css_selector(
            'button[class="btn btn-default"]')
        if type(buttons) is list and len(buttons) > 0:
            return buttons[-1]
        else:
            return None

c = Scraper()
infos = []
for i in range(500):
    print(i)
    infos += c.run_scroll()
