#!/usr/bin/python

import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import urllib
import urllib2
import traceback
import wx

#MACRO
RIGHT = '0'
ERROR = '1'
MAX_RETRY = 2

#FRAME
class Frame(wx.Frame):
    url_base="http://10.16.24.69/ces/api/aligd/v1/getresult?prepare_id=897414&key=A5E13AC7-8055-47D9-912D-39099BADB731&prepare_id="
    def __init__(self,parent=None,id=-1,pos=wx.DefaultPosition,title='Ali-Gaode O2O GUI'):
    #View
        #Positions and sizes
        pos_frm=pos            #Frame position
        sz_frm=(600,500)       #Frmae size
        sz_bt=(150,100)        #Button size
        sz_input=(300,300)     #Input text size
        sz_output=(300,150)    #Output text size
        pos_input=(50,20)      #Input text position
        pos_output=(50,330)    #Output text position
        pos_bt_get=(425,20)    #GetData btn position
        pos_bt_snd=(425,140)   #SendData btn position
        pos_bt_gtsd=(425,260)  #Get&Send btn position
        pos_bt_quit=(425,380)  #Quit btn position
        wx.Frame.__init__(self,parent,id,title,pos_frm,sz_frm,style=wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX))
        self.bt_get=wx.Button(self,label="Get Data From Worklist",pos=pos_bt_get,size=sz_bt)
        self.bt_snd=wx.Button(self,label="Send Data to Ali",pos=pos_bt_snd,size=sz_bt)
        self.bt_gtsd=wx.Button(self,label="Get & Send",pos=pos_bt_gtsd,size=sz_bt)
        self.bt_quit=wx.Button(self,label="Quit",pos=pos_bt_quit,size=sz_bt)
        self.txt_input=wx.TextCtrl(self,-1,"",size=sz_input,pos=pos_input,style=wx.TE_MULTILINE)
        self.txt_output=wx.StaticText(self,-1,"",size=sz_output,pos=pos_output)
        self.txt_output.SetBackgroundColour("Grey")
    #Control
        self.Bind(wx.EVT_BUTTON,self.OnClickGet,self.bt_get)
        self.Bind(wx.EVT_BUTTON,self.OnClickSnd,self.bt_snd)
        self.Bind(wx.EVT_BUTTON,self.OnClickGtsd,self.bt_gtsd)
        self.Bind(wx.EVT_BUTTON,self.OnClickQuit,self.bt_quit)
    #Model
    def OnClickGet(self,event):
        prepareIds=self.txt_input.GetValue().strip('\n').split('\n')
        #Generate the URL
        urlstr=''
        for prepId in prepareIds:
            tmpId=prepId.strip('\t').strip(' ')
            try:
                if isinstance(int(tmpId),int):
                    urlstr+='%d,'%int(tmpId)
                    self.txt_output.SetLabel('urlstr%s'%urlstr)               
            except:
                self.txt_output.SetLabel("Input data ERROR, please check")
                return
        urladdr=self.url_base+urlstr
        urladdr=urladdr[:-1]
        self.txt_output.SetLabel(urladdr)
        f_p=open('./data/pass_worklist_failed','a')
        f_un=open('./data/unprocess_worklist_failed','a')
        datas=""    
        code,datas=self.testGetUrlData(urladdr)
        datas=datas[17:-2]
        if code == ERROR:
            print "alio2o_resend:get url data ERROR"
            self.txt_output.SetLabel("Get URL data ERROR")
            return
        for c in range(len(datas)):
            if (datas[c]== ',') and (datas[c-1]=='}'):
                datas=datas[:c]+'\n'+datas[c+1:] 
        datas_list=datas.split('\n')
        for data in datas_list:
            print "Data 2 be dealt:"
            print data
            self.txt_output.SetLabel(data)
            #data = data[:-1]
            try:
                data_json=json.loads(data)
            except:
                print "ERROR when resolving json data\n"
                self.txt_output.SetLabel("Resolving Data ERROR")
            print data_json.get("process_status")
            status=int(data_json.get("process_status"))
            if status == 0:
                f_un.write(data+'\n')
            elif status == 1:
                f_p.write(data+'\n')
        f_un.close()
        f_p.close()
        self.txt_output.SetLabel("Get Data Success!")
    def OnClickSnd(self,event): 
        if self.txt_input.GetValue().strip('\n').strip('\t')=="":
            self.txt_output.SetLabel("Please input and get first.")
        elif 0!=os.system("python ProcessPassWorklist.py") or 0!= os.system("python ProcessUnprocessWorklist.py"):
            self.txt_output.SetLabel("Send Data Failed!")
        else:
            self.txt_output.SetLabel("Send Data Succeed!")    
    def OnClickGtsd(self,event):
        self.OnClickGet(event)
        self.OnClickSnd(event)
    def OnClickQuit(self,event):
        self.Close(True)
    def OnExit(self):
        print "Exit"

    def testGetUrlData(self,url,param = ""):
        code = ERROR
        content = ""
        count = 0
        while count < MAX_RETRY:
            try:
                if param != "":
                    connect = urllib2.urlopen(url,param)
                else:
                    connect = urllib2.urlopen(url)
                content = connect.read()
                connect.close()
                code = RIGHT
            except:
                print url
                sys.stdout.flush()
                traceback.print_exc()
                code = ERROR
            count+=1
            if code == RIGHT:
                break
        return code,content

#Application
class App(wx.App):
    def __init__(self,redirect=True,filename='./Ali-GaodeGUI.log'):
        wx.App.__init__(self,redirect,filename)
    def OnInit(self):
        if self.isWorkRun() == True:
            sys.exit(1)
        self.frame=Frame()
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True
    def isWorkRun(self):
        if os.path.exists("processPassWorklist_pid"):
            os.system("rm processPassWorklist_pid")
        if os.path.exists("processUnprocessWorklist_pid"):
            os.system("rm processUnprocessWorklist_pid")
        os.system('ps -ef | grep processPassWorklist.py > processPassWorklist_pid')
        os.system('ps -ef | grep processUnprocessWorklist.py > processUnprocessWorklist_pid')
        lines=[line for line in file('processPassWorklist_pid')]
        for line in lines:
            if line.find('python processPassWorklist.py')!=-1:
                return True
        lines=[line for line in file('processUnprocessWorklist_pid')]
        for line in lines:
            if line.find('python processUnprocessWorklist.py')!=-1:
                return True
        return False

if __name__=='__main__':
    app=App()
    app.MainLoop()

