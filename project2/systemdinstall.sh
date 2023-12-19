#!/bin/bash
if [ -n "$1" ]
then
rm /etc/systemd/system/bot_handlers.service
rm /etc/systemd/system/bot_orders.service
rm /etc/systemd/system/bot_tokens.service
touch /etc/systemd/system/bot_handlers.service
touch /etc/systemd/system/bot_orders.service
touch /etc/systemd/system/bot_tokens.service
echo -e "[Unit]\nDescription=bot Handlers\nAfter=network.target\n\n[Service]\nWorkingDirectory=$1\nUser=root\nGroup=root\n\nRestart=always\n\nExecStart=/usr/bin/python3 handlers.py\n\n[Install]\nWantedBy=multi-user.target" >> /etc/systemd/system/bot_handlers.service
echo -e "[Unit]\nDescription=bot Orders\nAfter=network.target\n\n[Service]\nWorkingDirectory=$1\nUser=root\nGroup=root\n\nRestart=always\n\nExecStart=/usr/bin/python3 orders.py\n\n[Install]\nWantedBy=multi-user.target" >> /etc/systemd/system/bot_orders.service
echo -e "[Unit]\nDescription=bot Tokens\nAfter=network.target\n\n[Service]\nWorkingDirectory=$1\nUser=root\nGroup=root\n\nRestart=always\n\nExecStart=/usr/bin/python3 tokens.py\n\n[Install]\nWantedBy=multi-user.target" >> /etc/systemd/system/bot_tokens.service
systemctl enable --now bot_handlers
systemctl enable --now bot_orders
systemctl enable --now bot_tokens
else
echo "Укажите абсолютную рабочую директорию (например: /opt/bot)"
fi