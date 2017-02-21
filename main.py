# *-* coding: utf-8 *-*
"""
This script retreives data from RunningAhead API and adds new(last) workout into google excel spreadsheet.
"""

import json
import logging.handlers
import datetime
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials


LOG_FILENAME = 'logging.log'
LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

# Set up a specific logger with our desired output level
logger = logging.getLogger('MainLogger')
logger.setLevel(logging.INFO)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=5)
handler.setFormatter(LOG_FORMATTER)
logger.addHandler(handler)


with open("settings/access_tokens.json") as f:
    local_settings_and_secrets = json.loads(f.read())


# Helper
def get_secret(setting, secrets=local_settings_and_secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
    raise Exception(error_msg)


def transorfm_date_format(date_to_transform):
    """Takes date_to_transform in format '2017-02-03' and transforms it to '2/3/2017' format"""
    dt = datetime.datetime.strptime(date_to_transform, '%Y-%m-%d')
    return '{0}/{1}/{2}'.format(dt.month, dt.day, dt.year)


# Runningahead API handler
class RunningAheadHandler:
    def __init__(self):
        self.payload = {
            'access_token': get_secret('mathias_account'),
            'fields': [10, 11, 12, 13, 20, 21, 22]
        }

    def get_workouts_list(self):
        """Get & return list with all workouts."""
        response = requests.get(
            "https://api.runningahead.com/rest/logs/me/workouts",
            params=self.payload,
            timeout=(20, 20)
        )
        print json.dumps(response.json(), indent=4)  # Debug
        return response.json()['data']['entries']

    def get_most_recent_workout_data(self):
        """Get & return most recent, last workout."""
        response = requests.get(
            "https://api.runningahead.com/rest/logs/me/workouts",
            params=self.payload,
            timeout=(20, 20)
        )
        # print json.dumps(response.json(), indent=4)  # Debug
        # raw_input()
        return response.json()['data']['entries']

    def get_date_from_workout_data(self, workout_data):
        return workout_data['date']


# Google spreadsheets handler
class GoogleSpreadsheetHandler:
    def __init__(self):
        scope = [
            'https://spreadsheets.google.com/feeds',
            # 'https://www.googleapis.com/auth/drive'
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name('settings/Analytics Code-d9b5f2ff02e5.json', scope)
        gc = gspread.authorize(credentials)
        sh = gc.open('Workout Metrics')
        self.worksheet = sh.sheet1

    @staticmethod
    def convert_seconds_to_hms(self, seconds_src):
        """Takes duration time in seconds and returns string in h:mm:ss format"""
        minutes, seconds = divmod(seconds_src, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d" % (hours, minutes, seconds)

    def get_last_row_num_in_sheet(self):
        list_of_lists = self.worksheet.get_all_values()
        return len(list_of_lists)

    def get_last_row_date(self, last_row_num):
        last_row_date = self.worksheet.cell(last_row_num, 1).value
        return last_row_date

    def append_workout_data_to_sheet(self, wkdata, last_row_num):
        """
        Cell names:
        A - Date
        B - Activity
        C - Workout Type
        D - Time of Day
        E - Distance
        F - Duration
        G - Course name
        :param wkdata:
        :param last_row_num: - in case of...
        :return:
        """
        new_row_to_add = []
        # Date
        try:
            new_row_to_add.append(wkdata['date'])
        except KeyError:
            new_row_to_add.append('')
        # Activity
        try:
            new_row_to_add.append(wkdata['activityName'])
        except KeyError:
            new_row_to_add.append('')
        # Workout Type
        try:
            new_row_to_add.append(wkdata['workoutName'])
        except KeyError:
            new_row_to_add.append('')
        # Time of Day
        try:
            new_row_to_add.append(wkdata['time'])
        except KeyError:
            new_row_to_add.append('')
        # Distance
        try:
            new_row_to_add.append(wkdata['details']['distance']['value'])
        except KeyError:
            new_row_to_add.append('')
        # Duration
        try:
            seconds_src = wkdata['details']['duration']
            new_row_to_add.append(self.convert_seconds_to_hms(self, seconds_src))
        except KeyError:
            new_row_to_add.append('')
        # Course name
        try:
            new_row_to_add.append(wkdata['course']['name'])
        except KeyError:
            new_row_to_add.append('')

        self.worksheet.append_row(new_row_to_add)


def main():
    """The main process handler. Retrieves data from runningahead account and populates google spreadhseet"""
    logger.info("Program started.")
    print "Program started."
    # Processing Runningahead Data
    try:
        runningahead_handler = RunningAheadHandler()
        last_runningahead_workout = runningahead_handler.get_most_recent_workout_data()[0]
        last_runningahead_workout_date = runningahead_handler.get_date_from_workout_data(last_runningahead_workout)
        last_runningahead_workout_date = transorfm_date_format(last_runningahead_workout_date)

        # Processing Google Spreadsheet
        spreadhseet_handler = GoogleSpreadsheetHandler()
        excel_last_row_num = spreadhseet_handler.get_last_row_num_in_sheet()
        excel_last_row_date = spreadhseet_handler.get_last_row_date(excel_last_row_num)

        if last_runningahead_workout_date != excel_last_row_date:
            print "Adding a new record into spreadsheet."
            logger.info("Adding a new record into spreadsheet.")
            spreadhseet_handler.append_workout_data_to_sheet(last_runningahead_workout, excel_last_row_num)
            print "New record successfully added to google spreadsheet."
            logger.info("New record successfully added to google spreadsheet.")
        else:
            print "There is no new records from runningahead api."
            logger.info("There is no new records from runningahead api.")
    except Exception as e:
        logger.info(e)

    print "Finished"
    logger.info("Program finished.")
    logger.info("= " * 50)

if __name__ == '__main__':
    main()
