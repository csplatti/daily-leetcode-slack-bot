CREATE TABLE IF NOT EXISTS users (
    workspace_id      TEXT    NOT NULL,
    slack_user_id     TEXT    NOT NULL,
    leetcode_username TEXT    NOT NULL,
    current_streak    INTEGER NOT NULL DEFAULT 0,
    max_streak        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (workspace_id, slack_user_id)
);
