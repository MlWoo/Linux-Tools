#!/bin/bash

VAR=$(expect -c '
  set host "10.128.X.14"
  set user_pwd "menglin"
  set partition "/dev/sda6"
  log_user 0
  spawn ssh $user_pwd@$host
  expect {
    timeout   { puts "Timeout or EOF\n"; exit 1 }
    eof       { puts "Connection rejected by the host\r"; exit 2 }
    "password:"
  }
  send "$user_pwd\r"
  expect "\$ "
 
  send "df -h | grep $partition \r"
  expect $partition
  expect "*\r"
  send_user  "$expect_out(0,string)\n"
  close
  exit 0
')
echo $VAR






