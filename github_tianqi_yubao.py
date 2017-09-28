#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    @Time    : 17-8-31 下午5:20
    @Author  : April
    @Site    : China
    @File    : tianqi_yubao.py
    @mail    : yzyawy@live.com
"""
import urllib2,time
import re
from twilio.rest import Client
import json
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

shishi_tianqi=""
shijians=""
yucetianqi=""
tianqi_dict={}
def get_tianqi_yubao(city):
    #获取城市的天气预报（api的问题，一次获取所有城市），但是我自己进行了处理，需要city参数
    try:
        host = "http://jisutqybmf.market.alicloudapi.com/weather/query"
        method = 'GET'
        appcode = '**************************'#你自己的appcode
        querys= 'city='
        query='&citycode=citycode&cityid=cityid&ip=ip&location=location'
        url = host + '?' + querys+city+query
        url=url.encode("utf8")
        request = urllib2.Request(url)
        request.add_header('Authorization', 'APPCODE ' + appcode)
        response = urllib2.urlopen(request)
        content = response.read()
        if (content):
            content = json.loads(content)
            for key, vaule in content.items():
                if key == u'result':
                    return vaule
    except Exception,e:
        print e
        pass

def get_quantian_tianqi():
    #详细的天气预报,适用于每天发送。
    global shishi_tianqi, shijians, tianqi_dict, yucetianqi
    try:
        citys = [{u"city1":"phone1"}]#注意，此时是要获取天气预报的城市和手机号，这是一个列表，列表中是字典
        for citys_xin in citys:
            for city_key, city_value in citys_xin.items():
                city_xin = get_tianqi_yubao(city_key)
                for k, v in city_xin.items():
                    if k == "week":
                        xinqi = v   #周几
                    if k == "templow":
                        zuidi_wendu = v #最低温度
                    if k == "temphigh":
                        zuigao_wendu = v    #最高温度
                    if k == "temp":
                        qinjun_qiwen = v    #平均气温
                    if k == "daily":  # 以天为单位的天气预报
                        dailt_list = []
                        for dayils in v:
                            for ks, vs in dayils.items():
                                dailt_list.append(vs)
                        jinwan_tianqi = dailt_list[2].values()[1]   #今晚天气
                        jinwan_qiwen = dailt_list[2].values()[0]    #今晚天气
                        mingtian_tianqi = dailt_list[10].values()[1]    #明天天气
                        mingtian_qiwen = dailt_list[10].values()[0] #明天气温
                    if k == "weather":
                        jintian_tianqi = v
                duanxin = city_key + ":" + xinqi + "," + "今天白天：" + jintian_tianqi + "。\n" + "最高温度：" + zuigao_wendu + "度，" \
                          + "最低温度：" + zuidi_wendu + "度，" + "平均气温：" + qinjun_qiwen + "度" + "。\n" + "今夜：" + \
                          jinwan_tianqi + "。平均气温：" + jinwan_qiwen + "度。\n" + "明天：" + mingtian_tianqi + \
                          "。平均温度：" + mingtian_qiwen + "度。" + "\n" + "——april"
                duanxin = str(duanxin)

                # 进行短信推送
                account_sid = "********************************"    #你的twilio的account_sid
                auth_token = "*******************************"  #你的twilio的auth_token
                client = Client(account_sid, auth_token)
                message = client.messages.create(to=city_value,  # 区号+你的手机号码
                                                 from_="*********",  # 你的 twilio 电话号码
                                                 body=duanxin)
                print "短信发送成功"
    except Exception,e:
        print "get_quantian_tianqi",e
        pass
def get_duanxin_neirong():
    #如果未来有雨，雪，雾，就进行短信推送。
    biaozhiwei=0
    global shishi_tianqi,shijians,tianqi_dict,yucetianqi
    now_time = time.strftime("%H:%M", time.localtime()) #获取现在的时间
    try:
        citys = [{u"city":"phone"},{u"city1":"phone1"}]
        for citys_xin in citys: #遍历列表
            for city_key,city_value in citys_xin.items():   #遍历列表中的字典
                city_xin=get_tianqi_yubao(city_key) #获取天气预报
                for k,v in city_xin.items():
                    if k=="hourly":#按小时
                        for i in v:
                            for ks,vs in i.items():
                                if ks=="time" :
                                    shijians=vs
                                if ks=="weather":
                                    shishi_tianqi=vs
                                    tianqi_dict[shijians]=shishi_tianqi
                items = tianqi_dict.items()
                items.sort()
                for k_t,v_t in items:#对当先时间之后的数据进行分析，看是否有雨，雪，雾
                    if k_t >= now_time:
                        vs=str(v_t)
                        yu=re.findall("(.*雨.*)|(.*雪.*)|(.*雾.*)",vs)
                        if len(yu)!=0:
                            biaozhiwei+=1#如果有雨，雪，雾，标志位+1
                            yucetianqi=yu[0][0]
                if biaozhiwei!=0:#判断标志位是否不为０
                    duanxin= "未来12小时，"+yucetianqi+"\n"+"——april"


                    # 进行短信推送
                    account_sid = "****************************"    #你的twilio的account_sid
                    auth_token = "****************************" #你的twilio的auth_token
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(to=city_value,  # 区号+你的手机号码
                                                     from_="*******",  # 你的 twilio 电话号码
                                                     body=duanxin)
                    print "短信发送成功"
                else:
                    print "今天天气不错！"
                    pass

    except Exception,e:
        print "get_duanxin_neirong",e
        pass
def timing_carried_out():       #定时启动
    while True:
        current_time = time.localtime(time.time())
        if ((current_time.tm_hour == 06) and (current_time.tm_min == 10) and (current_time.tm_sec == 0)):
            get_duanxin_neirong()#检测当前时间之后是否有雨雪雾
            get_quantian_tianqi()#每天发送天气预报信息
        if ((current_time.tm_hour == 18) and (current_time.tm_min == 10) and (current_time.tm_sec == 0)):
            get_duanxin_neirong()#检测当前时间之后是否有雨雪雾
        time.sleep(1)

if __name__=="__main__":
    timing_carried_out()