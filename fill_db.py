from repository.repository import database
import random
from datetime import *
def random_str(l):
    pool ="qwertyuiopasdfghjklzxcvbnmWERTYUIOPASDFGHJKLZXCVBNM"
    s = ""
    for i in range(l):
        s += random.choice(pool)
    return s

database.init("database.db")

for i in range(100):
    delta = timedelta(days=3*i)
    now = datetime.now()
    database._db.insert("UserDiagram", {
        "userId": 477114347496407040,
        "diagramId": random_str(16),
        "diagramName": random_str(7),
        "created": 1667000000,
        "updated": int((now - delta).timestamp())
    })