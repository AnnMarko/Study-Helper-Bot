from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from bot.core.filters.keyboard import (
    build_columns_from_dict, build_columns_from_dict_letters, build_columns_from_dict_numbers
)


class AdminFactory(CallbackData, prefix='a'):
    action: str
    value: str = 'none'

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(
            text='Додати тест ➕',
            callback_data=AdminFactory(action='select_subject_add_test')
        )
        builder.button(
            text='Редагувати тести ✏️',
            callback_data=AdminFactory(action='select_subject_edit_test')
        )
        builder.button(
            text='Повідомлення для учасників 📢',
            callback_data=AdminFactory(action='send_message_to_all')
        )
        builder.button(
            text='Згенерувати промокод 🔖',
            callback_data=AdminFactory(action='generate_promocode')
        )

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def select_subject_add_test() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(
            text='Українська мова 🇺🇦', callback_data=AdminFactory(action='select_subject_add_test', value='0')
        )
        builder.button(
            text='Математика 📐', callback_data=AdminFactory(action='select_subject_add_test', value='1')
        )
        builder.button(
            text='Історія України 🏛', callback_data=AdminFactory(action='select_subject_add_test', value='2')
        )
        builder.button(text='🚪', callback_data=AdminFactory(action='cancel'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def select_subject_edit_test() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(
            text='Українська мова 🇺🇦', callback_data=AdminFactory(action='select_subject_edit_test', value='0')
        )
        builder.button(
            text='Математика 📐', callback_data=AdminFactory(action='select_subject_edit_test', value='1')
        )
        builder.button(
            text='Історія України 🏛', callback_data=AdminFactory(action='select_subject_edit_test', value='2')
        )
        builder.button(text='🚪', callback_data=AdminFactory(action='cancel'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def enter_test_title() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Без назви 🙅', callback_data=AdminFactory(action='no_title'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def confirm_add_test() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='add_test', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='add_test', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def select_test_to_edit(list_len, index) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        text1 = "⬅️"
        text11 = "⏪"
        callback_data1 = AdminFactory(action='select_test_to_edit', value='go_back')
        callback_data11 = AdminFactory(action='select_test_to_edit', value='go_back_five')
        text2 = "➡️"
        text22 = "⏩"
        callback_data2 = AdminFactory(action='select_test_to_edit', value='go_forward')
        callback_data22 = AdminFactory(action='select_test_to_edit', value='go_forward_five')

        if index == 0:
            text1 = "  "
            text11 = "  "
            callback_data1 = AdminFactory(action='ignore')
            callback_data11 = AdminFactory(action='ignore')
        if index == list_len - 1:
            text2 = "  "
            text22 = "  "
            callback_data2 = AdminFactory(action='ignore')
            callback_data22 = AdminFactory(action='ignore')

        builder.button(text='Обрати', callback_data=AdminFactory(action='select_test_to_edit', value='select'))
        builder.button(text=text11, callback_data=callback_data11)
        builder.button(text=text1, callback_data=callback_data1)
        builder.button(text=f"{index + 1}/{list_len}", callback_data=AdminFactory(action='ignore'))
        builder.button(text=text2, callback_data=callback_data2)
        builder.button(text=text22, callback_data=callback_data22)
        builder.button(text='Назад', callback_data=AdminFactory(action='select_test_to_edit', value='back'))

        builder.adjust(1, 5, 1)
        return builder.as_markup()

    @staticmethod
    def select_edit() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Редагувати тест 📖', callback_data=AdminFactory(action='edit_test'))
        builder.button(text='Редагувати завдання тесту 🔖', callback_data=AdminFactory(action='edit_exercises'))
        builder.button(text='🚪', callback_data=AdminFactory(action='cancel'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def edit_test(is_available: bool) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Змінити назву ✏️', callback_data=AdminFactory(action='edit_title'))
        builder.button(text='Видалити тест 🗑', callback_data=AdminFactory(action='delete_test'))
        if is_available:
            builder.button(text='Закрити тест 📁', callback_data=AdminFactory(action='disable_test'))
        else:
            builder.button(text='Відкрити тест 📂', callback_data=AdminFactory(action='enable_test'))
        builder.button(text='Назад', callback_data=AdminFactory(action='select_edit'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def edit_title() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='edit_test'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def confirm_title() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='edit_title', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='edit_title', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def confirm_delete_test() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='delete_test', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='delete_test', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def select_edit_exercise() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Додати завдання 🔗', callback_data=AdminFactory(action='add_exercise_start'))
        builder.button(text='Переглянути завдання 👀', callback_data=AdminFactory(action='edit_exercise'))
        builder.button(text='Назад', callback_data=AdminFactory(action='select_edit'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def edit_exercise(exercises_numbers) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        col = 0
        rows = 1

        for i in range(1, max(exercises_numbers) + 1):
            text = f'{i}' if i in exercises_numbers else '  '
            callback_data = (
                AdminFactory(action='edit_exercise', value=f'{i}') if i in exercises_numbers
                else AdminFactory(action="ignore")
            )
            builder.button(text=text, callback_data=callback_data)

            if col >= 6:
                col = 1
                rows += 1

            col += 1

        if 6 > col >= 0:
            for _ in range(6 - col):
                builder.button(text='  ', callback_data=AdminFactory(action='ignore'))

        builder.button(text='Назад', callback_data=AdminFactory(action='edit_exercises'))

        builder.adjust(*[6] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def add_exercise(correct_answer_is_available, options_are_available, is_finished) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Номер 🔢', callback_data=AdminFactory(action='add_exercise_number'))
        builder.button(text='Фото 📷', callback_data=AdminFactory(action='add_exercise_photo'))
        builder.button(text='Тип ⁉️', callback_data=AdminFactory(action='add_exercise_type'))

        if options_are_available:
            builder.button(text='Варіанти відповіді 📝', callback_data=AdminFactory(action='add_exercise_options'))

        if correct_answer_is_available:
            builder.button(text='Правильна відповідь ✔️', callback_data=AdminFactory(action='add_exercise_answer'))

        builder.button(
            text='Навчальний матеріал 📚',
            callback_data=AdminFactory(action='add_exercise_educational_material')
        )
        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='edit_exercises'))

        if is_finished:
            builder.button(text='Додати завдання ✅', callback_data=AdminFactory(action='add_exercise'))

        if options_are_available:
            builder.adjust(1, 1, 2, 1, 1, 2)

        else:
            if not correct_answer_is_available:
                builder.adjust(1)
            else:
                builder.adjust(1, 1, 2, 1, 2)

        return builder.as_markup()

    @staticmethod
    def add_exercise_cancel() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def select_exercise_type(data, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder, rows = build_columns_from_dict(builder, data, "add_exercise_type", AdminFactory, selected, 2)
        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))

        builder.adjust(*[2] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def select_exercise_options(data, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder, rows = build_columns_from_dict(builder, data, "add_exercise_options", AdminFactory, selected, 2)
        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))

        builder.adjust(*[2] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def select_exercise_answer(data, selected) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder, rows = build_columns_from_dict(builder, data, "add_exercise_answer", AdminFactory, selected, 2)
        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))

        builder.adjust(*[2] * rows, 1)
        return builder.as_markup()

    @staticmethod
    def select_exercise_answer_c(letters, numbers, selected, is_done) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder = build_columns_from_dict_letters(
            builder, 'add_exercise_answer_c', AdminFactory, letters, numbers, selected
        )
        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))
        if is_done:
            builder.button(text='Підтвердити ✅', callback_data=AdminFactory(action='add_exercise_answer_c'))

        builder.adjust(*[len(letters) + 1] * (len(numbers) + 1), 2)
        return builder.as_markup()

    @staticmethod
    def select_exercise_answer_3(numbers, selected, is_done) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder = build_columns_from_dict_numbers(
            builder, 'add_exercise_answer_3', AdminFactory, numbers, selected
        )

        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='add_exercise_back'))
        if is_done:
            builder.button(text='Підтвердити ✅', callback_data=AdminFactory(action='add_exercise_answer_3'))

        builder.adjust(*[len(numbers)] * 2, 2)
        return builder.as_markup()

    @staticmethod
    def edit_chosen_exercise() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Видалити завдання 🗑', callback_data=AdminFactory(action='delete_exercise'))
        builder.button(text='Назад', callback_data=AdminFactory(action='edit_exercise'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def confirm_delete_exercise() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='delete_exercise', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='delete_exercise', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def send_message_to_all() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Відхилити 🔻', callback_data=AdminFactory(action='cancel'))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def confirm_send_message_to_all() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='do_send_message_to_all', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='do_send_message_to_all', value='1'))

        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def confirm_generate_promocode() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='🔴 Ні', callback_data=AdminFactory(action='confirm_generate_promocode', value='0'))
        builder.button(text='🟢 Так', callback_data=AdminFactory(action='confirm_generate_promocode', value='1'))

        builder.adjust(2)
        return builder.as_markup()
