#!/usr/bin/env python3

import telebot
from telebot import types
from keyboa import Keyboa

import logging
import json

import db
import users


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("main")
log.setLevel(logging.DEBUG)


cfg = db.Config()
usrs = users.Users()
bot = telebot.TeleBot(cfg.token())


def drawTxtDlg(message):
    log.info("drawText")
    if u := usrs.get(message):
        log.info(f"u = {u}")
        for d in u.dlgFilter():
            log.info(f"d = {d}")
            bot.send_message(u.id, d.text)
    else:
        log.info("can't get user")


def drawReplyDlg(message):
    log.info("drawReplyDlg")
    u = usrs.get(message)
    log.info(f"u = {u}")
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for d in u.dlgFilter():
        log.info(f"d = {d}")
        kb.add(telebot.types.KeyboardButton(text=d.text))
    bot.send_message(
        u.id,
        "Выбeрите:",
        reply_markup=kb,
    )
    bot.register_next_step_handler(message, remove_keyboard)


@bot.message_handler(commands=["rm_kb"])
def remove_keyboard(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "keyboard deleted", reply_markup=keyboard)
    bot.clear_step_handler(message)


def drawInlineDlgManual(message):
    log.info("drawInlineDlgManual")
    u = usrs.add(message)
    log.info(f"u = {u}")
    kb = telebot.types.InlineKeyboardMarkup()
    for d in u.dlgFilter():
        log.info(f"d = {d}({d.id})")
        kb.add(
            telebot.types.InlineKeyboardButton(
                text=d.text,
                callback_data=d.id,
            )
        )
    bot.send_message(u.id, "Выбeрите:", reply_markup=kb)


def drawInlineDlg(message):
    log.info("drawInlineDlg")
    u = usrs.get(message)
    dlgs = u.dlgFilter()
    menu = [{"text": d.text, "callback_data": d.id} for d in dlgs]
    if menu:
        log.info(f"buttons for menu: {menu}")
        kbcallback = Keyboa(items=menu)
        kb = kbcallback.keyboard
        bot.send_message(u.id, "Выбeрите:", reply_markup=kb)
    else:
        log.info("message.json = " + json.dumps(message.json))
        admins = [int(_.tgid) for _ in cfg.admins()]
        log.info(f"admins = {admins}")
        log.info("message.json = " + json.dumps(message.json))
        if message.chat.id not in admins:
            log.info("handle_text (USER)")
            for admin in admins:
                log.info(
                    f"handle_text (USER): forwarding message to admin {admin}")
                bot.send_message(admin, u._dlgs)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    log.info("callback_handler")
    log.info(f"callback data: {call.json}")
    u = usrs.get(call.message)
    u.fwd(call.data)
    bot.delete_message(chat_id=u.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id, text="Данные сохранены")
    bot.send_message(
        u.id, f"Выбрано {u.dlgFilter(parent=call.data)}(id={call.data})")
    drawInlineDlg(call.message)


@bot.message_handler(commands=["start", "начало"])
def start(message):
    log.info("/start")
    u = usrs.add(message)
    u.reset()
    bot.send_message(u.id, cfg.greeting())
    log.info(str(u.dlgFilter()))
    # drawReplyDlg(message)
    drawInlineDlg(message)
    #
    # bot.register_next_step_handler(message, save_username)


@bot.message_handler(commands=["back", "назад"])
def back(message):
    log.info("/back")
    if u := usrs.get(message):
        # получить первое сообщение из диалогов
        # остановить parent на парент из этого сообщения
        u.bwd()
    drawReplyDlg(message)


@bot.message_handler(
    func=lambda message: True,
    content_types=[
        "audio",
        "photo",
        "text",
        "voice",
        "video",
        "document",
        "location",
        "contact",
        "sticker",
    ],
)
def handle_text(message):
    log.info("handle_text")

    u = usrs.add(message)

    log.info("message.json = " + json.dumps(message.json))

    admins = [int(_.tgid) for _ in cfg.admins()]
    log.info(f"admins = {admins}")

    log.info("handle_text")
    log.info("message.json = " + json.dumps(message.json))
    if message.chat.id not in admins:
        log.info("handle_text (USER)")
        for admin in admins:
            log.info(
                f"handle_text (USER): forwarding message to admin {admin}")
            bot.forward_message(admin, message.chat.id, message.message_id)
    else:
        # log.info(f"handle_text (ADMIN): message = {message}")
        # log.info(f"handle_text (ADMIN): message = {message}")
        reply_message = message.reply_to_message or {}
        if reply_message:
            reply_message = reply_message.forward_origin or {}
            if reply_message.sender_user.id != message.chat.id:
                reply_id = reply_message.sender_user.id
                log.info(f"handle_text answer from admin to {reply_id}")
                bot.send_message(
                    reply_id,
                    f"{message.text}",
                )
        else:
            bot.send_message(
                message.chat.id,
                "Ответьте на сообщение пользователя.",
            )
    log.info("end of handle_text")


def main():
    # bot.polling(none_stop=True)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
