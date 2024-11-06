
import unicodedata
import re

class StringUtil:
    
    def __init__(self):
        pass

    def normalize(self, s):
        s = s.lower()
        s = ''.join(char for char in unicodedata.normalize('NFKD', s) if not unicodedata.combining(char))
        s = re.sub(r'\W+', '', s)
        return s
