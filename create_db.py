from flask import Flask

from config import user, password, db_name
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@localhost/{db_name}'
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()