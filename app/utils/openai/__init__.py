import openai

from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()


def start_openai():
    client = openai.AsyncOpenAI(
        api_key=keys["OPEN_AI_KEY"],
    )
    return client