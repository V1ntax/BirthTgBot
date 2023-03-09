import asyncio
import csv
import datetime
import glob
import random
import telegram
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

telegram_token = config['telegram']['token']
telegram_channel_id = config['telegram']['channel_id']

images_path = config['images']['path']
birthdays_table = config['Table']['Csv_table']
birthdays_messages = config['Messages']['birthdays_message']

birthday_dict = {}
with open(birthdays_table, 'r',  encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        name = row[0]
        date = row[1]
        birthday_dict[name] = date


def check_birthday():
    today = datetime.datetime.now().strftime('%m-%d')
    for name, date in birthday_dict.items():
        if today == date:
            return name
    return None


greetings = []
with open(birthdays_messages, 'r', encoding='utf-8') as file:
    for line in file:
        greetings.append(line.strip())


def generate_message(name, idx):
    greeting = greetings[idx % len(greetings)].replace('{name}', name)
    image_path = random.choice(glob.glob(images_path))

    return greeting, open(image_path, 'rb'), idx+1


bot = telegram.Bot(telegram_token)
channel_id = telegram_channel_id


async def send_birthday_messages():
    wasChecked = False
    index = 0

    while True:
        now = datetime.datetime.now()
        if (now.hour > 8 or (now.hour == 8 and now.minute >= 30)) and wasChecked == False:
            name = check_birthday()
            if name is not None:
                message, image, index = generate_message(name, index)
                await bot.send_photo(chat_id=channel_id, photo=image, caption=message)
            wasChecked = True
        else:
            wait_time = datetime.datetime(now.year, now.month, now.day, 8, 30) - now
            await asyncio.sleep(wait_time.seconds)
            wasChecked = False


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_birthday_messages())
