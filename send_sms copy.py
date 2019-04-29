from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
import requests
import os
from datetime import datetime, timedelta


def get_weather_dict(api_key, city_id='6176823'):
    '''
    Requests weather from OpenWeatherMap using the API key, api_key, and
    city ID, city_id. Assumes object is valid JSON and returns a Python
    dictionary of the JSON.

    Inputs: Valid API key
    '''

    parameters = {'id': city_id, 'appid': api_key, 'units': 'metric'}

    resp = requests.get(
        'https://api.openweathermap.org/data/2.5/weather', 	parameters)
    resp_json = resp.json()
    return resp_json


def get_weather_info(weather_data):

    temp = weather_data['main']['temp']
    city = weather_data['name']
    description = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']

    return temp, city, description, wind_speed


def get_nhl_dict():
    '''
    Requests NHL info from NHL Stats API. No API key required.
    '''
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    link = 'https://statsapi.web.nhl.com/api/v1/schedule/?date=' + yesterday
    resp = requests.get(link)
    resp_json = resp.json()
    return resp_json


def get_nhl_message(nhl_data):

    num_games = nhl_data['totalItems']
    message = ''

    for i in range(0, num_games):

        away_team = nhl_data['dates'][0]['games'][i]['teams']['away']['team']['name']
        home_team = nhl_data['dates'][0]['games'][i]['teams']['home']['team']['name']
        away_score = nhl_data['dates'][0]['games'][i]['teams']['away']['score']
        home_score = nhl_data['dates'][0]['games'][i]['teams']['home']['score']
        home_wins = nhl_data['dates'][0]['games'][i]['teams']['home']['leagueRecord']['wins']
        home_loss = nhl_data['dates'][0]['games'][i]['teams']['home']['leagueRecord']['losses']

        if home_score > away_score:
            message += "{} beat {} {}-{}. ".format(
                home_team, away_team, 		home_score, away_score)
        else:
            message += "{} beat {} {}-{}. ".format(
                away_team, home_team, 		away_score, home_score)

        series = 'lead'

        if home_wins == 4 or home_loss == 4:
            series = 'win'

        if home_wins > home_loss:
            message += "{} {} the series {}-{}. ".format(
                home_team, series, 	home_wins, home_loss)
        elif home_wins != home_loss:
            message += "{} {} the series {}-{}. ".format(
                away_team, series, 	home_loss, home_wins)
        else:
            message += "The series is tied {0}-{0}. ".format(home_wins)

        message += "\n"

    return message


def send_to_sms(receive_number, message, send_number, account_sid, auth_token):

    proxy_client = TwilioHttpClient()
    proxy_client.session.proxies = {"http": "http://10.10.1.10:3128",
                                    "https": "http://10.10.1.10:1080"}
    client = Client(account_sid, auth_token, http_client=proxy_client)
    client.messages.create(body=message, from_=send_number, to=receive_number)


if __name__ == '__main__':
    account_sid = '' // Twilio account ID
    auth_token = '' // Twilio authentication token
    my_api = '' // Api key from OpenWeather
    my_city = '6176823'
    my_msg = ''

    # Weather portion of message
    weather_data = get_weather_dict(my_api, my_city)
    my_name = 'Lucas'
    temp, city, description, wind_speed = get_weather_info(weather_data)
    my_msg += "Good Morning {}!\nThe weather in {} is {}. The current temperature" \
        " is {} with a wind speed of {}.\n".format(
            my_name, city, description, temp, wind_speed)

    # NHL portion of message, get_nhl_message function returns a string with
    # message and skips weather steps due to complexity of data
    nhl_data = get_nhl_dict()
    my_msg += get_nhl_message(nhl_data)

    recipient = '+19053175331'
    sender = '+12262418717'
    print(my_msg)
    send_to_sms(recipient, my_msg, sender, account_sid, auth_token)
