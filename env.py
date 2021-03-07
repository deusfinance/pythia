import os


def load_env(config_file=".env"):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file))