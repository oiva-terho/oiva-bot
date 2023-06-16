# Telegram bot to handle documents

The idea was in saving documents to computer through telegram. 

_Of course, I could just use USB cable or send to someone and download through Telegram Desktop. But it's fun to make own bot, isn't it?_

## Features
- [x] Does not need commands
- [x] Works with list of authorized users, so can be uses by whole family
- [x] Accepts jpg, pdf, doc formats
- [x] Saves documents in separate folders by name of owner
- [x] Names documents in format: Name_of_owner. Name_of_document
- [x] Check if document already exist and ask to replace or rename
- [ ] Gives back document if to ask for it
- [x] Saves log of messages sent, may be usefull to keep thoughts


## Setup

1.  Get your Telegram bot token from [@BotFather](https://t.me/BotFather)

2. Clone project
    ```bash
    git clone https://github.com/oiva-terho/oiva-bot.git oiva-bot
    cd oiva-bot
    ```
 
3. Install environment
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

4. Edit `config.example.yml` to set your tokens and authorized users, then run next command to rename:
    ```bash
    mv config.example.yml config.yml
    ```

5. Start the bot
    ```bash
    python bot.py
    ```