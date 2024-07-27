from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Определение полей таблицы Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    city_name = db.Column(db.String(255), nullable=False)
