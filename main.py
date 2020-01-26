from src import Extractor
from src import Planner
from dotenv import load_dotenv
import os

load_dotenv()


name = os.getenv("NAME")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'auth/client_secret.json'

# e = Extractor(name, email, password)
# e.delay = 2
# e.launchBrowser()
# e.login()
# e.goToPlanning()
# e.goToSchedule()
# e.displayMonth()
# e.monthPlanning()
# e.browser.close()

p = Planner(SCOPES, CREDENTIALS_FILE)
p.importPlanning("downloads/planning.ics")