import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from maxapi import Bot, Dispatcher
from maxapi.types import MessageCreated, CommandStart, MessageButton, ButtonsPayload

load_dotenv()

TOKEN = os.getenv("MAX_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не найден MAX_BOT_TOKEN. Создайте .env и добавьте токен.")

BASE_DIR = Path(__file__).resolve().parent
PRICES_FILE = BASE_DIR / "data" / "prices.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()


def load_prices():
    with open(PRICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main_menu():
    buttons = [
        [
            MessageButton(text="🧮 Рассчитать стоимость"),
            MessageButton(text="🏠 Наши услуги"),
        ],
        [
            MessageButton(text="📅 Записаться на замер"),
            MessageButton(text="📄 Оформить договор"),
        ],
        [
            MessageButton(text="📋 Мои заявки"),
            MessageButton(text="📞 Связаться с менеджером"),
        ],
    ]
    return ButtonsPayload(buttons=buttons).pack()


@dp.bot_started()
async def bot_started(event):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "🏗️ <b>СтройПроект</b>\n\n"
            "Помогу рассчитать стоимость работ, записаться на замер "
            "и подготовить данные для договора.\n\n"
            "Выберите действие ниже 👇"
        ),
        format="html",
        attachments=[main_menu()],
    )


@dp.message_created(CommandStart())
async def start(event: MessageCreated):
    await event.message.answer(
        text=(
            "🏗️ <b>СтройПроект</b>\n\n"
            "Добро пожаловать! Что хотите сделать?"
        ),
        format="html",
        attachments=[main_menu()],
    )


@dp.message_created()
async def messages(event: MessageCreated):
    text = (event.message.body.text or "").strip()

    if text == "🏠 Наши услуги":
        prices = load_prices()
        service_lines = []
        for key, item in prices.items():
            service_lines.append(f"• {item['name']} — от {item['price']} ₽/{item['unit']}")
        await event.message.answer(
            text="🏠 <b>Наши услуги</b>\n\n" + "\n".join(service_lines),
            format="html",
            attachments=[main_menu()],
        )

    elif text == "🧮 Рассчитать стоимость":
        await event.message.answer(
            text=(
                "🧮 <b>Быстрый расчёт</b>\n\n"
                "Напишите одним сообщением:\n"
                "<code>площадь 50</code>\n\n"
                "Пока тестируем базовый расчёт. Следующим этапом "
                "сделаем пошаговый калькулятор по каждому виду работ."
            ),
            format="html",
            attachments=[main_menu()],
        )

    elif text.startswith("площадь "):
        try:
            area = float(text.replace("площадь ", "").replace(",", "."))
            price = load_prices()["plaster"]["price"]
            total = area * price
            await event.message.answer(
                text=(
                    f"📐 Площадь: <b>{area:g} м²</b>\n"
                    f"💰 Ориентировочная стоимость: <b>{total:,.0f} ₽</b>\n\n"
                    "⚠️ Это предварительный расчёт. Точную стоимость "
                    "определим после замера."
                ).replace(",", " "),
                format="html",
                attachments=[main_menu()],
            )
        except ValueError:
            await event.message.answer("Не понял площадь. Пример: <code>площадь 50</code>", format="html")

    elif text == "📅 Записаться на замер":
        await event.message.answer(
            text=(
                "📅 <b>Запись на замер</b>\n\n"
                "Напишите:\n"
                "1. Ваше имя\n"
                "2. Телефон\n"
                "3. Адрес\n"
                "4. Желаемую дату\n\n"
                "В следующей версии сделаем нормальную пошаговую форму "
                "с выбором даты и времени."
            ),
            format="html",
            attachments=[main_menu()],
        )

    elif text == "📄 Оформить договор":
        await event.message.answer(
            text=(
                "📄 <b>Договор</b>\n\n"
                "Здесь будет автоматическое формирование договора "
                "из данных заявки: заказчик, объект, работы, стоимость, "
                "сроки и реквизиты исполнителя.\n\n"
                "Пока это демонстрационный экран."
            ),
            format="html",
            attachments=[main_menu()],
        )

    elif text == "📋 Мои заявки":
        await event.message.answer(
            text="📋 Пока заявок нет. После подключения базы здесь появятся ваши заявки.",
            attachments=[main_menu()],
        )

    elif text == "📞 Связаться с менеджером":
        await event.message.answer(
            text="📞 Напишите сообщение — менеджер свяжется с вами.",
            attachments=[main_menu()],
        )

    else:
        await event.message.answer(
            text="Выберите действие в меню 👇",
            attachments=[main_menu()],
        )


async def main():
    # Long Polling удобен для первого теста. Для production позже перейдём на Webhook.
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
