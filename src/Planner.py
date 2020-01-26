import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ics import Calendar
import arrow

class Planner:
    scopes = None
    creds = None
    service = None
    calendar_id = None
    calendar_name = None
    debug = True

    def __init__(self, scopes, creds, calendar='ECN Edt by OnBoardPlanning', debug=True):
        self.scopes = scopes
        self.creds = creds
        self.calendar_name = calendar
        self.debug = debug

    def log(self, msg):
        if self.debug:
            print(msg)

    def get_calendar_service(self):
        creds = None
        if os.path.exists('auth/token.pickle'):
            with open('auth/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds, self.scopes)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('auth/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_service(self):
        if not self.service:
            self.get_calendar_service()
        return self.service

    def list_calendars(self):
        service = self.get_service()
        # Call the Calendar API
        self.log('Getting list of calendars:')
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])

        if not calendars:
            self.log('No calendars found.')
        for calendar in calendars:
            summary = calendar['summary']
            if summary == self.calendar_name:
                self.calendar_id = calendar['id']
                if not self.debug:
                    break
            primary = "Primary" if calendar.get('primary') else ""
            onboard = "OnBoard Calendar" if summary == self.calendar_name else ""
            self.log("%s\t%s\t%s\t%s" %
                     (summary, calendar['id'], primary, onboard))

    def list_events(self, calendar_id, maxResults=10, orderBy="startTime"):
        service = self.get_service()
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self.log('Getting List of '+str(maxResults)+' events')
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=maxResults, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            self.log('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            self.log(start, event['summary'])

    def clear_calendar(self):
        service = self.get_service() 
        if not self.calendar_id:
            # raise Exception
            return False
            self.log("Calendar is not set!")
        else:
            page_token = None
            while True:
              events = service.events().list(calendarId=self.calendar_id, pageToken=page_token).execute()
              for event in events['items']:
                self.log('Deleting: Event #{} - {}'.format(event['id'], event['summary']))
                service.events().delete(calendarId=self.calendar_id, eventId=event['id']).execute()
              page_token = events.get('nextPageToken')
              if not page_token:
                break
            return True
    def get_calendar(self):
        service = self.get_service()
        # Check if already exists
        self.list_calendars()
        if self.calendar_id:
            self.log("Calendar exists!")
            return self.calendar_id
        else:
            self.log("Calendar doesn't exist! Creating it ..")
            calendar = {
                'summary': self.calendar_name,
                'description': 'An auto-generated ECN edt using OnBoard Planning',
                'timeZone': 'Europe/Paris'
            }
            created_calendar = service.calendars().insert(body=calendar).execute()
            self.calendar_id = created_calendar['id']
            self.log("Created calendar #" + created_calendar['id'])
            return self.calendar_id

    def is_empty(self):
        service = self.get_service()
        events = service.events().list(
            calendarId=self.get_calendar(), pageToken=None).execute()
        count = len(events['items'])
        self.log("Calendar contains {} events.".format(count))
        return count == 0

    def create_event(self, event, calendar):
        event = {
            'id': event.uid,
            'summary': event.name,
            'location': event.location,
            'description': event.description,
            'start': {
                'dateTime': event.begin.naive.isoformat(),
                'timeZone': 'Europe/Paris',
            },
            'end': {
                'dateTime': event.end.naive.isoformat(),
                'timeZone': 'Europe/Paris',
            },
            # 'recurrence': [
            #     'RRULE:FREQ=DAILY;COUNT=2'
            # ],
            'reminders': {
                'useDefault': True,
                # 'overrides': [
                #     {'method': 'email', 'minutes': 24 * 60},
                #     {'method': 'popup', 'minutes': 10},
                # ],
            },
        }
        service = self.get_service()
        event = service.events().insert(calendarId=calendar, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))

    def importPlanning(self, planning):
        with open(planning, 'r') as f:
            data = f.read()
        c = Calendar(data)
        if not self.is_empty():
          self.log("Clearing calendar!")
          self.clear_calendar()
        calendar = self.get_calendar()
        for event in c.events:
            self.create_event(event, calendar)
