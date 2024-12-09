from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='generate',
            description='начать создание нового теста'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())