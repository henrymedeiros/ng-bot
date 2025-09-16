DISCORD_BOT_TOKEN = "your-discord-bot-token-here"


try:
    from config_local import *
    print("Using config_local.py")
except ImportError:
    print("No config_local.py, using default values.")
