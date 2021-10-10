from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from matrix_bot_api.mregex_handler import MRegexHandler
from matrix_bot_api.mcommand_handler import MCommandHandler
from dotenv import load_dotenv
from deta import Deta
import os, datetime, requests

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
    user = users.fetch({"matrix": event['sender']}).items[0]
    users.update({'budget': budget}, user['key'])
    room.send_text(f'Your budget has been set to ${budget}')


def review_purchases(room, event):
    u_key = users.fetch({"matrix": event['sender']}).items[0]['key']
    r = requests.get(f'http://api.nessieisreal.com/accounts/{u_key}/purchases?key={os.environ.get("CAPITAL_ONE_KEY")}')
    transactions = r.json()
    merchant_counts = {}
    for transaction in transactions:
        if transaction.merchant_id in merchant_counts:
            merchant_counts['merchant_id'] += 1
        else:
            merchant_counts['merchant_id'] = 0
    high_purchase_merchants = []
    for merchant, count in merchant_counts.items():
        if count > 0.2 * len(transactions):
            high_purchase_merchants.append(merchant)


def link_capital_one_account(room, event):
    c1id = event['content']['body'].split()[1]
    users.insert({
        "matrix": event['sender'],
        "capital_one_id": c1id,
    })
    room.send_text('Matrix successfully linked to Capital One')


def main():
    # Create an instance of the MatrixBotAPI
    bot = MatrixBotAPI(USERNAME, PASSWORD, SERVER)
    print(f'{bot} intialized at time {datetime.datetime.now()}')

    # Add a regex handler waiting for the word Hi
    hi_handler = MRegexHandler("Hi", hi_callback)
    bot.add_handler(hi_handler)

    # Add a regex handler waiting for the echo command
    linkc1_handler = MCommandHandler("link_capital_one", link_capital_one_account)
    bot.add_handler(linkc1_handler)

    monthly_budget_handler = MCommandHandler("monthly_budget", monthly_budget_callback)
    bot.add_handler(monthly_budget_handler)

    review_purchases_handler = MCommandHandler("review_purchases", review_purchases)
    bot.add_handler(review_purchases_handler)

    # Start polling
    bot.start_polling()

    # Infinitely read stdin to stall main thread while the bot runs in other threads
    while True:
        input()


if __name__ == "__main__":
    main()
