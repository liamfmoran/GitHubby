# GitHubby

_Like Tinder, but for women looking for commitment._

## How to get started (for checkpoint 2)

1. Install Python 3 with Pip
2. Install `gender-guesser` with the command `pip3 install gender-guesser`
3. Run `core.py` with `python3 core.py`

### Web App

#### On Windows

1. On CMD, enter `set FLASK_APP=app.py` (or `$env:FLASK_APP="app.py"`)
2. Run `flask run`

#### On Mac

1. On Terminal, enter `export FLASK_APP=app.py`
2. Run `flask run`

## Features

### Users

- Location
- Primary langauge (determined from their repos)
- Number of repos
- Number of followers
- Number of following
- Weight of repos (determined by repo score)

#### Commits

- Number of total commits
- Distribution of commits
- Uniformity of distribution
- Average commits over a given period of time (use RMSE)
- Importance of commits (whether or not on master, importance of repo)
- __NOT__ size of commits, because size doesn't matter

#### Repos

- Number of watchers
- Number of stars
- Number of contributors
- Number of issues
- Number of pull requests