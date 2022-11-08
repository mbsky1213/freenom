# https://github.com/SunYufei/freenom
import re

import flask
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', methods=['GET'])
def home():
    return flask.render_template('index.html', report='')


@app.route('/renew', methods=['GET', 'POST'])
def renew():
    report = ''

    username = flask.request.args.get('username')
    password = flask.request.args.get('password')
    # 登录地址
    LOGIN_URL = 'https://my.freenom.com/dologin.php'
    # 域名状态地址
    DOMAIN_STATUS_URL = 'https://my.freenom.com/domains.php?a=renewals'
    # 域名续期地址
    RENEW_DOMAIN_URL = 'https://my.freenom.com/domains.php?submitrenewals=true'

    # token 正则
    token_ptn = re.compile('name="token" value="(.*?)"', re.I)
    # 域名信息正则
    domain_info_ptn = re.compile(
        r'<tr><td>(.*?)</td><td>[^<]+</td><td>[^<]+<span class="[^<]+>(\d+?).Days</span>[^&]+&domain=(\d+?)">.*?</tr>',
        re.I)
    # 登录状态正则
    login_status_ptn = re.compile('<a href="logout.php">Logout</a>', re.I)

    # request session
    sess = requests.Session()
    sess.headers.update({
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/103.0.5060.134 Safari/537.36'
    })

    # login
    sess.headers.update({
        'content-type': 'application/x-www-form-urlencoded',
        'referer': 'https://my.freenom.com/clientarea.php'
    })
    r = sess.post(LOGIN_URL, data={'username': username, 'password': password})
    if r.status_code != 200:
        report += 'login failed' + ' ' + username + ' ' + password + '\n'
        return flask.Response(report, mimetype='text/plain')

    # check domain status
    sess.headers.update({'referer': 'https://my.freenom.com/clientarea.php'})
    r = sess.get(DOMAIN_STATUS_URL)

    # login status check
    if not re.search(login_status_ptn, r.text):
        report += 'get login status failed' + '\n'
        return flask.Response(report, mimetype='text/plain')

    # page token
    match = re.search(token_ptn, r.text)
    if not match:
        report += 'get page token failed' + '\n'
        return flask.Response(report, mimetype='text/plain')

    token = match.group(1)

    # domains
    domains = re.findall(domain_info_ptn, r.text)

    # renew domains
    for domain, days, renewal_id in domains:
        days = int(days)
        if days < 14:
            sess.headers.update({
                'referer':
                f'https://my.freenom.com/domains.php?a=renewdomain&domain={renewal_id}',
                'content-type': 'application/x-www-form-urlencoded'
            })
            r = sess.post(RENEW_DOMAIN_URL,
                          data={
                              'token': token,
                              'renewalid': renewal_id,
                              f'renewalperiod[{renewal_id}]': '12M',
                              'paymentmethod': 'credit'
                          })
            if r.text.find('Order Confirmation') != -1:
                report += f'{domain} 续期成功' + '\n'
            else:
                report += f'{domain} 续期失败' + '\n'
        report += f'{domain} 还有 {days} 天续期' + '\n'
    return flask.Response(report, mimetype='text/plain')