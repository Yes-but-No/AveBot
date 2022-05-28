from AveBot.AveBot import AveBot, get_setup_from_env

setup = get_setup_from_env()

bot = AveBot(setup)

bot.run()