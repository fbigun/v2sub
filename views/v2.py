# coding: utf-8

from leancloud import Object
from leancloud import Query
from leancloud import LeanCloudError
from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
import json


class V2website(Object):
    pass

class V2info(Object):
    pass


v2website = Blueprint('v2', __name__)


@v2website.route('')
def show():
    try:
        v2 = Query(V2website).descending('createdAt').find()
    except LeanCloudError as e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            v2 = []
        else:
            raise e
    return render_template('v2.html', v2=v2)


@v2website.route('/sub')
def sub():
    try:
        v2url = Query(V2info).add_descending('createdAt').first()
    except LeanCloudError as e:
        print(e)
        context = None
    else:
        context = v2url.get('urls_vmess_paser')
    return context


@v2website.route('', methods=['POST'])
def add():
    content = request.form
    v2 = V2website(**content.to_dict())
    try:
        v2.save()
    except LeanCloudError as e:
        return e.error, 502
    return redirect(url_for('v2.show'))
