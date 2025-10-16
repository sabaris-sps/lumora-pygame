# What is this?

This is a zelda styled game created with pygame.
Movement of the player is done through hand control from camera

# Setup Process

If pyenv is not installed, open Powershell as administrator and execute
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"`

`pyenv install 3.12.2
pyenv global 3.12.2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py`

### Here's a pic of the game.

![Game Screenshot](./readme/game-screenshot.png "Game Screenshot")

## Movement instructions

- Make a fist - lock movement
- Index finger up - Move
- Thumb finger out - Attack
- Index + Thumb finger out - Move + attack
- Open palm - Magic
