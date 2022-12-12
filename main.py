import time

import imageio
import os, sys
from telebot import TeleBot
from requests import get


def convertFile(inputpath):
    outputpath = os.path.splitext(inputpath)[0] + '.gif'
    print(f"[INFO] converting\r\n\t{inputpath}\r\nto\r\n\t{outputpath}")

    reader = imageio.get_reader(inputpath)
    fps = reader.get_meta_data()['fps']

    writer = imageio.get_writer(outputpath, fps=fps)

    for i, im in enumerate(reader):
        sys.stdout.write(f"[INFO] \rframe {i}/{len(list(enumerate(reader)))}")
        sys.stdout.flush()
        writer.append_data(im)

    print("[INFO] \r\nFinalizing...")
    writer.close()
    print("[INFO] Done.\n")

    return outputpath


def telegram_bot(token):
    bot = TeleBot(token)

    @bot.message_handler(['start'])
    def start(message):
        bot.send_message(message.chat.id, f"Привет, <b>{message.from_user.first_name}</b>!\n"
                                          f"Отправь мне видео в формате <i>.mp4</i> и я "
                                          f"сделаю из него файл формата <i>.gif</i>\n"
                                          f"Но придётся немного подождать, пока я конвертирую файл. "
                                          f"Как только всё будет готово - я дам тебе знать", parse_mode='html')

    @bot.message_handler(content_types=['video'])
    def convert(message):
        file_info = bot.get_file(message.video.file_id)
        file = get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}').content
        file_path = f'{str(file_info.file_path).replace("videos/", "")}'

        with open(file_path, 'wb') as video:
            video.write(file)

        try:
            output_file = convertFile(f'{file_path}')

            with open(output_file, 'rb') as file:
                bot.send_document(message.chat.id, file)
                print('[INFO] .gif file was successfully sanded!')

            time.sleep(3)
            os.remove(file_path)
            print(f'[INFO] {file_path} was successfully deleted!')
            time.sleep(3)
            os.remove(output_file)
            print(f'[INFO] {output_file} was successfully deleted!')

        except Exception as ex:
            print(ex)
            bot.send_message(message.chat.id, "Что-то пошло не так. "
                                              "Возможно файл слишком большой и я не могу его обработать."
                                              "Попробуй выбрать файл который весит не так много.")

    bot.polling()


telegram_bot('5377279394:AAEo7i23FpDgPeI9FizGOhMUo24e0m_MMBU')
