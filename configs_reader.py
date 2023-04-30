from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        # Имя файла, откуда будут прочитаны данные
        env_file = '.env'
        # Кодировка читаемого файла
        env_file_encoding = 'utf-8'


config = Settings()
