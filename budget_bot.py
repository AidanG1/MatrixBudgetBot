from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler
from dotenv import load_dotenv
from deta import Deta
import os, requests

load_dotenv()

# Global variables
USERNAME = "budget_bot"  # Bot's username
PASSWORD = os.environ.get('PASSWORD')  # Bot's password
SERVER = "https://matrix.org"  # Matrix server URL
PROJECT_KEY = os.environ.get('PROJECT_KEY')

deta = Deta(PROJECT_KEY)
users = deta.Base('users')


def hi_callback(room, event):
    room.send_text("Hi, " + event['sender'])


def monthly_budget_callback(room, event):
    budget = event['content']['body'].split()[1]
    user = next(users.fetch({"matrix": event['sender']}))[0]
    users.update({'budget': budget}, user['key'])
    room.send_text(f'Your budget has been set to ${budget}')


def review_purchases(room, event):
    pass


def link_capital_one_account(room, event):
    c1id = event['content']['body'].split()[1]
    users.insert({
        "matrix": event['sender'],
        "capital_one_id": c1id,
    })


def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)
    print(bot)
    print('hi')

    # Add a regex handler waiting for the word Hi
    hi_handler = MRegexHandler("Hi", hi_callback)
    bot.add_handler(hi_handler)

    # Add a regex handler waiting for the echo command
    linkc1_handler = MCommandHandler("link_capital_one", link_capital_one_account)
    bot.add_handler(linkc1_handler)

    monthly_budget_handler = MCommandHandler("monthly_budget", monthly_budget_callback)
    bot.add_handler(monthly_budget_handler)



    # Start polling
    bot.start_polling()

    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()


if __name__ == "__main__":
    main()