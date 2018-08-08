#coding= utf-8
import time
import re
import sched
import os
import smtplib
import socket
user = "menglinwoo@gmail.com"
pwd = ''
sent_from = user
def send_email(to, email_text):
    try:
        print(' The storage will run out, try to send email')
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user=user, password=pwd)
        server.sendmail(sent_from, to, email_text)
        server.close()
    except:
        print('Something went wrong when logining the gmail...')

storage_threshold = 50

day_to_seconds = 24*3600

def job(inc):
    rst = os.popen("./script.sh")
    try:
        rst_list = rst.read().split()
        avail = rst_list[3]
        avail_num_s = re.compile(r'[1-9]\d*').findall(avail)
        avail_num = int(avail_num_s[0])
        if avail_num < storage_threshold:
            to = ['@cloudwalk.cn']
            subject = 'Storage WARNING'
            body = """Hey, all,\n The storage will run out, plz clear useless files ASAP.\n --wumenglin"""
            email_text = 'Subject: {}\n\n{}'.format(subject, body)
            send_email(to, email_text)
            return day_to_seconds  #send the email in the next day
        else:
            return inc
    except:
        print('Something went wrong when executing the scripts...')
        to = ['menglin@163.com']
        subject = 'System BROKENDOWN'
        body = """Hey, all,\n The sytem to check storage usage was broken, plz fix ASAP.\n --wumenglin"""
        email_text = 'Subject: {}\n\n{}'.format(subject, body)
        send_email(to, email_text)
        os._exit()
        

schedule = sched.scheduler(time.time, time.sleep)

def execute_command(inc):
    inc = job(inc)
    schedule.enter(inc, 0, execute_command, (inc,))

def main(inc=60):
    schedule.enter(0, 0, execute_command, (inc,))
    schedule.run()

if __name__ == '__main__':
    main(300)





