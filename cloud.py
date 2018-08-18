# coding: utf-8

import base64
import json
from datetime import datetime
from leancloud import Query
from leancloud import Object
from leancloud import Engine
from leancloud import LeanEngineError
import requests
from requests import RequestException

engine = Engine()


@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'


@engine.before_save('Todo')
def before_todo_save(todo):
    content = todo.get('content')
    if not content:
        raise LeanEngineError('内容不能为空')
    if len(content) >= 240:
        todo.set('content', content[:240] + ' ...')

@engine.define
def update_sub():
    v2s = Query('V2website').find()
    V2info = Object.extend('V2info')
    v2info = V2info()
    urls_vmess=[]
    status=[]
    time=datetime.now()

    for v2 in v2s:
        if v2.Inactivated == '0':
            status.append({'name': v2.name, 'status': '已停用'})
            continue
        try:
            context = requests.get(v2.url_sub, timeout=5)
        except RequestException:
            status.append({'name': v2.name, 'status': '更新失败'})
            pass
        else:
            urls = base64.standard_b64decode(context.content).decode('utf-8').split('\n')
            for url in urls:

                protocol, config = url.split('://')
                if protocol == 'vmess':
                    config_parse = base64.standard_b64decode(config).decode('utf-8')
                    config_dict = json.loads(config_parse)
                    config_dict['ps'] = ''.join([ '[', v2.Abbreviation, ']', config_dict['ps']])
                    config_parse = base64.standard_b64encode(json.dumps(config_dict).encode('utf-8'))
                    url_vmess = ''.join(['vmess://', config_parse])
                urls_vmess.append(url_vmess)
    urls_vmess_paser = base64.standard_b64encode('\n'.join(urls_vmess).encode('utf-8'))
    v2info.set('status', status)
    v2info.set('time', time)
    v2info.set('urls_vmess_paser', urls_vmess_paser)
    try:
        v2info.save()
    except:
        print('保存失败')


