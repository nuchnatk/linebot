import os
import sys
from features.CarAnalytics import LicencePlate
import tempfile


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, AudioMessage,StickerMessage
)

import oil_price
app = Flask(__name__)

latest_image_path = ""

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
   print('Specify LINE_CHANNEL_SECRET as environment variable.')
   sys.exit(1)
if channel_access_token is None:
   print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
   sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

#boringcat
#line_bot_api = LineBotApi('C6yfsXHC7V9w4hirs8TLebWIBFVukTMf8akta0E1y86Js6PXYJ5OcIAQIfRF7K+/ANoCEWyiq8AflFKh12A6qNkrKfVrZjSGAIbCszIWX+Mj9BX1jBqF2kENu5y0H96zQckb79g0FEzSllODk/iacgdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('f4ef22d049166efb5c2a57664c10ef8e')

#อุ๋ง
#line_bot_api = LineBotApi('Qv4eY7y1IeLvw1psLwtJeA/zAPVoZbu0lr3nIl/2/BJXbDG4UvhwfF+4CI2myQHzsZCY9/deUYYM/WJxJwlSuc94Iu4zSkeZcdSYy+5uRUaDk7cjmYQUgVdhp3RpaG1s1rD+nEcJPvK0QfkQAGKLZQdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('a4768ecdec76bea8c60d26c27a1c1f40')

@app.route("/", methods=['GET'])
def default_action():
    return 'Hello'
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('Body:',body)
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # Handle webhook verification
    if event.reply_token == 'ffffffffffffffffffffffffffffffff':
       return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global latest_image_path

    # Handle webhook verification
    if event.reply_token == '00000000000000000000000000000000':
       return 'OK'


    if event.message.text == 'ราคาน้ำมัน' :
        l = oil_price.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n" %(p[0],p[1])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    elif event.message.text == 'วิเคราะห์รูป':
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='สักครู่ครับ')
            ])

        try:
            lp = LicencePlate()
            result = lp.process(latest_image_path)
            s= lp.translate(result)

            line_bot_api.push_message(
                event.source.user_id, [
                TextSendMessage(text=s)
            ])
        except Exception as e:
            print('Exception:',type(e),e)
            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text='ไม่สามารถวิเคราะห์รูปได้')
                ])
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+'ขอรับ'))
        




# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    global latest_image_path

    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    latest_image_path = dist_path
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='เก็บรูปให้แล้วค่ะ')
        ])

    # line_bot_api.reply_message(
    #     event.reply_token, [
    #         TextSendMessage(text='Save content.'),
    #         TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
    #     ])


if __name__ == "__main__":
    app.run()