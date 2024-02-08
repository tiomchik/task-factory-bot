# Task Factory Telegram bot (RU)

The bot allows you to make a list of tasks and display their status. It is also possible to add daily tasks for easier tracking. The bot can help you not forget about the reward you have assigned, which you will receive for completing the task.

## How to start the project

1. Create a bot via [BotFather](https://t.me/BotFather/).

2. Clone this repository.

3. Create and activate the virtual enviroment:

Windows:
```powershell
py -m venv .venv
& .venv/scripts/activate.ps1
```
UNIX:
```bash
python3 -m venv .venv
source .venv/scripts/activate.ps1
```

4. Install the requirements:
```powershell
pip install -r requirements.txt
```

5. Change directory to src folder:

```powershell
cd src
```

6. Create .env file in src folder and paste the received bot token in key `BOT_TOKEN`:

```properties
BOT_TOKEN=YOUR_API_TOKEN
```

7. Start bot:

```powershell
python main.py
```

## License

Code is licensed under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
