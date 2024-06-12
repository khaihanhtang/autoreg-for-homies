This is the source code for auto-registering badminton slots, dedicated to badminton group Homies. This source code requires running on a server to handle requests from users via a Telegram bot.

## License
This source code [autoreg-for-homies](https://github.com/khaihanhtang/autoreg-for-homies) is licensed under [Apache License 2.0](https://github.com/khaihanhtang/autoreg-for-homies/blob/main/LICENSE).

## Statement of Data Collection
This source code [autoreg-for-homies](https://github.com/khaihanhtang/autoreg-for-homies) is open-sourced, non-profit, and auditable/verifiable by any public party. We use the library [python-telegram-bot](https://python-telegram-bot.org/), whose source code is in [this link](https://github.com/python-telegram-bot/python-telegram-bot), as a subroutine to send and receive messages from users. The following types of data are those that the bot collects:
1. Public information of users in the chat where the bot is among the participants. Public information includes Telegram ID, full name (first name and surname), and username.
2. The messages users send to control the bots, namely, those starting with "/".
3. Those collected by the above-mentioned library [python-telegram-bot](https://python-telegram-bot.org/) which are out of our control.

## Setup
The setup of this bot may differ in different operating systems. This guide here is for Windows 10/11. To set up the bot, please do the followings:
1. Install Python 3.xx (tested with Python 3.12 at the time) from Microsoft Store. Or use other source of suitable installations for Python 3.xx.
2. Install package `python-telegram-bot` from `pip` by running command `pip install python-telegram-bot` in Terminal (or Command Prompt, Windows PowerShell). See [python-telegram-bot](https://python-telegram-bot.org/) for more details. 
3. Open Terminal inside directory `autoreg-for-homies`. Run the bot by typing `python main.py` (or `python3 main.py` in Linux).
4. You will be required to enter the bot token. If you do not have bot token, please create a bot from [BotFather](https://t.me/BotFather) to get the bot and the corresponding token. You also need to specify the list of admins (via Telegram username) and the `chat_id` of the Telegeram group chat for the bot to work in the file [config.py](https://github.com/khaihanhtang/autoreg-for-homies/blob/main/config.py).
