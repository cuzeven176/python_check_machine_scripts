#!/usr/bin/env python
#-*- coding: utf8 -*-
import os
import smtplib
import urllib,urllib2,cookielib
from pyzabbix import ZabbixAPI
from email import encoders
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
from datetime import datetime,date
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# rule = json.load(file('D:\pycharm\project\REGION Manage Script\qn_rolerule.json'))
def login():
	zapi= ZabbixAPI("http://localhost/zabbix")  #zabbix url 
	zapi.login("Admin","zabbix")
	return zapi

def color(stat): 
	# Define HTML file colors         
	if 'UP' not in stat:
		return 'red'
	else:
		return 'white'

def mail(recv, sub, body ):
	'''
	send report email to the relevant personnel
	:return:
	'''
	def _format_addr(s):
		name, addr = parseaddr(s)
		return formataddr((Header(name, 'utf-8').encode(), addr))
	# stmp server email address and password 
	from_addr = '********'  
	password = '*******'

	to_addr = ["123@163.com"]
	## email address accepted

	smtp_server = 'smtp.163.com'
	subject = sub
	content = body

	msg = MIMEMultipart('related')
	msg['From'] = _format_addr('YBY_Admin <%s>' % from_addr)
	msg['To'] = _format_addr('YBY_User <%s>' % to_addr)
	msg['Subject'] = Header(subject, 'utf-8').encode()

	mText=MIMEText(content,'html','utf-8')
	msg.attach(mText)


	for p in ['nginx01','nginx02','mysql-innodb','mongodb','zookeeper','hbase','yarn','io','disk_usage_','disk_usage_export','disk_usage_export_haoop01','disk_usage_export_haoop02','disk_usage_export_haoop03']:
		mImage=""
		pf = p + '.png'
		with open(pf, 'rb') as f:
			mImage = MIMEImage(f.read())
			mImage.add_header('Content-Id',p)
			msg.attach(mImage)

	server = smtplib.SMTP_SSL(smtp_server, 465)
	server.set_debuglevel(0)
	server.login(from_addr, password)
	server.sendmail(from_addr, to_addr, msg.as_string())
	server.quit()


def get_item_value(host):
	mem_total = zapi.item.get(output=["itemid", "lastvalue"], host=host, search={"key_": "vm.memory.size[total]"})[0]['lastvalue']
	mem_available = zapi.item.get(output=["itemid", "lastvalue"], host=host, search={"key_": "vm.memory.size[available]"})[0]['lastvalue']
	cpu_load = zapi.item.get(output=["itemid", "name", "lastvalue"], host=host, search={ "key_": "system.cpu.load[percpu,avg5]"})[0]["lastvalue"]
	cpu_idle = zapi.item.get(output=["itemid", "name", "lastvalue"], host=host, search={ "key_": "system.cpu.util[,idle]"})[0]["lastvalue"]
	tcp_etab = zapi.item.get(output=["itemid", "name", "lastvalue"], host=host, search={ "key_": "linux_status[tcp_status,ESTAB]"})[0]['lastvalue']

	mem_usage = (1 - float(mem_available)/float(mem_total)) * 100
        return (mem_usage, cpu_load, cpu_idle, tcp_etab)


def get_problem():
	today = date.today()
	stamp = int(time.mktime(time.strptime(str(today), "%Y-%m-%d")))
	items = zapi.problem.get(output=["name"], time_from=stamp, recent="true")
	problem_list = []
	if len(items) > 0:
		for i in items:
#        	ddprint i
			problem_list.append(i["name"])
	return problem_list

def get_status(url):
	resp = urllib2.urlopen(url)
	return json.loads(resp.read())["status"]
  
def get_service_status():
	newservices = {}
	with open('./web.txt', 'r') as ff:
		svc_list = ff.readlines()
	for s in svc_list:
		server = s.split()
                print(server)
                name = server[0]
                instance_list = server[1:]
                for instance in instance_list:
		   try:
			status = get_status("http://%s/actuator/health" % instance)
		   except urllib2.HTTPError:
			status = "NotFound"
		   except KeyError:
			status = "NotSupport"
		   if name in newservices.keys():
				newservices[name].append(instance + ' - '+ status)
		   else:
			newservices[name] = [ instance + ' - '+ status ]
			print(newservices)
	return newservices



def download_pic():
	url = "http://localhost/zabbix/index.php"
	info = {"name": "Admin", "password": "zabbix", "autologin": 1, "enter": "Sign in"}
	cookie = cookielib.CookieJar()
	myopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	urllib2.install_opener(myopener)
	data = urllib.urlencode(info)
	#print data
	req = urllib2.Request(url, data)
	response = myopener.open(req)
	#print cookie
	#print response
	pics_list = [ { "name": "nginx01",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B37627%5D=37627&itemids%5B37626%5D=37626&itemids%5B37625%5D=37625&itemids%5B37624%5D=37624&itemids%5B37623%5D=37623&itemids%5B37622%5D=37622&itemids%5B37621%5D=37621&itemids%5B37620%5D=37620&itemids%5B37619%5D=37619&itemids%5B37617%5D=37617&itemids%5B37618%5D=37618&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urlbrjr3&screenid='
		   },
		  { "name": "nginx02",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B37707%5D=37707&itemids%5B37706%5D=37706&itemids%5B37705%5D=37705&itemids%5B37704%5D=37704&itemids%5B37703%5D=37703&itemids%5B37702%5D=37702&itemids%5B37701%5D=37701&itemids%5B37700%5D=37700&itemids%5B37699%5D=37699&itemids%5B37697%5D=37697&itemids%5B37698%5D=37698&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urlgboko&screenid='
		   },
		  { "name": "mysql-innodb",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B36717%5D=36717&itemids%5B36976%5D=36976&itemids%5B37235%5D=37235&itemids%5B37494%5D=37494&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urljier1'
		   },
		  { "name": "mongodb",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B35980%5D=35980&itemids%5B36153%5D=36153&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urll775t'
		   },
		  { "name": "zookeeper",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B41216%5D=41216&itemids%5B40979%5D=40979&itemids%5B40962%5D=40962&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urllcqjg'
		   },
		  { "name": "hbase",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B41458%5D=41458&itemids%5B41457%5D=41457&itemids%5B41453%5D=41453&itemids%5B41445%5D=41445&itemids%5B41456%5D=41456&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urllkb9l'
		   },
		  { "name": "yarn",
		   "url": 'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B41048%5D=41048&itemids%5B41049%5D=41049&itemids%5B41050%5D=41050&itemids%5B41051%5D=41051&itemids%5B41047%5D=41047&itemids%5B41052%5D=41052&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1094&height=200&_=urllo41t'
		   },
		  { "name": "io",
			"url":'http://localhost/zabbix/chart.php?from=now-12h&to=now&itemids%5B38450%5D=38450&itemids%5B38632%5D=38632&itemids%5B37944%5D=37944&itemids%5B38223%5D=38223&itemids%5B37889%5D=37889&itemids%5B38712%5D=38712&type=0&profileIdx=web.item.graph.filter&profileIdx2=0&batch=1&width=1082&height=200&_=uwo1khgh'
		   },
		  { "name":"disk_usage_",
			"url":"http://localhost/zabbix/chart6.php?graphid=2380&screenid=36&graph3d=1&width=400&height=200&legend=1&profileIdx=web.screens.filter&profileIdx2=36&from=now-1h&to=now&_=usx0ossn"
		   },
		  {"name":"disk_usage_export",
			"url":"http://localhost/zabbix/chart6.php?graphid=2382&screenid=36&graph3d=1&width=400&height=200&legend=1&profileIdx=web.screens.filter&profileIdx2=36&from=now-1h&to=now&_=usx0sng0"
		  },
		  {"name": "disk_usage_export_haoop01",
			"url": "http://localhost/zabbix/chart6.php?graphid=2383&screenid=36&graph3d=1&width=400&height=200&legend=1&profileIdx=web.screens.filter&profileIdx2=36&from=now-1h&to=now&_=usx0v13e"
		   },
		  {"name": "disk_usage_export_haoop02",
		    "url": "http://localhost/zabbix/chart6.php?graphid=2384&screenid=36&graph3d=1&width=400&height=200&legend=1&profileIdx=web.screens.filter&profileIdx2=36&from=now-1h&to=now&_=usx14qwb"
		   },
		   {"name":"disk_usage_export_haoop03",
			  "url":"http://localhost/zabbix/chart6.php?graphid=2385&screenid=36&graph3d=1&width=400&height=200&legend=1&profileIdx=web.screens.filter&profileIdx2=36&from=now-1h&to=now&_=usx1mrwb"
			}

		 ]
	# 抓取zabbix生成的状态图，并保存


	for pic in pics_list:
		pic_temp = ""
		pic_temp = urllib2.urlopen(pic["url"])
	  #  pic_temp = myopener.open(pic["url"]).read()
	#print(pic_temp)
		pname = "./" + pic["name"] + ".png"
		#print(pname)
		with open(pname, 'wb') as f:
			f.write(pic_temp.read())

	

if __name__ == "__main__":
#    download_pic()
	zapi=login()
	print(1)
	timstag = datetime.now().strftime("%Y%m%d")
	html = '''	<html><body><h1>巡检报告-%s</h1>
	   <hr>
	   <h2>重点主机系统资源状态：</h2>
	   <table border=1 cellpadding=2 cellspacing=0 width="80%%">
			<tr>
			<th>主机</th>
			<th>CPU负载</th>
			<th>CPU空闲</th>
			<th>内存使用率</th>
			<th>TCP连接数</th>
		  </tr>''' % timstag
	print(2)
	host_list = ["192.168.1.1","192.168.1.2"]
	# define  hosts
	for h in host_list:
		rest = get_item_value(h)
                #print(rest)
		if (rest[0] > 50) and (rest[0] < 75):
			mcolor = "yellow"
		elif rest[0] > 75:
			mcolor = "red"
		else:
			mcolor = "white"
		row = '''
				<tr>
			        <td>%s</td>
				<td>%s</td>	 
				<td>%s</td>	 
				<td bgcolor="%s">%s</td>	 
				<td>%s</td>	 
				</tr>''' % (h, rest[1], rest[2], mcolor,str(int(rest[0])) + "%", rest[3])
		html = html + row
	print(3)
	download_pic()
	for f in ['nginx01.png','nginx02.png','mysql-innodb.png','mongodb.png','zookeeper.png','hbase.png','yarn.png','io.png']:
		os.remove(f)
	print(4)
	download_pic()
	html = html + ''' </table>
			注：内存使用率超过75%时有潜在风险，需要随时关注，考虑扩容机器。

			</tr>'''



	print(5)
	results = get_service_status()
	#print(results)
	for k, v in results.items():
	# print v
		if len(v) > 1:
			stat1 = v[0]
			color1 = color(stat1)
			stat2 = v[1]
			color2 = color(stat2)
		else:
			stat1 = v[0]
			color1 = color(stat1)
			stat2 = ""
			color2 = "white"
		tbline = ''' <tr>
						<td>%s</td>
						<td bgcolor="%s">%s</td>
						<td bgcolor="%s">%s</td>
						</tr>'''  %(k, color1, stat1, color2, stat2)
		html = html + tbline
		html = html + '</table>注：标红部分，NotFound和NotSupport为目前尚不支持检测接口，Down为服务进程在，但服务不可用或部分连接不可用。'
	print(6)
# problems this day
	plist = get_problem()
	html = html + '''
			<hr>
			<h2>今天0点以后产生的错误及报警:</h2>
			<table border=1  cellpadding=2 cellspacing=0 width="80%%">
			'''
	if plist:
		for p in plist:
			html = html + '<tr><td bgcolor="yellow">%s</td></tr>' % p
	else:
		html = html + '<tr><td bgcolor="green">无</td></tr>'

	html = html + '''</table><hr>
			<h2>nginx连接状态图</h2><hr>
			<br><img src="cid:nginx01" width="80%%"><br>
			<br><img src="cid:nginx02" width="80%%"><br>
			nginx服务器的连接数及tcp连接数，正常波动。
			<hr>
			<h2>Mysql-innodb连接数图</h2>
			<br><img src="cid:mysql-innodb" width="80%%"><br>
			mysql-innodb连接数，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
			<h2>mongodb连接数图</h2>
			<br><img src="cid:mongodb" width="80%%"><br>
			mongodb连接数，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
			<h2>zookeeper连接数图</h2>
			<br><img src="cid:zookeeper" width="80%%"><br>
			zookeeper连接数，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
			<h2>hbase连接数图</h2>
			<br><img src="cid:hbase" width="80%%"><br>
			hbase状态，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
			<h2>yarn连接数图</h2>
			<br><img src="cid:yarn" width="80%%"><br>
			yarn状态，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
			<h2>io连接数图</h2>
			<br><img src="cid:io" width="80%%"><br>
			大数据集群io状态，根据历史数据，如有长时间突增或骤减需要特别关注！
			<hr>
		    <h2>大数据集群宿主机磁盘空间使用情况</h2>	
			<h2>根目录</h2>
			<br><img src="cid:disk_usage_" width="80%%"><br>
			<hr>
			<h2>export目录</h2>
			<br><img src="cid:disk_usage_export" width="80%%"><br>
			<hr>
			<h2>hadoop01目录</h2>
			<br><img src="cid:disk_usage_export_haoop01" width="80%%"><br>
			<hr>
			<h2>hadoop02目录</h2>
			<br><img src="cid:disk_usage_export_haoop02" width="80%%"><br>
			<hr>
			<h2>hadoop03目录</h2>
			<br><img src="cid:disk_usage_export_haoop03" width="80%%"><br>
		    <hr>
    		<h4>end: 此邮件为程序自动发出。内容及格式优化中。。。。</h4>
			<hr>
			<br>

			</body></html>'''
	#sys.exit(0)
	print(7)
	subj = u'系统检查报告'
	recvier = []
	mail(recv=recvier, sub=subj, body=html)
