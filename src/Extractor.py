# -*- coding: utf-8 -*-

# @Author: Stormix - Anas Mazouni
# @Date:   2020-01-26
# @Email:  anas.mazouni@stormix.co
# @Project: OnBoardPlanning
# @Website: https://stormix.co

# Import Some Python Modules

import inspect
import sys
import os
import time
from sys import platform
import re
from datetime import datetime
import shutil

# Import self.browser modules

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.keys import Keys


class Extractor:
    # Pronote Class Attributes
    delay = 5
    url = "https://onboard.ec-nantes.fr/faces/Login.xhtml"
    planning_url = "https://onboard.ec-nantes.fr/faces/Planning.xhtml"
    username_input_id = "username"
    password_input_id = "password"
    login_button_class = "bouton-connexion"
    browser = None
    name = None

    def __init__(self, name, email, password):
        self.name = name
        self.username = email
        self.password = password

    def goTo(self, link):
        self.browser.get(link)
        time.sleep(self.delay)

    def launchBrowser(self, headless=False):
        # Initiate the self.browser webdriver
        currentfolder = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        # Check which operating system is being used !
        if platform == "linux" or platform == "linux2":
            # linux
            chrome_driver = currentfolder+"/../drivers/chromedriver"
        elif platform == "win32":
            # Windows
            chrome_driver = "drivers/chromedriver.exe"
        print("Chrome Driver Location : "+chrome_driver)
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": currentfolder,
            'profile.default_content_setting_values.automatic_downloads': 2,
        })
        options.add_argument("start-maximized") # open Browser in maximized mode
        options.add_argument("disable-infobars") # disabling infobars
        options.add_argument("--disable-extensions") # disabling extensions
        options.add_argument("--disable-gpu") # applicable to windows os only
        options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
        options.add_argument("--no-sandbox") # Bypass OS security model
        if(headless):
            options.add_argument('headless')
            options.add_argument('window-size=1280,800')
            options.add_argument('disable-gpu')
            options.add_argument('allow-insecure-localhost')
        self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.get(self.url)
        print("Browser Initiated !")
        print("Loading .. " + self.url, end=' ')
        time.sleep(self.delay)
        print('[DONE]')

    def login(self):
        if self.isLoggedIn():
            print("Already logged In!")
            return
        # Fill in the login form
        self.browser.find_element_by_id(
            self.username_input_id).send_keys(self.username)
        self.browser.find_element_by_id(
            self.password_input_id).send_keys(self.password)
        # Click the connect buttun
        print("Logging in ...", end=" ")
        self.browser.find_element_by_class_name(
            self.login_button_class).click()
        time.sleep(self.delay)
        if(self.isLoggedIn()):
            print('[DONE]')
        else:
            print('[FAILED] ..retrying')
            self.refresh()
            time.sleep(self.delay)
            self.login()

    def isLoggedIn(self):
        try:
            NameElement = self.browser.find_element_by_css_selector(
                '.menuMonCompte > ul > li.ui-widget-header.ui-corner-all > h3')
            return self.name in self.browser.execute_script("return arguments[0].textContent", NameElement).lower()
        except NoSuchElementException as e:
            return False

    def goToPlanning(self):
        try:
            element = self.browser.find_element_by_xpath(
                "//*[contains(text(), 'Planning')]")
            element.click()
            time.sleep(self.delay)
        except NoSuchElementException as e:
            print("Failed to goToPlanning(): NoSuchElement")
            time.sleep(self.delay)
            self.goToPlanning()
        except ElementNotVisibleException as e:
            print("Failed to goToPlanning(): ElementNotVisible")
            time.sleep(self.delay)
            self.goToPlanning()

    def goToSchedule(self):
        try:
            element = self.browser.find_element_by_xpath(
                "//*[contains(text(), 'My schedule')]")
            element.click()
            time.sleep(self.delay)
        except NoSuchElementException as e:
            print("Failed to goToSchedule(): NoSuchElement")
            time.sleep(self.delay)
            self.goToSchedule()
        except ElementNotVisibleException as e:
            print("Failed to goToSchedule(): ElementNotVisible")
            time.sleep(self.delay)
            self.goToSchedule()

    def displayMonth(self):
        try:
            element = self.browser.find_element_by_xpath(
                "//*[contains(text(), 'Month')]")
            element.click()
            time.sleep(self.delay)
        except NoSuchElementException as e:
            print("Failed to displayMonth(): NoSuchElement")
            time.sleep(self.delay)
            self.displayMonth()

    def monthPlanning(self, filename):
        try:
            element = self.browser.find_element_by_xpath(
                "//*[@title='Download']")
            element.click()
            time.sleep(self.delay)
            return self.moveToDownloads(filename)
        except NoSuchElementException as e:
            print("Failed to monthPlanning(): NoSuchElement")
            return False

    def moveToDownloads(self, filename):
        print("Saving planning.ics to downloads/{}".format(filename))
        shutil.move("src/planning.ics", "downloads/{}".format(filename))
        return "downloads/{}".format(filename)

    def refresh(self):
        self.browser.refresh()
