__author__ = 'Reza Safaeiyan'

import json
import redis
from config import *


# noinspection PyBroadException
class ReSession():
    def __init__(self, handler):
        self.c = config
        self.redis_instance = redis.StrictRedis(
            host=self.c.host, port=self.c.port,
            db=self.c.db, password=self.c.password
        )
        self.__handler = handler
        try:
            self.__ip_address = self.__handler.request.remote_ip
        except:
            self.__ip_address = ''
        try:
            self.__user_agent = self.__handler.request.headers['User-Agent']
        except:
            self.__user_agent = None
        try:
            ss = self.__handler.get_secure_cookie('ReSSID')
            if ss and len(ss) == 37:
                self.__id = ss
            else:
                self.__id = self.__mk_sid()
        except:
            self.__id = self.__mk_sid()

        self.__make_session()

    def __auth(self):
        try:
            _di = self.redis_instance.get(self.__id)
            if _di:
                _di = json.loads(_di)
                if _di['ip_address'] == self.__ip_address:
                    if _di['user_agent'] == self.__user_agent:
                        return True
            else:
                self.__remove_from_db(sid=self.__id)
        except:
            pass
        return False

    def __make_session(self):
        if self.__auth():
            self.__update_session(self.__id)
        else:
            try:
                if self.__ip_address != '':
                    self.__id = self.__mk_sid()

                    self.__handler.set_secure_cookie("ReSSID", self.__id, (self.c.expire_time / 86400.0))

                    _temp = {
                        'ip_address': self.__ip_address,
                        'user_agent': self.__user_agent,
                        'data': {}
                    }
                    self.redis_instance.setex(self.__id, self.c.expire_time, json.dumps(_temp))
            except:
                pass

    def __remove_from_db(self, sid=None):
        try:
            if sid:
                self.redis_instance.delete(sid)
            return True
        except:
            return False

    def __update_session(self, sid):
        try:
            self.redis_instance.expire(sid, self.c.expire_time)
            return True
        except:
            return False


    def set(self, name=None, value=None):
        try:
            if not name or not value:
                return False
            _di = self.redis_instance.get(self.__id)
            if _di:
                _di = json.loads(_di)
                _di['data'][name] = value
                self.redis_instance.setex(self.__id, self.c.expire_time, json.dumps(_di))
            return True
        except:
            return False

    def get(self, name=None, default=None):
        try:
            _di = self.redis_instance.get(self.__id)
            if _di:
                _di = json.loads(_di)
                return _di['data'][name]
        except:
            if default:
                return default
            else:
                return None

    def get_sid(self):
        return self.__id

    def get_keys(self):
        try:
            _di = json.loads(self.redis_instance.get(self.__id))
            return list([k for k in _di['data'].keys()])
        except:
            return []

    def is_exist(self, name, index=False):
        k = self.get_keys()
        if name in k:
            return k.index(name) if index else True
        else:
            return -1 if index else False

    def delete(self, name):
        ind = self.is_exist(name)
        try:
            if ind:
                _di = json.loads(self.redis_instance.get(self.__id))
                if _di:
                    _di['data'].pop(name, None)
                    self.redis_instance.setex(self.__id, self.c.expire_time, json.dumps(_di))
                    return True
            else:
                return False
        except:
            return False

    def destroy(self):
        try:
            _di = self.redis_instance.get(self.__id)
            if _di:
                _di = json.loads(_di)
                _di['data'] = {}
                self.redis_instance.setex(self.__id, self.c.expire_time, json.dumps(_di))
            return True
        except:
            return False

    @staticmethod
    def __mk_sid():
        alpha = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(48, 58)]
        import random
        rnd = ""

        key = {'key': config.secret_key, 'length': len(config.secret_key)}

        for i in range(0, 63):
            if len(rnd) < 37:
                if i % 2 == 0:
                    rnd += alpha[random.randint(0, 61)]
                else:
                    rnd += key['key'][random.randint(0, (int(key['length']) - 1))]
            else:
                break
        return rnd