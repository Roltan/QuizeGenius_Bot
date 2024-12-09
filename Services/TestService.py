import requests
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter

router = Router()

# Состояния для отслеживания этапов ввода
class GenerateTest(StatesGroup):
    over_count = State()
    topic = State()

# Функция для обработки команды /generate
@router.message(Command(commands=['generate']))
async def generate(message: types.Message, state: FSMContext):
    await message.answer('Пожалуйста, введите количество вопросов (overCount):')
    await state.set_state(GenerateTest.over_count)

# Функция для обработки ввода количества вопросов
@router.message(StateFilter(GenerateTest.over_count))
async def over_count(message: types.Message, state: FSMContext):
    try:
        overCount = int(message.text)
        await state.update_data(overCount=overCount)
        await message.answer('Теперь введите тему вопросов (topic):')
        await state.set_state(GenerateTest.topic)
    except ValueError:
        await message.answer('Пожалуйста, введите целое число для количества вопросов.')

# Функция для обработки ввода темы вопросов
@router.message(StateFilter(GenerateTest.topic))
async def topic(message: types.Message, state: FSMContext):
    topic = message.text
    await state.update_data(topic=topic)
    
    # Получаем данные из состояния
    user_data = await state.get_data()
    
    # Отправляем POST-запрос на сервер
    try:
        response = requests.post('https://quizgenius/api/test/generate', json={
            "overCount": user_data['overCount'],
            "topic": user_data['topic']
        }, verify=False)  # Отключаем верификацию SSL
        
        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()
            
            # Формируем сообщение с информацией о вопросах типа blank
            message_text = "Вопросы типа 'blank':\n\n"
            for question in data:
                if question['type'] == 'blank':
                    message_text += f"Вопрос {question['id']}:\n"
                    message_text += f"Задание: {question['quest']}\n"
                    message_text += f"Правильные ответы: {', '.join(question['correct'])}\n\n"
            
            await message.answer(message_text)
        else:
            await message.answer('Произошла ошибка при генерации тестов.')
    except requests.exceptions.RequestException as e:
        await message.answer(f'Произошла ошибка: {str(e)}')
    
    await state.clear()

# Функция для отмены диалога
@router.message(Command(commands=['cancel']), StateFilter(GenerateTest.__all_states__))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Генерация тестов отменена.')