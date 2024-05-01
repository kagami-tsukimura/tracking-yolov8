from typing import Annotated

from database.database import SessionLocal, get_db
from fastapi import Depends


class Dependencies:
    def __init__(self):
        self.DBDependency = Annotated[SessionLocal, Depends(get_db)]

    def get_db_dependency(self):
        return self.DBDependency
