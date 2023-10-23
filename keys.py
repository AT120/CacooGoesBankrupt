#TODO: заменить на config.py

def get_cacoo_api_key() -> str:
    with open("sensitive/cacoo_key.txt") as f:
        return f.readline()[:-1]

def get_discord_token() -> str:
    with open("sensitive/discord_key.txt") as f:
        return f.readline()[:-1]