"""
Состояния для управления навигацией и активностями
"""
from aiogram.fsm.state import State, StatesGroup

class MenuState(StatesGroup):
    """Состояния меню"""
    OUTSIDE_ISLAND = State()  # Вне острова (стартовое меню)
    ON_ISLAND = State()       # На острове (игровое меню)

class TutorialState(StatesGroup):
    """Состояния туториала"""
    STEP_1 = State()  # Профиль
    STEP_2 = State()  # Ферма
    STEP_3 = State()  # Команды
    COMPLETED = State()

class ActivityState(StatesGroup):
    """Состояния активностей"""
    EXPEDITION = State()    # В экспедиции
    BATTLE = State()       # В бою
    BUILDING = State()     # Строительство
    FARMING = State()      # Работа на ферме
    RACING = State()       # Скачки лошадей
