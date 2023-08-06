# -*- coding: utf-8 -*-
"""
以\n为每个包的结束
和box不太一样的时，body内部存的是bytes，而外面读取的是unicode
"""

import json

END_STR = '\n'
ENCODING = 'utf-8'


def safe_str(src):
    if isinstance(src, unicode):
        return src.encode(ENCODING)

    return str(src)


class LineBox(object):
    """
    LineBox 打包解包
    """

    # 如果调用unpack成功的话，会置为True
    _unpack_done = None

    # 存储的话，还是统一用str
    _body = None

    def __init__(self, init_data=None):
        self._unpack_done = False

        self.body = ''

        if init_data and isinstance(init_data, dict):
            for k, v in init_data.items():
                setattr(self, k, v)

    @property
    def unpack_done(self):
        return self._unpack_done

    @property
    def body(self):
        # 返回时统一用unicode
        return self._body.decode(ENCODING)

    @body.setter
    def body(self, value):
        if not value.endswith(END_STR):
            value += END_STR

        self._body = safe_str(value)

    def pack(self):
        """
        打包
        """
        return self._body

    def unpack(self, buf, save=True):
        """
        解析buf，并赋值

        :param buf:     输入buf
        :param save:    是否赋值
        :return:
            >0: 成功生成obj，返回了使用的长度，即剩余的部分buf要存起来
            <0: 报错
            0: 继续收
        """

        found_idx = buf.find(END_STR)
        if found_idx < 0:
            # 说明没有\n
            return 0

        packet_len = found_idx + len(END_STR)

        if not save:
            # 如果不需要保存的话，就直接返回好了
            return packet_len

        # 直接赋值减少判断
        self._body = buf[:packet_len]

        self._unpack_done = True

        return packet_len

    def check(self, buf):
        """
        仅检查buf是否合法

        :param buf:     输入buf
        :return:
            >0: 成功生成obj，返回了使用的长度，即剩余的部分buf要存起来
            <0: 报错
            0: 继续收
        """
        return self.unpack(buf, save=False)

    def map(self, map_data):
        """
        获取对应的response
        :param :map_data
        :return:
        """
        return self.__class__(map_data)

    def get_json(self):
        """
        解析为json格式
        用函数而不是属性的原因参考requests、flask.request
        :return:
        """
        if not self.body:
            return None
        return json.loads(self.body)

    def set_json(self, value):
        """
        打包为json格式
        :return:
        """
        if not value:
            self.body = ''
            return
        self.body = json.dumps(value)

    def __repr__(self):
        return repr(self._body)
