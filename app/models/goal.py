from sqlalchemy.orm import Mapped, mapped_column
from ..db import db

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    def to_dict(self): 
        goal_dict = {
            "id": self.id,
            "title": self.title,
        } 
        return goal_dict

    @classmethod # uses when request body from postman
    def from_dict(cls, data):
        return cls(title=data["title"])

