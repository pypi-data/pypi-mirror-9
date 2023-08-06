# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import os
import sys
import argparse
import codecs
from ConfigParser import ConfigParser
import urllib2
import re
import base64
import json
import time

from .pysocks.socks import PROXY_TYPES as _proxy_types
from .pysocks.sockshandler import SocksiPyHandler

# from pprint import pprint

__version__ = '1.1.0'
__author__ = 'JinnLynn <eatfishlin@gmail.com>'
__license__ = 'The MIT License'
__copyright__ = 'Copyright 2013-2015 JinnLynn'

__all__ = ['main']

_default_gfwlist_url = 'https://autoproxy-gfwlist.googlecode.com/svn/trunk/gfwlist.txt'
_proxy_types['SOCKS'] = _proxy_types['SOCKS4']
_proxy_types['PROXY'] = _proxy_types['HTTP']

class HelpAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(HelpAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        with codecs.open(pkgdata('res/help.txt'), 'r', 'utf-8') as fp:
            print(fp.read())
        parser.exit()


_ret = argparse.Namespace()
_cfg = None

def abspath(path):
    if not path:
        return path
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(path)

def pkgdata(path):
    dir_path = os.path.dirname(__file__)
    dir_path = dir_path if dir_path else os.getcwd()
    return os.path.join(dir_path, path)

def error(*args, **kwargs):
    print(*args, file=sys.stderr)
    if kwargs.get('exit', False):
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(
        prog='genpac',
        add_help=False      # 默认的帮助输出对中文似乎有问题，不使用
    )
    parser.add_argument('-p', '--proxy')
    parser.add_argument('--gfwlist-url', default=_default_gfwlist_url)
    parser.add_argument('--gfwlist-proxy')
    parser.add_argument('--gfwlist-local')
    parser.add_argument('--disable-overwrite', action='store_true', default=False)
    parser.add_argument('--user-rule', action='append')
    parser.add_argument('--user-rule-from', action='append')
    parser.add_argument('--output')
    parser.add_argument('--config-from')
    parser.add_argument('-v', '--version',
                        action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('-h', '--help', action=HelpAction)
    return parser.parse_args()

def parse_config():
    cfg = {}
    args = parse_args()
    def update(name, key, default=None):
        v = getattr(args, name, None)
        if v:
            return v
        try:
            return cfg.get(key, default).strip(' \'\t"')
        except:
            return default

    if args.config_from:
        args.config_from = abspath(args.config_from)
        try:
            with codecs.open(args.config_from, 'r', 'utf-8') as fp:
                cfg_parser = ConfigParser()
                cfg_parser.readfp(fp)
                cfg = dict(cfg_parser.items('config'))
            args.gfwlist_url = update('gfwlist_url', 'gfwlist-url', _default_gfwlist_url)
            args.gfwlist_proxy = update('gfwlist_proxy', 'gfwlist-proxy')
            args.gfwlist_local = update('gfwlist_local', 'gfwlist-local')
            args.proxy = update('proxy', 'proxy')
            args.user_rule_from = update('user_rule_from', 'user-rule-from')
            args.output = update('output', 'output')
        except:
            error('read config file fail.')
    if args.user_rule is None:
        args.user_rule = []
    if not isinstance(args.user_rule, list):
        args.user_rule = [args.user_rule]
    if args.user_rule_from is None:
        args.user_rule_from = []
    if not isinstance(args.user_rule_from, list):
        args.user_rule_from = [args.user_rule_from]
    return args

def prepare():
    global _cfg, _ret
    _cfg = parse_config()
    _cfg.output = abspath(_cfg.output)
    _cfg.gfwlist_local = abspath(_cfg.gfwlist_local)
    _ret.version = __version__
    _ret.generated = ''
    _ret.modified = ''
    _ret.gfwlist_from = ''
    _ret.proxy = _cfg.proxy if _cfg.proxy else 'DIRECT'
    _ret.rules = ''

def build_opener():
    if not _cfg.gfwlist_proxy:
        return urllib2.build_opener()
    try:
        # 格式为 代理类型 [用户名:密码]@地址:端口 其中用户名和密码可选
        matches = re.match(r'(PROXY|SOCKS|SOCKS4|SOCKS5) (?:(.+):(.+)@)?(.+):(\d+)',
                           _cfg.gfwlist_proxy,
                           re.IGNORECASE)
        type_, usr, pwd, host, port = matches.groups()
        type_ = _proxy_types[type_.upper()]
        return urllib2.build_opener(
            SocksiPyHandler(type_, host, int(port), username=usr, password=pwd))
    except:
        error('gfwlist proxy error.', exit=True)

def fetch_gfwlist():
    global _ret
    content = ''
    opener = build_opener()
    try:
        res = opener.open(_cfg.gfwlist_url)
        content = res.read()
    except:
        try:
            with codecs.open(_cfg.gfwlist_local, 'r', 'utf-8') as fp:
                content = fp.read()
            _ret.gfwlist_from = 'local[{}]'.format(_cfg.gfwlist_local)
        except:
            pass
    else:
        _ret.gfwlist_from = 'online[{}]'.format(_cfg.gfwlist_url)
        if _cfg.gfwlist_local and not _cfg.disable_overwrite:
            with codecs.open(_cfg.gfwlist_local, 'w', 'utf-8') as fp:
                fp.write(content)
    if not content:
        error('fetch gfwlist fail.', exit=True)
    try:
        content = '! {}'.format(base64.decodestring(content))
        content = content.splitlines()
        for line in content:
            if line.startswith('!') and 'Last Modified' in line:
                _ret.modified = line.split(':', 1)[1].strip()
                break
    except:
        pass
    return content

def fetch_user_rules():
    rules = _cfg.user_rule
    for f in _cfg.user_rule_from:
        if not f:
            continue
        try:
            with codecs.open(abspath(f), 'r', 'utf-8') as fp:
                file_rules = fp.read().split('\n')
                rules.extend(file_rules)
        except:
            error('read user rule file fail. ', f)
    return rules

def parse_rules(rules):
    def wildcard_to_regexp(pattern):
        pattern = re.sub(r'([\\\+\|\{\}\[\]\(\)\^\$\.\#])', r'\\\1', pattern)
        #pattern = re.sub(r'\*+', r'*', pattern)
        pattern = re.sub(r'\*', r'.*', pattern)
        pattern = re.sub(r'\？', r'.', pattern)
        return pattern
    # d=direct p=proxy w=wildchar r=regexp
    result = {'d' : {'w' : [], 'r' : []}, 'p' :{'w' : [], 'r' : []}}
    for line in rules:
        line = line.strip()
        # comment
        if not line or line.startswith('!'):
            continue
        d_or_p = 'p'
        w_or_r = 'r'
        # original_line = line
        # 例外
        if line.startswith('@@'):
            line = line[2:]
            d_or_p = 'd'
        # 正则表达式语法
        if line.startswith('/') and line.endswith('/'):
            line = line[1:-1]
        elif line.find('^') != -1:
            line = wildcard_to_regexp(line)
            line = re.sub(r'\\\^', r'(?:[^\w\-.%\u0080-\uFFFF]|$)', line)
        elif line.startswith('||'):
            line = wildcard_to_regexp(line[2:])
            # When using the constructor function, the normal string escape rules (preceding
            # special characters with \ when included in a string) are necessary.
            # For example, the following are equivalent:
            # re = new RegExp('\\w+')
            # re = /\w+/
            # via: http://aptana.com/reference/api/RegExp.html
            # line = r'^[\\w\\-]+:\\/+(?!\\/)(?:[^\\/]+\\.)?' + line
            # 由于后面输出时使用json.dumps会自动对其转义，因此这里可不使用对\转义
            line = r'^[\w\-]+:\/+(?!\/)(?:[^\/]+\.)?' + line
        elif line.startswith('|') or line.endswith('|'):
            line = wildcard_to_regexp(line)
            line = re.sub(r'^\\\|', '^', line, 1)
            line = re.sub(r'\\\|$', '$', line)
        else:
            w_or_r = 'w'
        if w_or_r == 'w':
            line = '*{}*'.format(line.strip('*'))
        result[d_or_p][w_or_r].append(line)
    return [result['d']['r'], result['d']['w'], result['p']['r'], result['p']['w'],]

def generate(gfwlist_rules, user_rules):
    global _ret
    rules = [parse_rules(user_rules), parse_rules(gfwlist_rules)]
    _ret.rules = json.dumps(rules, indent=4)
    _ret.generated = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

def output():
    with codecs.open(pkgdata('res/pac-tpl.js'), 'r', 'utf-8') as fp:
        content = fp.read()

    content = content.replace('__VERSION__', _ret.version)
    content = content.replace('__GENERATED__', _ret.generated)
    content = content.replace('__MODIFIED__', _ret.modified)
    content = content.replace('__GFWLIST_FROM__', _ret.gfwlist_from)
    content = content.replace('__PROXY__', _ret.proxy)
    content = content.replace('__RULES__', _ret.rules)

    file_ = codecs.open(_cfg.output, 'w', 'utf-8') if _cfg.output else sys.stdout
    file_.write(content)

def main():
    prepare()

    gfwlist = fetch_gfwlist()
    user_rules = fetch_user_rules()

    generate(gfwlist, user_rules)

    output()

if __name__ == '__main__':
    main()
