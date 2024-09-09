import sqlite3
from datetime import datetime, timedelta, UTC
from data_objects import Event, Server
class Events_DB:
    def __init__(self, path) -> None:
        self._connection = sqlite3.connect(path)
        self._cursor = self._connection.cursor()
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS Events (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              server_id INTEGER,
                              time DATETIME,
                              message TEXT);""")
        
        self._cursor.execute("""CREATE TABLE IF NOT EXISTS Servers (
                              server_id INTEGER  PRIMARY KEY,
                              channel_id INTEGER,
                              notification_time DATETIME,
                              role_id INTEGER);""")
    
    def add_event(self, server_id:int, timestamp:datetime, message:str=''):
        self._cursor.execute("""INSERT INTO Events(server_id, time, message) VALUES(?, ?, ?)""", (server_id, timestamp, message))
        self._connection.commit()
        id = self._cursor.lastrowid
        return id
    
    def add_server(self, server_id:int):
        self._cursor.execute("""INSERT INTO Servers(server_id, channel_id, notification_time, channel_id)
                             VALUES(?, NULL, NULL, NULL)""", (server_id, ))
        self._connection.commit()
        return True
    
    def modify_server(self, server_id:int, channel_id:int, notification_time: datetime, role_id: int):
        self._cursor.execute("""UPDATE Servers SET channel_id = ?, notification_time = ?, role_id = ?
                             WHERE server_id = ?""", (channel_id, notification_time, role_id, server_id))
        self._connection.commit()
        return True

    def get_next_event(self, server_id:int):
        res = self._cursor.execute("""SELECT * FROM Events WHERE server_id=? ORDER BY time ASC""", (server_id,))
        event = res.fetchone()
        if event != None:
            return Event(*event)
        else:
            return None

    def get_server(self, server_id:int):
        res = self._cursor.execute("""SELECT * FROM Servers WHERE server_id=?""", (server_id,))
        server = res.fetchone()
        if server != None:
            return Server(*server)
        else:
            return None


    def check_imminent_event(self, server_id:int):
        next_event = self.get_next_event(server_id)
        server = self.get_server(server_id)
        if (next_event == None or server == None):
            return None
        else:
            current_time = datetime.now(UTC)
            next_event.time = datetime.strptime(next_event.time, '%Y-%m-%d %H:%M:%S%z')
            if (next_event.time-current_time < timedelta(minutes=server.notification_time)):
                return (next_event, server)
            else:
                return None


    def clear_events():
        pass