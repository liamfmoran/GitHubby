# GitHubby Crawler

| Object | Description |
|--|--|
| __User__ |
| `login` | Login id used for tracking users. |
| `id` | Unique id used for database. |
| `avatar_url` | Used for displaying image of avatar. |
| `followers_url` | Used to find follower users. |
| `following_url` | Used to find following users. |
| `starred_url` | Used for getting starred repos. |
| `subscriptions_url` | Used for getting subscribed to repos. |
| `repos_url` | Used for getting owned repos. |
| `events_url` | Events done by user. |
| `name` | Actual name of user. |
| `company` | Company of user. |
| `blog` | Blog of user. |
| `location` | Location of user. |
| `bio` | Bio of user. |
| `public_repos` | Count of public repos. |
| `followers` | Count of followers. |
| `following` | Count of users following. |
| `created_at` | Maturity of the user account. |
| `updated_at` | Last update of user account. |
| __Repo__ |
| `id` | Id used for tracking repos. |
| `name` | Used for display. |
| `full_name` | Used for display too? |
| `description` | Used to show description of repo. |
| `forks_url` | Projects that have been created from fork. |
| `events_url` | Could be very useful for finding the importance of repositories. |
| `languages_url` | Languages used in project. |
| `created_at` | When the proejct was created. |
| `updated_at` | When the project was last updated. |
| `pushed_at` | When the project was last pushed to. |
| `size` | The size of the repo. |
| `stargazers_count` | Use Number of Stars to rank. |
| `langauge` | Primary language of project. |
| `has_wiki` | Whether or not the project has a wiki. |
| `forks_count` | How many have forked his repo. |
| `open_issues_count` | How many issues are currently open. |


### Idea

We should use a database system with IDs to grab info. Then when a user has some repos, we can use them to grab the appropriate info.
