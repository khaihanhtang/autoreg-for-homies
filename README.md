This is the source code for auto-registering badminton slots, dedicated to badminton group Homies. This source code requires running on a server to handle requests from users via a Telegram bot.

## License
This source code [autoreg-for-homies](https://github.com/khaihanhtang/autoreg-for-homies) is licensed under [Apache License 2.0](https://github.com/khaihanhtang/autoreg-for-homies/blob/main/LICENSE).

## Statement of Data Collection
This source code [autoreg-for-homies](https://github.com/khaihanhtang/autoreg-for-homies) is open-sourced, non-profit, and auditable/verifiable by any public party. We use the library [python-telegram-bot](https://python-telegram-bot.org/), whose source code is in [this link](https://github.com/python-telegram-bot/python-telegram-bot), as a subroutine to send and receive messages from users. The following types of data are those that the bot collects:
1. Public information of users in the chat where the bot is among the participants. Public information includes Telegram ID, full name (first name and surname), and username.
2. The messages users send to control the bots, namely, those starting with "/".
3. Those collected by the above-mentioned library [python-telegram-bot](https://python-telegram-bot.org/) which are out of our control.

For `/ai` questions that need AI, the bot sends the question text and built-in help topics to Cloudflare Workers AI. Any details you type are included in that request. The bot looks up your alias or Telegram name locally when it fills in a command. Keep sensitive details out of questions. [Cloudflare Workers AI data usage](https://developers.cloudflare.com/workers-ai/platform/data-usage/)

## Setup
The setup of this bot may differ in different operating systems. This guide here is for Windows 10/11. To set up the bot, please do the followings:
1. Install Python 3.xx (tested with Python 3.12 at the time) from Microsoft Store. Or use other source of suitable installations for Python 3.xx.
2. Install `python-telegram-bot` with JobQueue support by running `pip install "python-telegram-bot[job-queue]"` in Terminal (or Command Prompt, Windows PowerShell). See [python-telegram-bot](https://python-telegram-bot.org/) for more details.
3. Open Terminal inside directory `autoreg-for-homies`. Run the bot by typing `python main.py` (or `python3 main.py` in Linux).
4. The console prompts for the Telegram bot token, Cloudflare account ID, and Cloudflare Workers AI API token at startup. If you do not have a bot token, please create a bot with BotFather to get one. You also need to specify the admins (via Telegram username) and the `chat_id` of the Telegram group in `config.py`. [BotFather](https://t.me/BotFather) · [config.py](https://github.com/khaihanhtang/autoreg-for-homies/blob/main/config.py)

Keep the same `data` directory when restarting. The bot saves the lock, active and staged lists, and release schedule together in `data/state.json`. On a first run without that file, it loads any existing list and schedule files. Earlier versions had no saved lock setting, so that first load starts unlocked.

Admins can use `/testnotitime HH:MM:SS DD/MM/YYYY` to exercise the recurring release flow. It starts at the supplied Singapore time, repeats every 5 minutes, clears the active list and unlocks registration 2 minutes before release, and sends a reminder 1 minute before release. Like `/weeklynotitime`, a recurring occurrence only prepares and publishes when a replacement list has been staged.

## AI command help

`/ai [question]` suggests commands from the bot's built-in English guide and declines unrelated questions. Try `/ai tôi muốn vào danh sách slot a`. If your alias is Alex, the bot suggests `/rg Alex a`. For signup, reserve, and removal requests about yourself, the bot uses your `/aka` alias when set and your Telegram full name otherwise. You can supply a name explicitly. Use the **Copy** button and paste the command into Telegram. Fill in any placeholders in a template before sending it.

In the registration group, you can also ask for a slot by name, such as `/ai tôi muốn vào slot có tên là Buổi tối`. The bot looks up the label from the active list. If the name matches several slots, check `/all` and use the label for the one you want.

In the Cloudflare dashboard, open **Workers AI** and select **Use REST API**. Create a Workers AI API token and copy your account ID. Run `python main.py` in a terminal and enter both values after the Telegram bot token. The terminal hides the Workers AI token as you type. [Workers AI REST API setup](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)

`/ai` handles common requests in English and Vietnamese directly. It uses Gemma 4 26B on Cloudflare Workers AI for other wording. The Workers Free plan includes 10,000 Neurons of inference per day. [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)

## Acknowledgments

OpenAI Codex provided AI coding assistance for the updates to `/notitime`, the addition of `/weeklynotitime` and `/state`, the configurable pre-release reset and unlock, and state recovery after a restart.
