from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_columns_from_dict(
        builder: InlineKeyboardBuilder,
        data: dict,
        action: str,
        factory,
        selected: list[int] = [],
        columns: int = 3
) -> tuple[InlineKeyboardBuilder, int]:
    """
    This build will return builder and num rows

    :builder: builder for add button
    :data: for set in buttons
    :action: for factory
    :factory: factory
    :columns: max elements in one row
    """

    col = 0
    rows = 1

    # build button
    for id, name in data.items():

        builder.button(
            text=f"🟢 {name}" if id in selected else name,
            callback_data=factory(action=action, value=str(id))
        )

        if col > columns:
            col = 1
            rows += 1

        col += 1

    # build empty button
    if columns > col >= 0:
        for _ in range(columns - col):
            builder.button(text='  ', callback_data=factory(action='ignore'))

    return builder, rows


def build_columns_from_dict_letters(
        builder: InlineKeyboardBuilder,
        action: str,
        factory,
        letters: dict,
        numbers: dict,
        selected: dict,
) -> InlineKeyboardBuilder:
    """
    This build will return builder and num rows

    :builder: builder for add button
    :data: for set in buttons
    :action: for factory
    :factory: factory
    :columns: max elements in one row
    """

    builder.button(text='  ', callback_data=factory(action='ignore'))
    for letter_id, letter in letters.items():
        builder.button(text=letter, callback_data=factory(action='ignore'))

    for number_id, number in numbers.items():
        builder.button(text=number, callback_data=factory(action='ignore'))
        for letter_id, letter in letters.items():
            try:
                text = '🟢' if selected[number_id] == letter_id else '  '
            except (IndexError, KeyError):
                text = '  '
            builder.button(text=text, callback_data=factory(action=action, value=f'{number_id}-{letter_id}'))

    return builder


def build_columns_from_dict_numbers(
        builder: InlineKeyboardBuilder,
        action: str,
        factory,
        numbers: dict,
        selected: dict,
) -> InlineKeyboardBuilder:
    """
    This build will return builder and num rows

    :builder: builder for add button
    :data: for set in buttons
    :action: for factory
    :factory: factory
    :columns: max elements in one row
    """

    for _, number in numbers.items():
        builder.button(text=number, callback_data=factory(action='ignore'))
    for number_id, _ in numbers.items():
        try:
            if number_id in selected:
                builder.button(text='🟢', callback_data=factory(action='ignore'))
            else:
                builder.button(text='  ', callback_data=factory(action=action, value=f"{number_id}"))
        except (IndexError, KeyError):
            builder.button(text='  ', callback_data=factory(action='ignore'))

    return builder
