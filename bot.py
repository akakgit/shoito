import telebot
import requests
import urllib.parse
import urllib.request
import uuid
import os
import time

safer = lambda t: urllib.parse.quote_plus(t)

token = '7178870665:AAF-EV-APn8uAqroh4HKZu7bzYPyaGhJABM'
bot = telebot.TeleBot(token)

def gen_audio_video(text, message):
    songfilename = str(uuid.uuid4()) + ".mp3"
    songfilepath = "./tts/" + songfilename
    urllib.request.urlretrieve("https://degtev-api.vercel.app/t?i=" + safer(text), songfilepath)
    with open(r'{}'.format(songfilepath), 'rb') as audio:
        bot.send_audio(message.chat.id, audio)

        videofilename = str(uuid.uuid4()) + ".mp4"
        videofilepath = './tts/' + videofilename
        try:
            data = {'audio': audio}
            url = 'https://us-central1-aivision-app.cloudfunctions.net/talkingheadsapi/api/v0/'
            response = requests.post(url + 'speeches', files=data)
            if response.status_code == 200:
                audio_id = response.json()['id']
                try:
                    payload = {
                        "avatar": "default_persons/default_tokkingheads/artbreeder7_v2.jpeg",
                        "inverse_align_video": "true",
                        "speech": audio_id,
                    }
                    response = requests.post(url + 'tokkingheads', json=payload)
                    if response.status_code == 200:
                        video_id = response.json()['id']
                        url = url + 'tokkingheads/' + video_id
                        videourl = ''
                        attempts = 500
                        while not videourl and attempts > 0:
                            attempts -= 1
                            video = requests.get(url)
                            data = video.json()
                            if data.get('status') == 'complete':
                                videourl = data.get('download_url')[0]
                            else:
                                time.sleep(0.5)
                        if videourl:
                            urllib.request.urlretrieve(videourl, videofilepath)
                            with open(videofilepath, 'rb') as video:
                                bot.send_video_note(message.chat.id, video)
                except: pass
        except: pass
        finally:
            try:
                os.remove(songfilepath)
                os.remove(videofilepath)
            except: pass

@bot.message_handler(commands=['start'])
def hello(message):
    bot.reply_to(message, "Привет!")

@bot.message_handler(content_types=['text'])
def text(message):
    q = message.text.strip()
    if q:
        bot.reply_to(message, 'Дайте подумать...')
        try:
            answer = requests.get('https://degtev-api.vercel.app/s?i=' + safer(q))
            if answer.status_code == 200:
                answer = answer.json().get('result', 'Не могу знать')
                bot.reply_to(message, answer)
                try:
                    gen_audio_video(answer, message)
                except: pass
            else:
                bot.reply_to(message, 'Не знаю что ответить')
        except:
            bot.reply_to(message, 'Мозгов нема у меня :(')
bot.infinity_polling()

