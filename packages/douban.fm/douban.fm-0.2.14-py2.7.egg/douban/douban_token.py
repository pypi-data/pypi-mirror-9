#-*- encoding: UTF-8 -*-
"""
豆瓣FM的网络连接部分
"""
#---------------------------------import------------------------------------
import requests
import tempfile
import lrc2dic
import getpass
import pickle
import urllib
import os
#---------------------------------------------------------------------------
class Doubanfm(object):
    def __init__(self):
        self.login_data = {}
        self.channel_id = 0
        self.lines = [] # 要输出到终端的行
        # 红心兆赫需要手动添加
        self.channels = [{
            'name':'红心兆赫',
            'channel_id' : -3
            }]
        self.pro = 0
        self.playlist = [] # 播放列表
        self.playingsong = {} # 当前播放歌曲
        self.find_lrc = False  # 是否查找过歌词
        self.lrc_dic = {}  # 歌词
        print '''
        ──╔╗─────╔╗────────╔═╗
        ──║║─────║║────────║╔╝
        ╔═╝╠══╦╗╔╣╚═╦══╦═╗╔╝╚╦╗╔╗
        ║╔╗║╔╗║║║║╔╗║╔╗║╔╗╬╗╔╣╚╝║
        ║╚╝║╚╝║╚╝║╚╝║╔╗║║║╠╣║║║║║
        ╚══╩══╩══╩══╩╝╚╩╝╚╩╩╝╚╩╩╝

        '''
        self.login() # 登陆
        self.get_channels() # 获取频道列表
        self.get_channellines() # 重构列表用以显示
        self.is_pro()
        if self.pro == 1:
            self.login_data['kbps'] = 192 # 128 64 歌曲kbps的选择

    # 查看是否是pro用户
    def is_pro(self):
        self.get_playlist()
        self.get_song()
        if  int(self.playingsong['kbps']) != 64:
            self.pro = 1
        self.playingsong = {} # 清空列表

    # 登陆界面
    def win_login(self):
        email = raw_input('email:')
        password = getpass.getpass('password:')
        return email, password

    # 登陆douban.fm获取token
    def login(self):
        path_token = os.path.expanduser('~/.douban_token.txt')
        if  os.path.exists(path_token): # 已登陆
            with open(path_token, 'r') as f:
                self.login_data = pickle.load(f)
                self.token = self.login_data['token']
                self.user_name = self.login_data['user_name']
                self.user_id = self.login_data['user_id']
                self.expire = self.login_data['expire']
        else: # 未登陆
            while True:
                self.email, self.password = self.win_login()
                login_data = {
                        'app_name': 'radio_desktop_win',
                        'version': '100',
                        'email': self.email,
                        'password': self.password
                        }
                s = requests.post('http://www.douban.com/j/app/login', login_data)
                dic = eval(s.text)
                if dic['r'] == 1:
                    print dic['err']
                    continue
                else:
                    self.token = dic['token']
                    self.user_name = dic['user_name']
                    self.user_id = dic['user_id']
                    self.expire = dic['expire']
                    self.login_data = {
                        'app_name' : 'radio_desktop_win',
                        'version' : '100',
                        'user_id' : self.user_id,
                        'expire' : self.expire,
                        'token' : self.token,
                        'user_name' : self.user_name
                            }
                    with open(path_token, 'w') as f:
                        pickle.dump(self.login_data, f)
                    break
        # 配置文件
        path_config = os.path.expanduser('~/.doubanfm_config')
        if not os.path.exists(path_config):
            config = '''[key]
UP = k
DOWN = j
TOP = g
BOTTOM = G
OPENURL = w
RATE = r
NEXT = n
BYE = b
QUIT = q
PAUSE = p
LOOP = l
MUTE = m
LRC = o
''' # 这个很丑,怎么办
            with open(path_config, 'w') as F:
                F.write(config)

    # 获取channel,c存入self.channels
    def get_channels(self):
        r = requests.get('http://www.douban.com/j/app/radio/channels')
        self.channels += eval(r.text)['channels']

    # 格式化频道列表,以便display
    def get_channellines(self):
        for index, channel in enumerate(self.channels):
            self.lines.append(channel['name'])

    # 发送post_data
    def requests_url(self, ptype, **data):
        post_data = self.login_data.copy()
        post_data['type'] = ptype
        for x in data:
            post_data[x] = data[x]
        s = requests.get('http://www.douban.com/j/app/radio/people?' + urllib.urlencode(post_data))
        return s.text

    # 当playlist为空,获取播放列表
    def get_playlist(self):
        self.login_data['channel'] = self.channel_id
        s = self.requests_url('n')
        self.playlist = eval(s)['song']

    # 下一首
    def skip_song(self):
        s = self.requests_url('s', sid=self.playingsong['sid'])
        self.playlist = eval(s)['song']

    # bye,不再播放
    def bye(self):
        s = self.requests_url('b', sid=self.playingsong['sid'])
        self.playlist = eval(s)['song']

    # 选择频道
    def set_channel(self, num):
        self.channel_id = num

    # 获得歌曲
    def get_song(self):
        self.find_lrc = False
        self.lrc_dic = {}
        if not self.playlist:
            self.get_playlist()
        self.playingsong = self.playlist.pop(0)

    # 标记喜欢歌曲
    def rate_music(self):
        s = self.requests_url('r', sid=self.playingsong['sid'])
        self.playlist = eval(s)['song']

    # 取消标记喜欢歌曲
    def unrate_music(self):
        s = self.requests_url('u', sid=self.playingsong['sid'])
        self.playlist = eval(s)['song']

    # 歌曲结束标记
    def end_music(self):
        s = self.requests_url('e', sid=self.playingsong['sid'])

    # 获取专辑封面
    def get_pic(self):
        path = os.path.join(tempfile.gettempdir(), 'tmp.jpg')
        url = self.playingsong['picture'].replace('\\', '')
        urllib.urlretrieve(url, path)
        return path

    def get_lrc(self):
        if not self.find_lrc:
            try:
                url = "http://api.douban.com/v2/fm/lyric"
                postdata = {
                        'sid':self.playingsong['sid'],
                        'ssid':self.playingsong['ssid'],
                        }
                s = requests.session()
                response = s.post(url, data = postdata)
                lyric = eval(response.text)
                lrc_dic = lrc2dic.lrc2dict(lyric['lyric'])
                for key, value in lrc_dic.iteritems():
                    lrc_dic[key] = value.decode('utf-8')  # 原歌词用的unicode,为了兼容
                self.lrc_dic = lrc_dic
                return lrc_dic
            except:
                return 0
        self.find_lrc = True
        return lrc_dic
############################################################################
