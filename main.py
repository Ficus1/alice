# импортируем библиотеки
import os

from flask import Flask, request
import logging
# библиотека, которая нам понадобится для работы с JSON
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
sessionStorage = {}
a = 0


@app.route('/post', methods=['POST'])
def main():
    global a
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response, a)
    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res, wheel):
    to_buy = ['слона', 'кролика']
    user_id = req['session']['user_id']
    global a

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = f'Привет! Купи {to_buy[wheel]}!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id, wheel)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо',
        'я покупаю',
        'я куплю'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = f'{to_buy[wheel].capitalize()} можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True if wheel == 1 else False
        a += 1
        if a == 1 and not res['response']['end_session']:
            res['response']['text'] = f'Привет! Купи {to_buy[a]}!'
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {to_buy[wheel]}!"
    res['response']['buttons'] = get_suggests(user_id, wheel)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id, wheel):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2 and wheel == 0:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })
    elif len(suggests) < 2 and wheel == 1:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=кролик",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)