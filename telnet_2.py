import threading,os,re
import numpy as np

from cv2 import imdecode,cvtColor,COLOR_BGR2RGB
from socket import *
from tkinter import *
from PIL import Image as im, ImageTk
from tkinter.messagebox import *



#pyinstaller --clean --win-private-assemblies -Fw -i ser.ico telnet_.py 打包方式
'''
路径不能有中文名，这里是为了交作业
'''

def gui():#GUI1 主窗口
    def quits():#退出
        if askyesno('提示','确定退出吗？(这并不是关闭host机器)'):
            send_host('s')
            os._exit(0) and root.quit()
    
    def san_ip_gui():#GUI2 扫描ip占用
        def _arp():#使用arp获取地址
            ip_online = []
            ip = gethostbyname(gethostname())
            i = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.(\d{1,3})',ip)[0]
            ip_online.append(i)
            ans = os.popen('arp -a').read()
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',ans)[1:] #ip地址匹配
            
            for i in ips:
                if '224' in i or '255' in i:#限制为本地ip
                    break
                else:
                    i = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.(\d{1,3})',i)[0]#ip最后一位匹配
                    ip_online.append(i)
            return ip_online #ip最后 总列表

        def ping(start,ends): #ping ip测试
            ip = gethostbyname(gethostname())
            i = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}',ip)[0]
            for host_end in range(start,ends+1):
                if host_end < 255:
                    ip = i+str(host_end)
                    ans = os.popen('ping -c 1 -n 1  %s'%ip).read()
        
        def ping_threa(): #ping线程
            if askyesno('警告！！！','10秒内不要在ping！！'):
                ith = []
                for i in range(50):
                    ih,ie = (i*5)+1,(i+1)*5+1
                    ith.append(threading.Thread(target=ping,args=(ih,ie)))
                ith.append(threading.Thread(target=ping,args=(251,255)))
                for th in ith:
                    th.start()
                tishi.insert(END,'等待10s')

        def b_bre():#GUI ip按钮排版
            global b_list
            b_row = 0
            b_col = 0
            
            ip_online = _arp()#获取ip尾数列表
            # print('ip list:',ip_online)
            for _ in range(1,255):
                b_col += 1
                if str(_) in ip_online:
                    b_bg = 'MediumSpringGreen'
                    b_list['%d'%_] = (Button(root1,text=_,width=5,bg=b_bg,command=lambda _=_ :b_chios(b_list['%d'%_])))#在lambda后 冻结_ 不在回调_
                    b_list['%d'%_].grid(row=b_row,column=b_col)
                else:
                    b_bg = 'Silver'
                    b_list['%d'%_] = (Button(root1,text=_,width=5,bg=b_bg))
                    b_list['%d'%_].grid(row=b_row,column=b_col)
                if b_col == 16:
                    b_col = 0
                    b_row +=1

        def b_del():#刷新按钮 删除按钮再从排      不要一直使用，妈的卡死
            global b_list
            b_list = {}
            b_bre()

        def b_chios(text):#GUI4 选择窗口
            def on_closing():#销毁窗口
                global root1
                root3.destroy()
                root1.destroy()

            def en_get():#返回框框的方法
                global ip_read
                ip = gethostbyname(gethostname())
                i = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}',ip)[0]
                iP = i+str(text)[8:]
                ip_read.set(iP)
            root3 = Tk()
            root3.title("选择")
            root3.geometry("250x125+800+500")
            root3.resizable(False,False)
            Label(root3).grid(row=0,column=0,columnspan=2)
            Label(root3,width=5).grid(row=1,column=0,rowspan=2)
            Button(root3,text='GET  到  IP  框',width=20,command=lambda:[en_get(),on_closing()]).grid(row=1,column=1,ipadx=10,ipady=2)
            Button(root3,text='扫  描  端  口',width=20,command=lambda:[b_port(text),on_closing()]).grid(row=2,column=1,ipadx=10,ipady=2)
        
            root3.mainloop()
        
        def b_port(ipend):#GUI3 端口界面
            ip = gethostbyname(gethostname())
            i = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.)\d{1,3}',ip)[0]
            ip = i+str(ipend)[8:]
            timeout = 0.00001

            def chios(ids):#选择扫描
                if ids == 1:
                    port_list = [i for i in range(1,1024)]
                elif ids == 2:
                    port_list = [i for i in range(1024,49152)]
                elif ids == 3 :
                    port_list = [i for i in range(49152,65536)]
                else:
                    return
                thread_port(port_list=port_list,_=ids) 

            def port_scan(portran,_):#扫描端口
                lb_s = [lb1,lb3,lb5]
                for port in portran:
                    try:
                        s = socket(AF_INET,SOCK_STREAM)
                        s.settimeout(timeout)
                        result_code = s.connect_ex((ip, port)) #开放放回0
                        if result_code == 0:
                            po_ok = '     port: %6d  [open]' % port
                            lb_s[_-1].insert(END,po_ok)
                    except Exception as e:
                        # print(port, ':' ,e)
                        return

            def thread_port(port_list,_):
                zong_num = len(port_list)
                pin_jun_num = 200    # 每条线程分配数量
                thead_list = []
                for i in range(zong_num//pin_jun_num):
                    port_this = port_list[-200:]
                    port_list = port_list[:-200]
                    thead_list.append(threading.Thread(target=port_scan,args=(port_this,_)))
                thead_list.append(threading.Thread(target=port_scan,args=(port_list,_)))
                for th in thead_list:
                    th.start()

            global root2
            root2 = Tk()
            root2.title("port_scan---------"+ip)
            root2.geometry("720x470")
            root2.resizable(False,False)

            #标签组
            for i in range(20):
                Label(root2,text='|').grid(row=i,column=1)
                Label(root2,text='|').grid(row=i,column=3)

            #按钮组
            Button(root2,text='知名端口 1---1023 快',width=30,command=lambda:chios(1)).grid(row=0,column=0)
            Button(root2,text='用户端口 1024---49151 慢',width=30,command=lambda:chios(2)).grid(row=0,column=2)
            Button(root2,text='公共端口 49152---65535 中',width=30,command=lambda:chios(3)).grid(row=0,column=4)

            #listbox背景组
            lb0 = Listbox(root2,width=30,height=24)
            lb0.grid(row=1,column=0,rowspan=19)

            lb2 = Listbox(root2,width=30,height=24)
            lb2.grid(row=1,column=2,rowspan=19)

            lb4 = Listbox(root2,width=30,height=24)
            lb4.grid(row=1,column=4,rowspan=19)
            
            #Scrollbar滚动组
            sc = Scrollbar(lb0)
            sc.pack(side=RIGHT, fill=Y)

            sc1 = Scrollbar(lb2)
            sc1.pack(side=RIGHT, fill=Y)

            sc2 = Scrollbar(lb4)
            sc2.pack(side=RIGHT, fill=Y)

            #容器组 (已有滚轮占用)
            lb0_s = StringVar()
            lb0_s.set('等待点击获取.....')

            lb2_s = StringVar()
            lb2_s.set('等待点击获取.....')

            lb4_s = StringVar()
            lb4_s.set('等待点击获取.....')

            #listbox前景组
            lb1 = Listbox(lb0, yscrollcommand=sc.set,width=30,height=24)
            lb1.pack(side=LEFT, fill=BOTH, expand=True)

            lb3 = Listbox(lb2, yscrollcommand=sc1.set,width=30,height=24)
            lb3.pack(side=LEFT, fill=BOTH, expand=True)

            lb5 = Listbox(lb4, yscrollcommand=sc2.set,width=30,height=24)
            lb5.pack(side=LEFT, fill=BOTH, expand=True)

            # 滚动条动，列表跟着动
            sc.config(command=lb1.yview)
            sc1.config(command=lb3.yview)
            sc2.config(command=lb5.yview)


            root2.mainloop()

        global b_list,root1
        b_list = {}
        root1 = Tk()
        root1.title("ip_scan")
        root1.geometry("720x480")
        root1.resizable(False,False)
        b_bre()
        b_ping = Button(root1,text='ping',width=5,bg='red',command=lambda:ping_threa())
        b_ping.grid(row=15,column=15)
        b_break = Button(root1,text='刷新',width=5,bg='MediumSpringGreen',command=lambda:b_del())
        b_break.grid(row=15,column=16)
        root1.mainloop()

    def hos_info():#获取host主机信息
        ip = gethostbyname(gethostname())
        s = s = socket(AF_INET, SOCK_DGRAM)
        addr = (ip, 4439)               #接受地址
        s.bind(addr)
        global sys_read,net_read
        while th_run:
            cl_info = s.recv(1024).decode('utf-8')
            cl_info = cl_info.split('-',6)
            zg = "总量ROM %d MB"%int(cl_info[0])
            us = "使用ROM %d MB"%int(cl_info[1])
            fr = "空闲ROM %d MB"%int(cl_info[2])
            perc = 'ROM使用量百分比 %2.2f  '%(int(cl_info[1])/int(cl_info[0])*100)+'%'

            if int(cl_info[3]) >= 1024:
                send_net = '以太网上传： %2.2f MB'%(int(cl_info[3])/1048576)
            elif int(cl_info[3]) == 0:
                send_net = ''
            else:
                send_net = '以太网上传： %4.2f KB'%(int(cl_info[3])/1024)

            if int(cl_info[4]) >= 1024:
                down_net = '以太网下载： %2.2f MB'%(int(cl_info[4])/1048576)
            elif int(cl_info[4]) == 0 :
                down_net = ''
            else:
                down_net = '以太网下载： %4.2f KB'%(int(cl_info[4])/1024)

            if int(cl_info[5]) >= 1024:
                send_net_w = 'WLAN上传： %2.2f MB'%(int(cl_info[5])/1048576)
            elif int(cl_info[5]) == 0:
                send_net_w = ''
            else:
                send_net_w = 'WLAN上传： %4.2f KB'%(int(cl_info[5])/1024)
                

            if int(cl_info[6]) >= 1024:
                down_net_w = 'WLAN下载： %2.2f MB'%(int(cl_info[6])/1048576)
            elif int(cl_info[6]) == 0:
                down_net_w = ''
            else:
                down_net_w = 'WLAN下载： %4.2f KB'%(int(cl_info[6])/1024)
                
            sys_read.set((zg,us,fr,perc))
            net_read.set((send_net,down_net,send_net_w,down_net_w))

    def server():#接受host主机传来的图片
        def th_ser(cns,cns2):
            global port_read,Big_LA,Bi_cou,root4
            try:
                img = np.frombuffer(data, dtype=np.uint8)
                img = imdecode(img,1)#二进制--》ndarray--》图片
                img = im.fromarray(cvtColor(img,COLOR_BGR2RGB))#将图片转换为Image对象
                if Bi_cou:
                    # img = img.resize((1344,756), im.ANTIALIAS)
                    img = img.resize((1728,972), im.ANTIALIAS)
                    img = ImageTk.PhotoImage(img)
                    Big_LA.config(image=img,width=1728,height=972)
                    Big_LA.image = img
                else:
                    img = img.resize((860,648), im.ANTIALIAS)
                    img = ImageTk.PhotoImage(img)
                    imgge_label.config(image=img,width=860,height=648)#刷新label内容
                    imgge_label.image = img
            except Exception as e:
                pass

        global port_read,Big_LA,Bi_cou,root4
        ip = gethostbyname(gethostname())
        port = port_read.get()
        s = socket(AF_INET, SOCK_STREAM)
        addr = (ip, int(port))               #接受地址
        s.bind(addr)
        s.listen(1)
        skl,_ = s.accept()
        th_num_ser = 0
        hunxi_num = 0
        Th_list = []
        for i in range(5):
            Th_list.append(threading.Thread(target=th_ser,args=(hunxi_num,hunxi_num+1)))
            hunxi_num += 1
        while th_run:
            data = skl.recv(300000)
            Th_list[th_num_ser].start()
            th_num_ser += 1
            if th_num_ser == 4:
                Th_list=[]
                for i in range(5):
                    Th_list.append(threading.Thread(target=th_ser,args=(hunxi_num,hunxi_num+1)))
                    hunxi_num += 1
                th_num_ser = 0
        s.close()
        if not th_run:
            rea_img('bg2.jpg')
           
    def send_id():#切换监控方法
        global ti_read,zl_id,port_read
        if zl_id == '0':
            zl_id = '2'
            port_read.set('4443')
            ti_read.set('摄像监控模式')
        else:
            zl_id = '0'
            port_read.set('4444')
            ti_read.set('桌面监控模式')
        
    def send_host(zl='q'):#发送指令方法
        global zl_id,ip_read,ti_read
        ip = ip_read.get()
        if ip == '':
            ti_read.set('无ip内容')
            return
        addr = (ip, 4440)  
        s = socket(AF_INET, SOCK_DGRAM)#使用的是ipv4 和 udp协议
        if zl == 'qq':
            if askyesno('提示','确定关闭host机器吗？'):
                send_data = 'q'.encode('utf-8')
            else:
                return
            try:
                s.sendto(send_data, addr)
                s.close()
            except:
                tishi.insert(END, '出错')
                s.close()
            tishi.insert(END, '对方已断开连接')
            return
        elif zl == 's':
            # print('停止监控')
            send_data = zl.encode('utf-8')
            try:
                s.sendto(send_data, addr)
                s.close()
            except:
                s.close()
                tishi.insert(END, '出错')
            return
        elif zl == 'q':
            return
        send_data = zl_id.encode('utf-8')
        try:
            s.sendto(send_data, addr)
            s.close()
        except:
            s.close()
            tishi.insert(END, '出错')

    def two_theah():#加入线程池
        theads = []
        theads.append(threading.Thread(target=server))
        theads.append(threading.Thread(target=hos_info))
        return theads
        
    def video_main():#启用线程
        send_host('1')
        global th_run
        th_run = True
        rea_img('R-C.gif')
        theads = two_theah()
        for th in theads:
            th.start()

    def rea_img(im_name='bg2.jpg'):#加载图片
        img = im.open('./'+im_name)
        img = img.resize((int(860), int(648)), im.ANTIALIAS)

        img = ImageTk.PhotoImage(img)
        imgge_label.config(text='暂无画面',image=img,width=860,height=648)#刷新label内容
        imgge_label.image = img
    
    def th_quit():#停止画面
        send_host(zl='s')
        rea_img('bg2.jpg')
        global th_run
        th_run = False

    def big_screen():
        def bi_qu():
            if askyesno('提示','确定关闭全屏吗？'):
                global Bi_cou
                Bi_cou =False
                root4.destroy()
        global Big_LA,root4,Bi_cou
        root4 = Toplevel()
        root4.title('全屏')
        root4.geometry("1728x972+96+27")
        root4.resizable(False,False)
        root4.protocol("WM_DELETE_WINDOW",lambda: bi_qu())
        root4.attributes("-topmost",True)
        
        
        Big_LA = Label(root4,bg='white',width=246,height=57,text='暂无画面')
        Big_LA.grid(row=0,column=0)
        Bi_cou = True
        root4.mainloop()

    local_ip = gethostbyname(gethostname())
    if local_ip == None:
        local_ip == '未连接到ipv4'
    root = Tk()
    root.title("Telnet-----"+local_ip)
    root.geometry("1200x800")
    root.resizable(False,False)
    root.protocol("WM_DELETE_WINDOW",root.quit())

    #各种判断变量
    global th_run,zl_id,Bi_cou
    zl_id = '0'
    Bi_cou = False
    #容器区域
    global port_read,ti_read,ip_read,sys_read,net_read
    sys_read = StringVar()
    net_read = StringVar()
    ti_read = StringVar()
    ip_read = StringVar()
    port_read = StringVar()
    port_read.set(4444)
    runhoust_read = '跑马灯：testtesttesttesttesttesttesttesttesttesttesttesttestt\
esttesttesttesttesttesttesttesttesttesttesttesttesttesttesttestesttesttesttesttest\
ttesttesttesttesttesttesttesttesttesttesttesttesttesttesttesttest'

    #监控画布
    imgge_label = Label(root,text="hello",bg='white',width=122,height=38)
    imgge_label.grid(row=0,rowspan=20,column=0,columnspan=15)

    #初始化画面
    rea_img()

    #标签区域+
    Label(root,text='系统监控:').grid(row=0,column=15)
    Label(root,text='网络监控:').grid(row=10,column=15)
    Label(root,text='提示：').grid(row=20,column=15)
    Label(root,text='ip:').grid(row=20,column=0,ipadx=0)
    Label(root,text='port:').grid(row=20,column=2,ipadx=0)
    Label(root,text=runhoust_read).grid(row=30,column=0,columnspan=25)

    #提示框区域-
    sys_ti = Listbox(root,height=15,width=35,listvariable=sys_read)
    sys_ti.grid(row=0,column=16,rowspan=10)
    net_ti =Listbox(root,height=15,width=35,listvariable=net_read)
    net_ti.grid(row=10,column=16,rowspan=10)
    tishi = Listbox(root,height=5,width=35,listvariable=ti_read)
    tishi.grid(row=20,column=16,rowspan=10)

    #文本框区域
    Entry(root,width=15,textvariable=ip_read).grid(row=20,column=1,ipadx=0)
    Entry(root,width=5,state='readonly',textvariable=port_read).grid(row=20,column=3,ipadx=0)

    #按钮区域
    Button(root,text='切换监控',bg='Silver',command=lambda:send_id()).grid(row=20,column=4,ipadx=0)
    start = Button(root,text="开始监控",command=lambda:video_main(),bg='Silver')
    start.grid(row=20,column=5)
    ends = Button(root,text="停止监控",command=lambda:th_quit(),bg='MediumSpringGreen')
    ends.grid(row=20,column=6)
    po_can = Button(root,text='ip scan',bg='Silver',width=20,command=lambda:san_ip_gui())
    po_can.grid(row=21,column=0,columnspan=2)
    mouse_kteboard = Button(root,text='鼠键控制',bg='Silver')
    mouse_kteboard.grid(row=20,column=12)
    big_cont = Button(root,text="大屏显示",bg='Gold',command=lambda:big_screen())
    big_cont.grid(row=20,column=13)
    end_host = Button(root,text='关闭host',bg='Silver',command=lambda:send_host('qq'))
    end_host.grid(row=20,column=14)
    quit_cont = Button(root,text="退出",command=lambda:quits(),bg='red')
    quit_cont.grid(row=20,column=15)

    root.mainloop()

if __name__=='__main__':
    gui()
