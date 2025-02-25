from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app import db


class User(db.Model):
    __tablename__ = "user"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    cards = relationship("Card", back_populates="creator")
    comments = relationship("Comment", back_populates="user")

    def __repr__(self):
        return f'User with id {self.id} and name {self.name}'


class Card(db.Model):
    __tablename__ = "card"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    creator_id = Column(String, ForeignKey("user.id"), nullable=False)

    creator = relationship("User", back_populates="cards")
    comments = relationship("Comment", back_populates="card")
    webhooks = relationship("Webhook", back_populates="card")


class Comment(db.Model):
    __tablename__ = "comment"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    card_id = Column(String, ForeignKey("card.id"), nullable=False)
    content = Column(String, nullable=False)

    user = relationship("User", back_populates="comments")
    card = relationship("Card", back_populates="comments")


class Mirror(db.Model):
    __tablename__ = "mirror"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_card_id = Column(String, ForeignKey("card.id"), nullable=False)
    mirror_card_id = Column(String, ForeignKey("card.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("original_card_id <> mirror_card_id", name="original_not_mirror"),
    )


class Webhook(db.Model):
    __tablename__ = "webhook"

    id = Column(String, primary_key=True)
    card_id = Column(String, ForeignKey("card.id"), unique=True, nullable=False)

    card = relationship("Card", back_populates="webhooks")
