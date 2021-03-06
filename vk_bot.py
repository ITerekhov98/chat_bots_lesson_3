import logging
import random
import time

from environs import Env
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from dialog_flow_lib import fetch_intent_response
from log_hadler import LogsHandler


logger = logging.getLogger('vk_bot')


def reply_using_dialog_flow(event, vk_api):
    user_id = event.user_id,
    message = event.text,

    response = fetch_intent_response(user_id, *message)

    if not response.query_result.intent.is_fallback:
        vk_api.messages.send(
            user_id=user_id,
            message=response.query_result.fulfillment_text,
            random_id=random.randint(1, 1000)
        )


def main():
    env = Env()
    env.read_env()
    logger.setLevel(logging.WARNING)
    logger.addHandler(LogsHandler(
        env.str('TG_BOT_TOKEN'),
        env.str('SERVICE_TG_CHAT_ID'),
        'VK_bot',
        )
    )
    vk_session = vk.VkApi(token=env.str('VK_API_TOKEN'))
    vk_api = vk_session.get_api()
    while True:
        try:
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    reply_using_dialog_flow(event, vk_api)
        except Exception as err:
            logger.exception(err)
            time.sleep(120)


if __name__ == '__main__':
    main()
