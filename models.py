from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Определение полей таблицы Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # first_name = db.Column(db.String(255), nullable=False)
    # last_name = db.Column(db.String(255), nullable=False)
    # username = db.Column(db.String(255), unique=True, nullable=False)
    # password = db.Column(db.String(255), nullable=False)