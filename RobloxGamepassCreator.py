import requests
import re
from rich.console import Console
import os
from rich.prompt import IntPrompt
import time
from playwright.sync_api import sync_playwright

console = Console()


def get_numbers_from_string(input_string):
    numbers = re.findall(r'\d+', input_string)
    if numbers:
        return ''.join(numbers)
    else:
        return None


def create_gamepasses(UserID,page):
    prices = [2, 5, 7, 10, 15, 25, 50, 75, 100, 175, 249, 499, 749, 1000, 2499, 5000, 10000]

    for price in prices:
        gamepass_name = "gaspas"
        gamepass_desc = "ehehehe"
        gamepass_price = str(price)
        page.goto(f"https://create.roblox.com/dashboard/creations/experiences/{UserID}/associated-items?activeTab=Pass")
        page.wait_for_selector('button[data-testid="createAssociatedItemsButton"]')
        page.click('button[data-testid="createAssociatedItemsButton"]')
        page.fill('textarea[id="name"]', gamepass_name)
        page.fill('textarea[id="description"]', gamepass_desc)
        time.sleep(1)
        page.click('button[data-testid="create-pass-button"]')
        time.sleep(2)
        page.click('img[alt*=gaspas]')
        gamepass_url = page.url
        split = gamepass_url.split("/")
        gamepass_id = split[-2]
        page.goto(f"https://create.roblox.com/dashboard/creations/experiences/4456367954/passes/{gamepass_id}/sales")
        page.click('input[name="isForSale"]')
        page.fill('input[id="priceTextField"]', gamepass_price)
        page.click('button.MuiButton-root.MuiButton-contained.MuiButton-containedPrimary')
        time.sleep(1)
        console.log(f"Gamepass Created (ID : {gamepass_id}, Price : {price})")


def get_game_id(UserID):
    api_url = f'https://games.roblox.com/v2/users/{UserID}/games?limit=10'
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                game_id = data['data'][0]['id']
                return game_id
            else:
                console.log('No data found in the response.')
                return None
        else:
            console.log(f'Failed to fetch data from Roblox API. Status code: {response.status_code}')
            return None
    except Exception as e:
        console.log(f'An error occurred: {str(e)}')
        return None


def start(username, password):
    try:
        with sync_playwright() as pw:
            browser = pw.firefox.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.set_viewport_size({"width": 640, "height": 480})
            login_url = "https://roblox.com/login"
            page.goto(login_url)
            time.sleep(2)
            page.click('button.btn-cta-lg.cookie-btn.btn-primary-md.btn-min-width')
            page.fill('input[id="login-username"]', username)
            page.fill('input[id="login-password"]', password)
            page.click('button[id="login-button"]')
            page.wait_for_load_state()

            time.sleep(5)
            page.wait_for_selector('a.text-link.dynamic-overflow-container')
            page.click('a.text-link.dynamic-overflow-container')
            page.wait_for_load_state()
            profile_url = page.url
            console.log(f"Profile URL: {profile_url}")
            user_id = get_numbers_from_string(profile_url)
            if user_id:
                console.log(f"Extracted UserID: {user_id}")
                GameID = get_game_id(user_id)
            else:
                console.log("Unable to extract UserID from the URL")

            create_gamepasses(GameID,page)
            time.sleep(1)
            browser.close()

    except:
        console.log("Unexpected Error Occured.")

def start2():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.rule('[bold red]Gamepass Creator[/]')
        amount = IntPrompt.ask('1 : Create gamepasses for all of the accounts in "accounts.txt" \n2 : Give username and password to create gamepasses to that account \n3 : Custom amount of accounts from "accounts.txt" \nSelect')

        if amount == 1:
            with open('accounts.txt', 'r') as file:
                for line in file:
                    username, password = line.strip().split(':')
                    start(username, password)

        if amount == 2:
            username = input("Input Username : ")
            password = input("Input Password : ")
            start(username, password)

        if amount == 3:
            amount_to_generate = IntPrompt.ask("Custom number to generate ")
            with open('accounts.txt', 'r') as file:
                for i, line in enumerate(file):
                    if i >= amount_to_generate:
                        break
                    username, password = line.strip().split(':')
                    start(username, password)

    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    start2()
