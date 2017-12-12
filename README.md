# GitHubby

_Like Tinder, but for women looking for commitment._

## How to get started

0. Install Python 3 on your system
1. Install `Flask` with the command `pip3 install --upgrade Flask`
2. Install `gender-guesser` with the command `pip3 install --upgrade gender-guesser`
3. Install `google-cloud-bigquery` with the command `pip3 install --upgrade google-cloud-bigquery`

#### API Authenticaion

- Generate a `creds.json` file for [Google Cloud API Authentication](https://cloud.google.com/docs/authentication/getting-started)
- Create a `tokens.txt` file for [GitHub Personal API Tokens](https://github.com/blog/1509-personal-api-tokens) with one token per line
- Place both of the above files in the `./crawler/` directory

### On Windows

1. On CMD, enter `set FLASK_APP=app.py` (or `$env:FLASK_APP="app.py"`)
2. Run `flask run`

### On Mac

1. On Terminal, enter `export FLASK_APP=app.py`
2. Run `flask run`
