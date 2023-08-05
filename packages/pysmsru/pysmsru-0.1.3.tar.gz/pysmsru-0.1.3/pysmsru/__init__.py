# -*- coding: utf8 -*-
# pysmssend - send sms with sms.ru service.
import os
import sys
from urllib2 import urlopen
from urllib import quote, urlencode


servicecodes = {
    100: u"Сообщение принято к отправке. На следующих строчках вы найдете "
         u"идентификаторы отправленных сообщений в том же порядке, в котором "
         u"вы указали номера, на которых совершалась отправка.",
    200: u"Неправильный api_id",
    201: u"Не хватает средств на лицевом счету",
    202: u"Неправильно указан получатель",
    203: u"Нет текста сообщения",
    204: u"Имя отправителя не согласовано с администрацией",
    205: u"Сообщение слишком длинное (превышает 8 СМС)",
    206: u"Будет превышен или уже превышен дневной лимит на отправку сообщений",
    207: u"На этот номер (или один из номеров) нельзя отправлять сообщения, "
         u"либо указано более 100 номеров в списке получателей",
    208: u"Параметр time указан неправильно",
    209: u"Вы добавили этот номер (или один из номеров) в стоп-лист",
    210: u"Используется GET, где необходимо использовать POST",
    211: u"Метод не найден",
    220: u"Сервис временно недоступен, попробуйте чуть позже.",
    300: u"Неправильный token (возможно истек срок действия, либо ваш IP "
         u"изменился)",
    301: u"Неправильный пароль, либо пользователь не найден",
    302: u"Пользователь авторизован, но аккаунт не подтвержден (пользователь "
         u"не ввел код, присланный в регистрационной смс)",
}


class UnableToGetHomePath(Exception):
    pass


class RCFileNotDefined(Exception):
    pass


class SMSRU(object):
    """
    Default API ID are read from the files:
        Linux: $HOME/.smssendrc
        Windows: %USERPROFILE%/.smssendrc

    Example usage:

    smsru = SMSRU(
        api_id='youapiid' - or set in .smssendrc
        debug=True|None - Print debug messages
        sendername='sender name' - Sender name (optional)
        time=10 - Send time in UNIX TIME format (optional)
        translit=True|None|False - Convert message to translit
        http_timeout=10|None - Timeout for http connection (optional, default is 10)
    )
    smsru.send_one(phone_to='79121234567', message='Hello World!')
    smsru.send_scope(phones_to=['79120123456', '79120012345'], message='Hello World!')
    """
    API_ID = None
    PARTNER_ID = '3805'
    URL_SEND = "http://sms.ru/sms/send"
    debug = None

    def __init__(self, api_id=None, debug=None, sendername=None, time=None,
                 translit=None, http_timeout=None):
        self.API_ID = api_id or self._get_api_id()
        self.debug = debug
        self.sendername = sendername
        self.time = time
        self.translit = translit
        self.http_timeout = http_timeout

    def _get_home_path(self):
        home = None
        if sys.platform.startswith('freebsd') or \
                sys.platform.startswith('linux'):
            home = os.getenv('HOME')
        elif sys.platform.startswith('win'):
            home = os.getenv('USERPROFILE')
        if home is None:
            raise UnableToGetHomePath(u"Unable to get home path.")
        return home

    def _get_api_id(self):
        homepath = self._get_home_path()
        if '.smssendrc' not in os.listdir(homepath):
            raise RCFileNotDefined(
                u'Unable to find {0}/.smssendrc'.format(homepath))
        api_id = None
        with open("{0}/.smssendrc".format(homepath)) as fp:
            data = fp.read()
            if len(data) >= 10:  # ????
                api_id = data.replace("\n", "").replace("\r\n", "")
        return api_id

    def _get_url(self, phone_to, message):
        params = dict(
            api_id=self.API_ID,
            to=phone_to,
            text=quote(message)
        )
        if self.debug:
            params['test'] = '1'
        if self.sendername:
            params['from'] = self.sendername
        if self.time:
            params['time'] = int(self.time)
        if self.translit:
            params['translit'] = '1'
        url = u'{0}?{1}'.format(self.URL_SEND, urlencode(params))
        return url

    def _show_debug_messages(self, msg):
        if self.debug:
            print msg

    def send_one(self, phone_to, message):
        url = self._get_url(phone_to, message)
        res = urlopen(url, timeout=self.http_timeout)
        self._show_debug_messages(u"GET: {0} {1}\nReply:\n{2}".format(
            res.geturl(), res.msg, res.info()))

        service_result = res.read().splitlines()

        if service_result is not None:
            scode = int(service_result[0])
            if scode == 100:
                self._show_debug_messages(
                    u"smssend[debug]: Message send ok. ID: {0}".format(
                        service_result[1]))
            else:
                self._show_debug_messages(
                    u"smssend[debug]: Unable send sms message to {0} when "
                    u"service has returned code: {1} ".format(
                        phone_to, servicecodes[int(service_result[0])]))


    def send_scope(self, phones_to, message):
        if not isinstance(phones_to, (list, tuple)):
            raise ValueError(
                u'Required list or tuple not {0}'.format(type(phones_to)))
        for phone_to in phones_to:
            self.send_one(phone_to, message)
