# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:20:18 2021

@author: travis
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class User(db.Model):
    """DB Class."""
    pid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(20), nullable=False, default="default.jpg")
    pw = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        """Print user representation string."""
        return f"User('{self.uname}', '{self.email}', '{self.image}')"
    
class Post(db.Model):
    pid = db.Column(db.Integer, primary_key=True)

def test():
    """Figuring this out."""
    