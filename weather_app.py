from datetime import datetime
from uuid import uuid4
import requests
from flask import Flask, render_template, request, make_response, jsonify
import json
from models import db, Users
from config import password, db_name, user

# Подключение к базе данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@localhost/{db_name}'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
db.init_app(app)

# Получение координат города с помощь API
def weather_results(city_name):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey=a2b400ac-c925-4aea-8cf0-206ceb9dcda3&geocode={city_name}&format=json"
    r = requests.get(url)
    response_json = json.loads(r.content)
    data = response_json['response']['GeoObjectCollection']['featureMember']
    result = list(
        filter(lambda x: x['GeoObject']['metaDataProperty']['GeocoderMetaData']['kind'] == 'locality' or "province",
               data))
    return result

# Разбиение координат на длину и широту
def get_coordinates(result):
    coordinate = result[0]['GeoObject']['Point']['pos']
    coordinates = coordinate.split(' ')
    return coordinates

# Объявление главной страницы
@app.route('/', methods=['GET', 'POST'])
def render_results():
    if request.method == 'POST':
        now_time = (datetime.utcnow().time()).strftime("%H")
        city_name = request.form['city_name']
        coordinate = weather_results(city_name)
        coordinates = get_coordinates(coordinate)

        r = requests.get(
            f'https://api.open-meteo.com/v1/forecast?latitude={coordinates[1]}&longitude={coordinates[0]}&hourly=temperature_2m,apparent_temperature,precipitation_probability,surface_pressure,wind_speed_10m&wind_speed_unit=ms&forecast_days=3')
        response_json = json.loads(r.content)
        data = [{
            'date': 'Текущий час',
            'temperature': response_json['hourly']['temperature_2m'][int(now_time)],
            'apparent_temperature': response_json['hourly']['apparent_temperature'][int(now_time)],
            'wind_speed': response_json['hourly']['wind_speed_10m'][int(now_time)],
            'precipitation_probability': response_json['hourly']['precipitation_probability'][int(now_time)],
            'surface_pressure': round(((response_json['hourly']['surface_pressure'][int(now_time)]) * 0.75))
        },
            {
                'date': 'Следующий час',
                'temperature': response_json['hourly']['temperature_2m'][int(now_time) + 1],
                'apparent_temperature': response_json['hourly']['apparent_temperature'][int(now_time) + 1],
                'wind_speed': response_json['hourly']['wind_speed_10m'][int(now_time) + 1],
                'precipitation_probability': response_json['hourly']['precipitation_probability'][int(now_time) + 1],
                'surface_pressure': round(((response_json['hourly']['surface_pressure'][int(now_time) + 1]) * 0.75))
            },
            {
                'date': 'Через два часа',
                'temperature': response_json['hourly']['temperature_2m'][int(now_time) + 2],
                'apparent_temperature': response_json['hourly']['apparent_temperature'][int(now_time) + 2],
                'wind_speed': response_json['hourly']['wind_speed_10m'][int(now_time) + 2],
                'precipitation_probability': response_json['hourly']['precipitation_probability'][int(now_time) + 2],
                'surface_pressure': round(((response_json['hourly']['surface_pressure'][int(now_time) + 2]) * 0.75))
            }
        ]

        user_id = request.cookies.get('user_id') if request.cookies.get('user_id') else str(uuid4())
        new_item = Users(user_id=user_id, city_name=city_name)
        db.session.add(new_item)
        db.session.commit()
        users_list = Users.query.distinct(Users.city_name).filter_by(user_id=user_id).all()
        resp = make_response(render_template('index.html', weather_data=data, city=city_name, coordinates=coordinates,
                                             users_list=users_list, user_id=user_id))
        resp.set_cookie('user_id', user_id)
        return resp

    if request.method == 'GET':
        user_id = request.cookies.get('user_id') if request.cookies.get('user_id') else str(uuid4())
        users_list = Users.query.distinct(Users.city_name).filter_by(user_id=user_id).all()
        return render_template('index.html', users_list=users_list, user_id=user_id)

# Объявление API для просмотра статитики запрашиваемых городов
@app.route('/amount', methods=['GET'])
def create_amount_list():
    city_list = []
    row_list = Users.query.distinct(Users.city_name).all()

    for row in row_list:
        city_list.append(row.city_name)
        amount_list = {}
        for i in range(len(city_list)):
            amount_list[city_list[i]] = Users.query.filter_by(city_name=city_list[i]).count()
    return jsonify(amount_list)

# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
