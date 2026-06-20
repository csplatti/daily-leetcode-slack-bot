# daily-leetcode-slack-bot

## About
A bot for slack which tracks the leetcode profiles of channel members, sending a daily update showing who completed problems each day

## Setting Up Docker
```bash
cd backend  

docker build -t csplatti/daily-lc-bot-backend:1.2 .  

docker run -p [outside-port]:8000 --env-file ../.env -e DB_HOST=host.docker.internal [image-id]
```
