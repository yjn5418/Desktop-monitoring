import numpy as np
import socket as sk
import os,re,time,threading,cv2

from PIL import ImageGrab
from socket import *
from psutil import virtual_memory,net_io_counters

###pyinstaller --clean --win-private-assemblies -F -i nwe.ico host_.py

def win_api():       
    try:       
        api =  os.popen('wmic desktopmonitor get screenheight, screenwidth').read()
        hei,wh = re.findall(r'(\d+)',api)
        # print('hei:',hei,'wh:',wh)
        if hei=='' or wh =='':
            return 1920,1080
        return int(hei),int(wh)
    except Exception as e:
        print('问题：api获取\n')
        print(e)

def win_iofo():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        addr = (ser_ip,4439)
        ds = net_io_counters(pernic=True)['以太网'][:2]
        dx = net_io_counters(pernic=True)['WLAN'][:2]
        # print('yitainet:',ds)
        # print('WLAN:',dx)
        while zl_yn:
            try:
                mem = virtual_memory()
                zj = mem.total /1048576 #总
                ysy = mem.used /1048576 #使用
                kx = mem.free /1048576 #空闲

                send_,recv_ = ds[0],ds[1]
                send_dx,recv_dx= dx[0],dx[1]

                ds = net_io_counters(pernic=True)['以太网'][:2]
                dx = net_io_counters(pernic=True)['WLAN'][:2]
                
                send__,recv__ = ds[0]-send_,ds[1]-recv_
                send__dx,recv__dx = dx[0]-send_dx,dx[1]-recv_dx
                data = str(int(zj))+'-'+str(int(ysy))+'-'+str(int(kx))+'-'+str(send__)+'-'+str(recv__)+'-'+str(send__dx)+'-'+str(recv__dx)

                send_data = data.encode('utf-8')
                s.sendto(send_data, addr)
                time.sleep(1)
            except Exception as e:
                print('问题：信息(2)信息')
                print(e)
    except Exception as e:
        print('问题：信息(1)发送\n')
        print(e)

def win_img():
    try:
        def send_img():
            try:
                s.send(send_data)
                # print('发送成功 size: %d kb'%(len(send_data)))
            except:
                print('发送失败 size: %d kb'%(len(send_data)))

        addr = (ser_ip, 4444)    #发送地址q
        hei,wh =  win_api()
        BOX=(0,0,wh,hei)
        s = socket(AF_INET, SOCK_STREAM)#使用的是ipv4 和 udp协议
        s.connect(addr)
        while zl_yn:
            img=np.array(ImageGrab.grab(bbox=BOX))
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) #纠正色彩问题
            img = cv2.resize(img,(hei,wh),interpolation=cv2.INTER_CUBIC)
            time.sleep(0.01)
            th = threading.Thread(target=send_img)#在send_img函数里创建一个线程
            th.setDaemon(True)#设置为守护线程
            
            _, send_data = cv2.imencode('.jpg', img,[cv2.IMWRITE_JPEG_QUALITY,50])#将图片转换为二进制数据
            th.start()#开启线程
        s.close()
        print('已关闭桌面连接')
        return False
    except Exception as e:
        print('问题：桌面发送\n')
        print(e)

def client():
    try:
        def send_img():
            
            s.send(send_data)

        cap = cv2.VideoCapture(0)
        addr = (ser_ip, 4443)              #发送地址
        s = socket(AF_INET, SOCK_STREAM)#使用的是ipv4 和 udp协议
        s.connect(addr)
        while zl_yn:
            _, img = cap.read()
            img = cv2.flip(img,1)
            th = threading.Thread(target=send_img)#在send_img函数里创建一个线程
            th.setDaemon(True)#设置为守护线程
            _, send_data = cv2.imencode('.jpg', img,[cv2.IMWRITE_JPEG_QUALITY,50])#将图片转换为二进制数据
            th.start()#开启线程
        s.close()
        print('已关闭视频连接')
        cap.release()
        return False
    except Exception as e:
        print('问题：摄像头发送\n')
        print(e)

def zhiling(zl_id):
    try:
        zl_book = [win_img,'桌面监控',client,'摄像头监控']
        try:
            threading.Thread(target=zl_book[zl_id]).start()
            print('已连接'+zl_book[zl_id+1])
            threading.Thread(target=win_iofo).start()
        except:
            print('连接失败')
    except Exception as e:
        print('问题：指令转换\n')
        print(e)

def ser():
    try:
        s = socket(AF_INET,SOCK_DGRAM)
        addr = (local_ip, 4440)               #接受地址
        s.bind(addr)
        print('正在运行......')
        while True:
            data = s.recv(1024).decode('utf-8')
            # print('recv:',data,'\n')
            global zl_yn
            if data == 'q':
                zl_yn = False
                break
            elif data == 's':
                zl_yn = False
            elif len(data) == 1:
                zl_yn = False
                time.sleep(1)
                zl_yn = True
                zhiling(int(data))
        print('已关闭程序')
        input('\n\n按任意键退出......')
    except Exception as e:
        print('问题：接受指令\n')
        print(e)

if __name__ == '__main__':
    hostname = sk.gethostname()
    local_ip = sk.gethostbyname(hostname)
    print('local ip: %s'%local_ip)
    ser_ip = input('service ip: ')
    zl_yn = True
    ser()
