from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, ForeignKeyConstraint
from typing import List
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id: Mapped[str] = mapped_column(String, primary_key=True)
    boards: Mapped[List['Board']] = relationship()

class Board(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id'), primary_key=True)
    tasks: Mapped[List['Task']] = relationship(cascade="all, delete-orphan")

    def as_json(self, without_tasks=False):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'tasks': [task.as_json() for task in self.tasks]
        } if not without_tasks else {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
        }

class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[int] = mapped_column(Integer)
    board_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    board_user_id: Mapped[str] = mapped_column(String, primary_key=True)
    __table_args__ = (ForeignKeyConstraint([board_id, board_user_id],
                                           [Board.id, Board.user_id]),
                      {})
    def as_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'board_id': self.board_id,
            'board_user_id': self.board_user_id
        }

# class UserSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = User
#
# class BoardSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Board
#
# class TaskSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Task
#
# print(UserSchema)