# Telegram-template



## Getting started
docker-compose up

If you want to use Poetry:
sudo docker-compose -f docker-compose-poetry.yml up


### Local
To locally start, you need to create a tunnel and copy the "Forwarding" from "ngrok" to the environment variable "WEBHOOK_PATH."

sudo snap install ngrok # https://dashboard.ngrok.com/get-started/setup

ngrok http 8001

OR use serveo

ssh -R ferry_timetable:80:localhost:8001 serveo.net







## For manual set up telegram hook

https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}

https://api.telegram.org/bot6449572797:AAGcL2Of8lqhtyQ8uzf-s9DGY6ut8CLGu7E/setWebhook?url=https://8b2d-95-47-150-96.ngrok-free.app