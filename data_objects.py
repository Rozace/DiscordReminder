from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    id: int
    server_id: int
    time: str
    message: str

@dataclass
class Server:
    server_id: int
    channel_id: int
    notification_time: int
    role_id: int