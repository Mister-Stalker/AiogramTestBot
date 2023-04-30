import re

from aiogram import filters, types


class TextInputRegexFilter(filters.BaseFilter):
    """
    Фильтр с регулярным выражением
    """
    on_false_text = "ваше сообщение не подходит установленному фильтру"

    def __init__(self,
                 pattern: str,
                 text: str = "",
                 send_default_text: bool = False,
                 is_command: bool = False,
                 ) -> None:
        """
        Фильтр с регулярным выражением для проверки введенного текста

        :param pattern: регулярное выражение
        :param text: текст при не прохождении фильтра (пустой - нет текста)
        :param send_default_text: отправлять ли дефолтный текст при не прохождении фильтра
        :param is_command: команда или просто текст (в командах игнорируется первое "слово")
        """
        self.pattern = pattern
        self.text = text
        self.send_default_text = send_default_text
        self.is_command = is_command

    async def __call__(self, message: types.Message):
        if re.fullmatch(self.pattern, " ".join(message.text.split()[1:]) if self.is_command else message.text):
            return True
        if self.text:
            await message.reply(self.text)

        elif self.send_default_text:

            await message.reply(self.on_false_text)


class TextInputFilterOnlyText(TextInputRegexFilter):
    on_false_text = "Доступны только буквы, цифры и пробелы"

    def __init__(self, send_text=True):
        """
        фильтр на ввод только букв, цифр, пробелов и нижних подчеркиваний
        просто обертка на TextInputRegexFilter

        :param send_text: отправлять ли сообщение если проверка не пройдена
        """
        super().__init__(pattern=r"[\w\s]+",
                         text=self.on_false_text if send_text else "", )
