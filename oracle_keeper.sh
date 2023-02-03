#!/bin/bash

py_path="/usr/local/oracle_keeper/oracle_keeper.py"

check() {
  if [ -f /usr/local/oracle_keeper/oracle_keeper.py ]; then
    return 1
  else
    return 0
  fi
}

install() {
  mkdir -p /usr/local/oracle_keeper
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.service -O /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
  systemctl enable oracle_keeper
  systemctl start oracle_keeper
}

update() {
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
  systemctl restart oracle_keeper
}

uninstall() {
  systemctl stop oracle_keeper
  systemctl disable oracle_keeper
  rm -rf /usr/local/oracle_keeper
  rm -rf /etc/oracle_keeper
  rm /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
}

RunScript() {
  check_result=$(check)

  if [ "$1" = "install" ]; then
    if [ check_result ]; then
      uninstall
      install
    else
      install
    fi
  elif [ "$1" = "update" ]; then
    if [ check_result ]; then
      update
    else
      install
    fi
  elif [ "$1" = "uninstall" ]; then
    uninstall
  else
    echo "Error command"
  fi
}

RunScript $1

echo "脚本执行完成"
