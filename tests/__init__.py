from datetime import datetime
from datetime import timedelta
from random import randint
from tests.helpers import *

TARGET_DATE = datetime.utcnow() + timedelta(days=randint(2, 10))
TARGET_DATE_OLD = datetime.utcnow() - timedelta(days=randint(2, 10))
