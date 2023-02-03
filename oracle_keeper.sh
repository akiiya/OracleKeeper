#!/bin/bash

check() {
  if [ -f /usr/lib/systemd/system/oracle_keeper.service ]; then
    return 1
  else
    return 0
  fi
}

install() {
  check
  if [[ $? == 1 ]]; then
    uninstall
  fi

  mkdir -p /usr/local/oracle_keeper
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
  wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.service -O /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
  systemctl enable oracle_keeper
  systemctl start oracle_keeper
  echo '服务安装完成'
}

update() {
  check
  if [[ $? == 0 ]]; then
    install
  else
    wget -N --no-check-certificate https://raw.githubusercontent.com/akiiya/OracleKeeper/master/oracle_keeper.py -O /usr/local/oracle_keeper/oracle_keeper.py
    systemctl restart oracle_keeper
    echo '服务更新完成'
  fi
}

uninstall() {
  systemctl stop oracle_keeper
  systemctl disable oracle_keeper
  rm -rf /usr/local/oracle_keeper
  rm -rf /etc/oracle_keeper
  rm /usr/lib/systemd/system/oracle_keeper.service
  systemctl daemon-reload
  echo '服务卸载完成'
}

if [ "$1" = "install" ]; then
  install
elif [ "$1" = "update" ]; then
  update
elif [ "$1" = "uninstall" ]; then
  uninstall
else
  echo "Error command"
fi
