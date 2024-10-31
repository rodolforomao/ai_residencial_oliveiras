# utils/date_util.py

from datetime import datetime

class DateUtil:
    def convert_date_format(self, date_str):
        if date_str:
            # Parse the date string in YYYY-MM-DD format
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Return the date in DD/MM/YYYY format
            return date_obj.strftime('%d/%m/%Y')
        return None
