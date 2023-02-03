#!/bin/bash

install() {
  mkdir -p /usr/local/oracle_keeper
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/Shell/master/oracle_keeper/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/Shell/master/oracle_keeper/oracle_keeper.service -O /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
  systemctl enable oracle_keeper
  systemctl start oracle_keeper
}

update() {
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/Shell/master/oracle_keeper/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
  systemctl restart oracle_keeper
}

uninstall() {
  systemctl stop oracle_keeper
  systemctl disable oracle_keeper
  rm -rf /usr/local/oracle_keeper
  rm /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
}

RunScript() {
  if [ "$1" = "install" ]; then
    install
  elif [ "$1" = "update" ]; then
    update
  elif [ "$1" = "uninstall" ]; then
    uninstall
  else
    echo "Error command"
  fi
}

RunScript $1
