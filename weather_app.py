from datetime import datetime

import flask
import requests
from flask import Flask, render_template, request, url_for, session, make_response
import json
from models import db

from config import password, db_name, user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@localhost/{db_name}'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
db.init_app(app)


def weather_results(city_name):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey=a2b400ac-c925-4aea-8cf0-206ceb9dcda3&geocode={city_name}&format=json"
    r = requests.get(url)
    response_json = json.loads(r.content)
    data = response_json['response']['GeoObjectCollection']['featureMember']
    result = list(
        filter(lambda x: x['GeoObject']['metaDataProperty']['GeocoderMetaData']['kind'] == 'locality' or "province",
               data))
    return result


def get_coordinates(result):
    coordinate = result[0]['GeoObject']['Point']['pos']
    coordinates = coordinate.split(' ')
    return coordinates


@app.route('/', methods=['GET', 'POST'])
def render_results():
    if request.method == 'POST':
        now_time = (datetime.utcnow().time()).strftime("%H")
        city_name = request.form['city_name']
        coordinate = weather_results(city_name)
        coordinates = get_coordinates(coordinate)

        def set_cookies():
            response = make_response()
            response.set_cookie('city_name', city_name)
            return response

        def get_cookies():
            name = request.cookies.get('city_name')

        set_cookies()
        print(get_cookies())

        # def func():
        #     context = {}
        #     context['text'] = 'Привет Мир!'
        #     name = 'nikolay'
        #
        #
        #     return response

        # Cookies.get()
        # bbb = request.cookies.get('user')
        # a = func()
        # print(a)

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

        return render_template('index.html', weather_data=data, city=city_name, coordinates=coordinates)

    if request.method == 'GET':
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
