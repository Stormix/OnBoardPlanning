from src import Extractor
from dotenv import load_dotenv
import os

load_dotenv()


name = os.getenv("NAME")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
e = Extractor(name, email, password)
e.delay = 2
e.launchBrowser()
e.login()
e.goToPlanning()
e.goToSchedule()
e.displayMonth()
e.monthPlanning()
e.browser.close()