import subprocess
from collections import deque
from time import sleep
import json

j = json.loads(open('config.json').read())

adb = j['adb_path'] + ' '
time_to_sleep = j['time_to_sleep']

logs = deque(maxlen=100)


def get_current_activity():
    return subprocess.getoutput(adb + "shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")


# output = subprocess.getoutput(adb + " shell dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
# print(output)
def isAtDingLogin():
    output = get_current_activity()
    return output.find('com.alibaba.android.user.login.SignUpWithPwdActivity') >= 0 and \
           output.find('com.alibaba.android.user.login.SignUpWithPwdActivity')


def isIncomingCall():
    output = get_current_activity()
    return output.find('com.huawei.remoteassistant.view.activity.ReceiveCallActivity') >= 0 and \
           output.find('.view.activity.ReceiveCallActivity') >= 0


def isScreenOff():
    output = subprocess.getoutput(adb + 'shell dumpsys power | grep "Display Power"')
    return output.find('state=OFF') >= 0


def isAtHome():
    output = get_current_activity()
    return output.find('com.huawei.android.launcher.unihome.UniHomeLauncher') >= 0 and \
           output.find('com.huawei.android.launcher/.unihome.UniHomeLauncher') >= 0


def click_power():
    subprocess.call(adb + 'shell input keyevent KEYCODE_POWER', shell=True)


def click_home():
    subprocess.call(adb + 'shell input keyevent KEYCODE_HOME', shell=True)


def click_remote_assistant():
    subprocess.call(adb + 'shell input tap 105 346', shell=True)


def click_answer_call():
    subprocess.call(adb + 'shell input tap 540 1400', shell=True)


def ding_login():
    subprocess.call(adb + 'shell input tap 167 563', shell=True)
    sleep(time_to_sleep)
    subprocess.call(adb + 'shell input text ea191213', shell=True)
    sleep(time_to_sleep)
    subprocess.call(adb + 'shell input keyevent KEYCODE_BACK', shell=True)
    sleep(time_to_sleep)
    subprocess.call(adb + 'shell input tap 350 690', shell=True)
    sleep(time_to_sleep)


def work():
    if isScreenOff():
        sub_logs = list(logs)[-60:]
        log = {'status': 'screenoff'}
        if len(sub_logs) < 60 or any({i['status'] != 'screenoff' for i in sub_logs}):
            logs.append(log)
            print(log)
            return 1
        log['action'] = 'click_power'
        print(log)
        click_power()
        log['action'] = 'click_home'
        click_home()
        print(log)
        logs.append(log)
        return 0

    elif isAtHome():
        sub_logs = list(logs)[-10:]
        log = {'status': 'at_home'}
        if len(sub_logs) < 10 or any({i['status'] != 'at_home' for i in sub_logs}):
            logs.append(log)
            print(log)
            return 1
        log['action'] = 'click_home'
        print(log)
        click_home()
        sleep(time_to_sleep)
        log['action'] = 'click_remote_assistant'
        print(log)
        click_remote_assistant()
        logs.append(log)
        return 0

    elif isIncomingCall():
        log = {'status': 'incoming_call', 'action': 'answer_call'}
        click_answer_call()
        logs.append(log)
        return 0

    elif isAtDingLogin():
        log = {'status': 'ding_login', 'action': 'input psw; return to cancel keyboard; click login;'}
        print(log)
        ding_login()
        logs.append(log)
        return 0

    log = {'status': 'undefined'}
    print(log)
    logs.append(log)
    return 0


if __name__ == '__main__':
    # print(isIncomingCall())
    while True:
        try:
            work()
        except:
            pass
        sleep(time_to_sleep)
