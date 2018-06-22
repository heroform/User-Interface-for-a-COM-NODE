from jsonrpcserver import methods
import zmq
import random
import time
from jsonrpcserver.response import NotificationResponse
from jsonrpcserver.response import RequestResponse


# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("ipc:///home/taitd/var/run/rrh_pool/rrh1.sock")

id_ = 0
ueid = 0
imsiList = ['11111111111111111111111111111111',
            '10101010101010101010101010101010',
            '12341234123412341234123412341234',
            '68686868686868686868686868686868',
            '92929292929292929292929292929292',
            '57575757575757575757575757575757',
            '35772345656788965565683257665434',
            '25434546546675673544777777777896',
            '78878987545423423499999993434343',
            '98898344556679834323545567654545',
            '54567484213245712124875422128212',
            '48787875421272113287798653232444',
            '88888929929956563354165656899898',
            '98986653522212128787545109898247']
status = ["attached", "detached", "attaching"]
#
#
#
# @methods.add
# def statistics_updates(message):
#     # Variables
#     if (message == 'need log'):
#         ueid1 = random.randrange(1, 100)
#         ueid2 = random.randrange(1, 100)
#         ueid3 = random.randrange(1, 100)
#         ueid4 = random.randrange(1, 100)
#         ueid5 = random.randrange(1, 100)
#         ueid6 = random.randrange(1, 100)
#         imsi1 = imsiList[ueid1 % 14]
#         imsi2 = imsiList[ueid2 % 14]
#         imsi3 = imsiList[ueid3 % 14]
#         imsi4 = imsiList[ueid4 % 14]
#         imsi5 = imsiList[ueid5 % 14]
#         imsi6 = imsiList[ueid6 % 14]
#         sentStatus1 = status[ueid1 % 3]
#         sentStatus2 = status[ueid2 % 3]
#         sentStatus3 = status[ueid3 % 3]
#         sentStatus4 = status[ueid4 % 3]
#         sentStatus5 = status[ueid5 % 3]
#         sentStatus6 = status[ueid6 % 3]
#
#         text = "'" + str(id_) + "':{ueid:" + str(ueid1) + ", imsi:" + imsi1 + ", status:'" + sentStatus1 + \
#                "'}, {ueid:" + str(ueid2) + ", imsi:" + imsi2 + ", status:'" + sentStatus2 + \
#                "'}, {ueid:" + str(ueid3) + ", imsi:" + imsi3 + ", status:'" + sentStatus3 + \
#                "'}, {ueid:" + str(ueid4) + ", imsi:" + imsi4 + ", status:'" + sentStatus4 + \
#                "'}, {ueid:" + str(ueid5) + ", imsi:" + imsi5 + ", status:'" + sentStatus5 + \
#                "'}, {ueid:" + str(ueid6) + ", imsi:" + imsi6 + ", status:'" + sentStatus6 + \
#                "'}\n"
#
#         socket.send_string(text)
#
# @methods.add
# def config_update(message):
#     if (message == 'wrong ki'):
#         socket.send_string('change milenage ki')
#
#     if (message == 'need more RRH number'):
#         socket.send_string('increase RRH number')
#
# def main():
#     while True:
#         request = socket.recv()
#         statistics_updates(request)
#         config_update(request)
#         time.sleep(1)
#
# if __name__ == '__main__':
#     main()

socket = zmq.Context().socket(zmq.REP)

@methods.add
def ping():
    return 'pong'

@methods.add
def statistics_updates():
    # Variables
    ueid1 = random.randrange(1, 100)
    ueid2 = random.randrange(1, 100)
    ueid3 = random.randrange(1, 100)
    ueid4 = random.randrange(1, 100)
    ueid5 = random.randrange(1, 100)
    ueid6 = random.randrange(1, 100)
    imsi1 = imsiList[ueid1 % 14]
    imsi2 = imsiList[ueid2 % 14]
    imsi3 = imsiList[ueid3 % 14]
    imsi4 = imsiList[ueid4 % 14]
    imsi5 = imsiList[ueid5 % 14]
    imsi6 = imsiList[ueid6 % 14]
    sentStatus1 = status[ueid1 % 3]
    sentStatus2 = status[ueid2 % 3]
    sentStatus3 = status[ueid3 % 3]
    sentStatus4 = status[ueid4 % 3]
    sentStatus5 = status[ueid5 % 3]
    sentStatus6 = status[ueid6 % 3]

    text = "{ueid:" + str(ueid1) + ", imsi:" + imsi1 + ", status:'" + sentStatus1 + \
           "'}, {ueid:" + str(ueid2) + ", imsi:" + imsi2 + ", status:'" + sentStatus2 + \
           "'}, {ueid:" + str(ueid3) + ", imsi:" + imsi3 + ", status:'" + sentStatus3 + \
           "'}, {ueid:" + str(ueid4) + ", imsi:" + imsi4 + ", status:'" + sentStatus4 + \
           "'}, {ueid:" + str(ueid5) + ", imsi:" + imsi5 + ", status:'" + sentStatus5 + \
           "'}, {ueid:" + str(ueid6) + ", imsi:" + imsi6 + ", status:'" + sentStatus6 + \
           "'}"

    return text

@methods.add
def statistics_updates_reduce():
    ueid1 = random.randrange(1, 100)
    ueid2 = random.randrange(1, 100)
    ueid3 = random.randrange(1, 100)

    imsi1 = imsiList[ueid1 % 14]
    imsi2 = imsiList[ueid2 % 14]
    imsi3 = imsiList[ueid3 % 14]

    sentStatus1 = status[ueid1 % 3]
    sentStatus2 = status[ueid2 % 3]
    sentStatus3 = status[ueid3 % 3]

    text = "{ueid:" + str(ueid1) + ", imsi:" + imsi1 + ", status:'" + sentStatus1 + \
           "'}, {ueid:" + str(ueid2) + ", imsi:" + imsi2 + ", status:'" + sentStatus2 + \
           "'}, {ueid:" + str(ueid3) + ", imsi:" + imsi3 + ", status:'" + sentStatus3 + \
           "'}"

    return text
        # def config_update():
#     a =

if __name__ == '__main__':
    socket.bind("ipc:///home/taitd/var/run/rrh_pool/rrh2.sock")
    while True:
        request = socket.recv().decode()
        response = methods.dispatch(request)
        socket.send_string(str(response))