from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from bot.core.filters.keyboard import (
    build_columns_from_dict, build_columns_from_dict_numbers, build_columns_from_dict_letters
)


class UserFactory(CallbackData, prefix='u'):
    action: str
    value: str = 'none'

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='НМТ тести 📚', callback_data=UserFactory(action='select_subject_nmt'))
        builder.button(text='Допомога із завданням 📝', callback_data=UserFactory(action='get_response_gpt'))
        builder.button(text='Профіль 👤', callback_data=UserFactory(action='profile'))
        builder.button(text='Таблиця лідерів 🏆', callback_data=UserFactory(action='leaderboard'))
        builder.button(text='Платежі 💸', callback_data=UserFactory(action='payments'))
        builder.button(text='Звернення ✉️', callback_data=UserFactory(action='support'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def response_language(data, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder, rows = build_columns_from_dict(builder, data, "get_response_gpt", UserFactory, selected, 3)
        builder.button(text='Відхилити 🔻', callback_data=UserFactory(action='cancel_gpt'))

        builder.adjust(*[3] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def select_payment() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='1 тиждень', callback_data=UserFactory(action='select_payment', value='0'))
        builder.button(text='1 місяць', callback_data=UserFactory(action='select_payment', value='1'))
        builder.button(text='3 місяці', callback_data=UserFactory(action='select_payment', value='2'))
        builder.button(text='Назад', callback_data=UserFactory(action='payments'))

        builder.adjust(3, 1)
        return builder.as_markup()

    @staticmethod
    def payments_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Подовжити підписку 💸', callback_data=UserFactory(action='select_payment'))
        builder.button(text='Ввести промокод 🔖', callback_data=UserFactory(action='enter_promocode'))
        builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def select_subject_nmt() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Українська мова 🇺🇦', callback_data=UserFactory(action='select_subject_nmt', value='0'))
        builder.button(text='Математика 📐', callback_data=UserFactory(action='select_subject_nmt', value='1'))
        builder.button(text='Історія України 🏛', callback_data=UserFactory(action='select_subject_nmt', value='2'))
        builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def select_test_nmt(list_len, index, is_done) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        text1 = "⬅️"
        text11 = "⏪"
        callback_data1 = UserFactory(action='select_test_nmt', value='go_back')
        callback_data11 = UserFactory(action='select_test_nmt', value='go_back_five')
        text2 = "➡️"
        text22 = "⏩"
        callback_data2 = UserFactory(action='select_test_nmt', value='go_forward')
        callback_data22 = UserFactory(action='select_test_nmt', value='go_forward_five')

        if index == 0:
            text1 = "  "
            text11 = "  "
            callback_data1 = UserFactory(action='ignore')
            callback_data11 = UserFactory(action='ignore')
        if index == list_len - 1:
            text2 = "  "
            text22 = "  "
            callback_data2 = UserFactory(action='ignore')
            callback_data22 = UserFactory(action='ignore')

        if is_done:
            builder.button(
                text='Скласти знову 🌀', callback_data=UserFactory(action='select_test_nmt', value='select_again')
            )
        else:
            builder.button(text='Скласти 🧩', callback_data=UserFactory(action='select_test_nmt', value='select'))

        builder.button(text=text11, callback_data=callback_data11)
        builder.button(text=text1, callback_data=callback_data1)
        builder.button(text=f"{index + 1}/{list_len}", callback_data=UserFactory(action='ignore'))
        builder.button(text=text2, callback_data=callback_data2)
        builder.button(text=text22, callback_data=callback_data22)
        builder.button(text='Назад', callback_data=UserFactory(action='select_test_nmt', value='back'))

        builder.adjust(1, 5, 1)
        return builder.as_markup()

    @staticmethod
    def exercise_options(data, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder, rows = build_columns_from_dict(builder, data, "exercise_options", UserFactory, selected, columns=2)
        if len(selected) == 1:
            builder.button(text='Перевірити ✔️', callback_data=UserFactory(action='check_option'))
        else:
            builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(*[2] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def exercise_options_3(numbers, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder = build_columns_from_dict_numbers(builder, "exercise_options_3", UserFactory, numbers, selected)
        if len(selected) == 3:
            builder.button(text='Перевірити ✔️', callback_data=UserFactory(action='check_option'))
        else:
            builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(*[len(numbers)] * 2, 1)
        return builder.as_markup()

    @staticmethod
    def exercise_options_c(letters, numbers, selected, is_done) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder = build_columns_from_dict_letters(
            builder, "exercise_options_c", UserFactory, letters, numbers, selected
        )
        if is_done:
            builder.button(text='Перевірити ✔️', callback_data=UserFactory(action='check_option'))
        else:
            builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(*[len(letters) + 1] * (len(numbers) + 1), 2)
        return builder.as_markup()

    @staticmethod
    def cancel_answer() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def take_test_again_confirm() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=UserFactory(action='take_test_again', value='0'))
        builder.button(text='🟢 Так', callback_data=UserFactory(action='take_test_again', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def correct_answer(exercise_educational_material, exercise_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        if exercise_educational_material:
            builder.button(
                text='Пояснення 📖',
                callback_data=UserFactory(action='educational_material', value=f"{exercise_id}")
            )
        builder.button(text='➡️', callback_data=UserFactory(action='proceed_nmt_next'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def educational_material() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='➡️', callback_data=UserFactory(action='proceed_nmt_next'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def support() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def profile() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Змінити нікнейм 🖊', callback_data=UserFactory(action='change_nickname'))
        builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def enter_nickname() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=UserFactory(action='cancel_enter_nickname'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def enter_promocode() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def leaderboard() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🚪', callback_data=UserFactory(action='main_menu'))

        builder.adjust(1)
        return builder.as_markup()
