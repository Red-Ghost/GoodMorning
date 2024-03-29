from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
import json
from zhdate import ZhDate

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
wai = os.environ['WEATHER_APIKEY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

# def get_weather():
#   url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
#   res = requests.get(url).json()
#   weather = res['data']['list'][0]
#   return weather['weather'], math.floor(weather['temp'])

if city is None or wai is None:
  print('没有城市行政区域编码或者apikey')
  city_id = None
else:
  city_idurl = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={wai}"
  city_data = json.loads(requests.get(city_idurl).content.decode('utf-8'))['location'][0]
  city_id = city_data.get("id")
  city_name = city_data.get('name')

# weather 直接返回对象，在使用的地方用字段进行调用。
def get_weather():
  if city_id is None:
    return None
  weatherurl = f"https://devapi.qweather.com/v7/weather/3d?location={city_id}&key={wai}&lang=zh"
  weather = json.loads(requests.get(weatherurl).content.decode('utf-8'))["daily"][0]
  return weather

def get_realtimeweather():
  if city_id is None:
    return None
  realtimeweatherurl = f"https://devapi.qweather.com/v7/weather/now?location={city_id}&key={wai}&lang=zh"
  realtimeweather = json.loads(requests.get(realtimeweatherurl).content.decode('utf-8'))["now"]["temp"]
  return realtimeweather

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  # next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")

  # 1、获取今日的农历日历
  now = str(datetime.now().strftime('%Y-%m-%d')).split("-")
  year, month, day = int(now[0]), int(now[1]), int(now[2])
  # 2、获取阴历生日，转为阳历
  birth_month = int(birthday.split("-")[0].strip())
  birth_day = int(birthday.split("-")[-1].strip())
  birth_ying = ZhDate(year, birth_month, birth_day)
  next = birth_ying.to_datetime()
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days
  

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  # return words.json()['data']['text']
  wstr = words.json()['data']['text']
  word_1 = wstr[0:17]
  word_2 = wstr[17:]
  return  word_1,word_2

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
# wea, temperature = get_weather()
weather = get_weather()
realtimeweather = get_realtimeweather()
word_1,word_2 = get_words()
data = {"weather":{"value":weather['textDay']},
        "temperature":{"value":realtimeweather},
        "love_days":{"value":get_count()},
        "birthday_left":{"value":get_birthday()},
        "words1":{"value":word_1, 
                  "color":get_random_color()},
        "words2":{"value":word_2, 
                  "color":get_random_color()}
       }
res = wm.send_template(user_id, template_id, data)
print(res)
