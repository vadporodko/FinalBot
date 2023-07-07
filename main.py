from aiogram import Dispatcher, Bot, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputFile
from config import TG_API_TOKEN, SUPPORT_CHAT
from emails import emails_dict
from keyboard import start_keyboard, denied_keyboard, success_keyboard
from texts import (
    start_message,
    login_message,
    success_login,
    denied_login,
    describe_problem,
    waiting_message,
    support_message,
)

bot = Bot(TG_API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Email(StatesGroup):
    waiting = State()
    logged = State()


class Support(StatesGroup):
    describe = State()


@dp.message_handler(commands=["start"])
async def start(message: Message):
    img = InputFile("img/92.png")
    await bot.send_photo(
        chat_id=message.chat.id,
        caption=start_message,
        photo=img,
        reply_markup=start_keyboard,
    )


@dp.callback_query_handler(text="login")
async def login(callback: CallbackQuery, state: FSMContext):
    img = InputFile("img/93.png")
    await bot.answer_callback_query(callback_query_id=callback.id)
    await bot.send_photo(
        chat_id=callback.from_user.id, caption=login_message, photo=img
    )
    await state.set_state(Email.waiting)


@dp.message_handler(state=Email.waiting)
async def check(message: Message, state: FSMContext):
    img = InputFile("img/94.png")
    success_img = InputFile("img/96.png")
    denied_img = InputFile("img/97.png")
    await bot.send_photo(chat_id=message.chat.id, caption=waiting_message, photo=img)
    if message.text in emails_dict:
        await state.finish()
        await bot.send_photo(
            chat_id=message.chat.id,
            caption=success_login,
            photo=success_img,
            reply_markup=success_keyboard,
        )
    else:
        await state.finish()
        await bot.send_photo(
            chat_id=message.chat.id,
            caption=denied_login,
            photo=denied_img,
            reply_markup=denied_keyboard,
        )


@dp.callback_query_handler(text="support")
async def support(
    callback: CallbackQuery,
    state: FSMContext,
):
    await bot.send_message(text=describe_problem, chat_id=callback.from_user.id)
    await bot.answer_callback_query(callback_query_id=callback.id)
    await state.set_state(Support.describe)


@dp.message_handler(state=Support.describe)
async def save_support_message(
    message: Message,
    state: FSMContext,
):
    img = InputFile("img/95.png")
    await state.finish()
    await bot.send_message(chat_id=SUPPORT_CHAT, text=f'User:@{message.from_user.username} \n Message:{message.text}')
    await bot.send_photo(chat_id=message.chat.id, caption=support_message, photo=img)


if __name__ == "__main__":
    executor.start_polling(dp)
