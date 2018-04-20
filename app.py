from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('C6yfsXHC7V9w4hirs8TLebWIBFVukTMf8akta0E1y86Js6PXYJ5OcIAQIfRF7K+/ANoCEWyiq8AflFKh12A6qNkrKfVrZjSGAIbCszIWX+Mj9BX1jBqF2kENu5y0H96zQckb79g0FEzSllODk/iacgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f4ef22d049166efb5c2a57664c10ef8e')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()