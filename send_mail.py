from fabric import Connection

import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr

hosts = ["192.168.1.1","192.168.122.3"]
#define hosts 


user = "******"
passwd = "******"

# passwd = "gudao123"
result = dict()
def disk_space():
    for host in hosts:
            conn = Connection(host,user=user,connect_kwargs={"password":passwd})
            re = conn.run("df -hP | awk 'NR>1 && int($5) > 60' ")
            response = re.stdout.strip()
            result[host] = response
    return result


def build_content(result):
    html= ''
    for key,value in result.items():
        if value != "":
            row = '''
                    <tr>
                    <td>{}</td>
                    <td>{}</td>
                    </tr>
                    '''.format(key, value)

            html = html + row
    return html

html_tail = '''
         <h5>本邮件为系统自动发送，内容迭代中......</h5>
    </html>
    '''

html_head = '''	<html><body><h1>运维检测报告</h1>
    	   <hr>
    	   <h2>生产机器磁盘空间：</h2>
    	   <p>超出百分之50,需关注！</p>
    	   <table border=1 cellpadding=2 cellspacing=0 width="80%%">

    '''


def content(middle):
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))
    sender_mail = "******@163.com"
    to_mail = ["****@****.com","****@****.com"]
    html_sub = MIMEMultipart('related')
    html_sub['Subject'] = Header('服务器磁盘空间检查', 'utf-8').encode()
    html_sub['From'] = _format_addr('YBY_Admin <%s>' % sender_mail)
    html_sub['to'] = _format_addr('YBY_User <%s>' % to_mail)
    html_info = html_head + middle + html_tail
    html_txt = MIMEText(html_info, 'html', 'utf-8')
    html_sub.attach(html_txt)
    return html_sub

def send_mail(cont):
    sender_mail = "1231@163.com"
    sender_passwd = "*********"

    to_mail = ["122222@163.com","1222@162.com"]
    # email address
    server = smtplib.SMTP_SSL('smtp.163.com',465)
    server.set_debuglevel(0)
    server.login(sender_mail,sender_passwd)
    server.sendmail(sender_mail,to_mail,cont.as_string())
    server.quit()


s=disk_space()
row = build_content(s)
Con=content(row)
send_mail(Con)
