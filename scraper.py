# -*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class Scraper(object):
    def __init__(self,
                 headless: bool = True,
                 type_propositions: str = 'ecologie'):
        """ Scraper for granddebat.fr

        Args:
            headless: True does not show chrome
            type_propositions: theme between 'ecologie', 'fiscalite', 'citoyennete', 'organisation'
        """
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

    # def run(self, i=1):
    #     time.sleep(random.randint(1, 20)/10)
    #     driver = webdriver.Chrome(options=self.options)
    #     driver.get(self.url)
    #     soup = BeautifulSoup(self.driver.page_source)
    #     proposals = soup.select('div[class*="proposal-preview"]')
    #     infos = [Scraper.extract_proposal_info(x) for x in proposals]
    #     driver.close()
    #     return infos

    def run_scroll(self):
        """ Browse the propositions pages and scroll to retrieve the maximum number
        of propositions.

        Propositions are randomly shown, need to request the page multiple times
        """
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)
        time.sleep(2)
        print(self.driver.execute_script(
            'return document.readyState;'
        ))
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
        """ Scroll until the end of the page
        """
        self.driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        return None

    def get_button(self):
        """ Get the selector for more propositions
        """
        buttons = self.driver.find_elements_by_css_selector(
            'button[class="btn btn-default"]')
        if type(buttons) is list and len(buttons) > 0:
            return buttons[-1]
        else:
            return None

    @staticmethod
    def extract_proposal_info(proposal: BeautifulSoup):
        """ BeautifulSoup magic to extract relevant data such as
        the titles, links, owners of the propositions
        """
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


def scrap_proposition(url: str):
    """ Scrap the propositions
    """
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tab-content')))
        soup = BeautifulSoup(driver.page_source)
        content = soup.find('div', {'class': 'tab-content'})
        blocks = content.find_all('div', {'class': 'block'})
        q_and_a = [(block.h3.text, block.p.text)
                   if block.p is not None else (block.h3.text, '')
                   for block in blocks[1:-1]]
        driver.close()
        return q_and_a
    except:
        return None

# c = Scraper()
# infos = []
# for i in range(500):
#     print(i)
#     infos += c.run_scroll()


# from multiprocessing import Pool
# t = time.time()
# with Pool(6) as p:
#     results = p.map(scrap_proposition, urls)
# print(time.time()-t)

# r = []
# for url in urls:
#     print(url)
#     r.append(scrap_proposition(url))
