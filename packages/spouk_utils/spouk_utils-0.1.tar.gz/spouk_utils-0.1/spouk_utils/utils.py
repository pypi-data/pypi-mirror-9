# coding: utf-8
__author__ = 'spouk'

import random
import string
from datetime import datetime
from hashlib import md5
from email.mime.text import MIMEText
import smtplib
import os
from random import randint
import base64
from flask import session
from BeautifulSoup import BeautifulSoup
from PIL import Image
from decorators import debug_wrapper


########################################################
# random functions for easy coding in flask distribution
########################################################
@debug_wrapper(debug=True)
def csrf_token_generate(length_token=100):
    """make random string and push session"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(
            [random.choice(string.ascii_letters + string.digits) for n in xrange(length_token)])
    return session['_csrf_token']


###################
# time functions
###################
@debug_wrapper(debug=True)
def time_expired(day=1):
    """get current date and + current day day for write Restore password link active"""
    tmp = datetime.today().strftime("%Y%m%d%H")
    return datetime(year=int(tmp[0:4]), month=int(tmp[4:6]), day=int(tmp[6:8]) + day, hour=int(tmp[8:10]))


################
# users function
################
@debug_wrapper(debug=True)
def user_make_profile(basedir, idprofile):
    """create defaults user profile in /static/users/<idprofile>/"""
    userProfile = os.path.join(basedir, idprofile)
    userProfileImage = os.path.join(userProfile, 'image')
    userProfileUpload = os.path.join(userProfile, 'upload')
    [os.mkdir(x) for x in [userProfile, userProfileImage, userProfileUpload]]


# ##############
# text function
###############
@debug_wrapper(debug=True)
def make_random_string_for_password():
    """random generating string for make_hash_password and send user with recovery password"""
    return md5(''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(11)])).hexdigest()


@debug_wrapper(debug=True)
def text_from_markdown(html_to_text):
    """clear text htmltags for edit in post example"""
    return ''.join(BeautifulSoup(html_to_text).findAll(text=True))


@debug_wrapper(debug=True)
def transliter(string, mode='en'):
    """ transliter GOST """

    book_gost = {u'А': u'A', u'Б': u'B', u'В': u'V', u'Г': u'G', u'Ь': u"''",
                 u'Д': u'D', u'Е': u'E', u'Ё': u'E', u'З': u'Z', u'И': u'I',
                 u'Й': u'J', u'К': u'K', u'Л': u'L', u'М': u'M', u'Н': u'N',
                 u'О': u'O', u'П': u'P', u'Р': u'R', u'С': u'S', u'Т': u'T',
                 u'У': u'U', u'Ф': u'F', u'Х': u'H', u'Ъ': u'""', u'Ы': u'Y',
                 u'Э': u'E', u'Ж': u'Zh', u'Ц': u'Ts', u'Ч': u'Ch', u'Ш': u'Sh',
                 u'Щ': u'Sch', u'Ю': u'Yu', u'Я': u'Ya', u'а': u'a', u'б': u'b',
                 u'в': u'v', u'г': u'g', u'д': u'd', u'е': u'e', u'ё': u'e',
                 u'ж': u'zh', u'з': u'z', u'и': u'i', u'й': u'j', u'к': u'k',
                 u'л': u'l', u'м': u'm', u'н': u'n', u'о': u'o', u'п': u'p',
                 u'р': u'r', u'с': u's', u'т': u't', u'у': u'u', u'ф': u'f',
                 u'х': u'h', u'ц': u'ts', u'ч': u'ch', u'ш': u'sh', u'щ': u'sch',
                 u'ъ': u'"', u'ы': u'y', u'ь': u"'", u'э': u'e', u'ю': u'yu',
                 u'я': u'ya', }

    book = {u'А': u'A', u'Б': u'B', u'В': u'V', u'Г': u'G', u'Ь': u"",
            u'Д': u'D', u'Е': u'E', u'Ё': u'E', u'З': u'Z', u'И': u'I',
            u'Й': u'J', u'К': u'K', u'Л': u'L', u'М': u'M', u'Н': u'N',
            u'О': u'O', u'П': u'P', u'Р': u'R', u'С': u'S', u'Т': u'T',
            u'У': u'U', u'Ф': u'F', u'Х': u'H', u'Ъ': u'', u'Ы': u'Y',
            u'Э': u'E', u'Ж': u'Zh', u'Ц': u'Ts', u'Ч': u'Ch', u'Ш': u'Sh',
            u'Щ': u'Sch', u'Ю': u'Yu', u'Я': u'Ya', u'а': u'a', u'б': u'b',
            u'в': u'v', u'г': u'g', u'д': u'd', u'е': u'e', u'ё': u'e',
            u'ж': u'zh', u'з': u'z', u'и': u'i', u'й': u'j', u'к': u'k',
            u'л': u'l', u'м': u'm', u'н': u'n', u'о': u'o', u'п': u'p',
            u'р': u'r', u'с': u's', u'т': u't', u'у': u'u', u'ф': u'f',
            u'х': u'h', u'ц': u'ts', u'ч': u'ch', u'ш': u'sh', u'щ': u'sch',
            u'ъ': u'', u'ы': u'y', u'ь': u"", u'э': u'e', u'ю': u'yu',
            u'я': u'ya', }

    result = []

    if mode == 'en':
        for key in string:
            try:
                result.append(book[key])
            except:
                result.append(key)
        return ''.join(result)

    if mode == 'ru':
        book_ru = {book[key]: key for key in book}
        tmpbook = {key: book_ru[key] for key in book_ru if len(key) > 1}
        for key in tmpbook:
            string = string.replace(key, book_ru[key])
        for key in string:
            try:
                string = string.replace(key, book_ru[key])
            except:
                pass
        return string


@debug_wrapper(debug=True)
def slugprobel(string, debug=False):
    """remove space and put - for good navigate in fucken WWW"""

    def erase(msg):
        result = []
        erasesym2 = '!"#$%&\'()*\-/<=>?@\[\\\]^_`-{|},.]'
        erasesym = u'!"#$%&\'()*\\-/<=>?@\\[\\\\]^_`{|},.]\u2014\u2013\u2012'

        for sym in msg:
            if sym in erasesym:
                result.append(u' ')
            else:
                result.append(sym)
        result = ' '.join(''.join(result).split())
        return result

    string = erase(string)  # удаление всякого непотребства
    string = string.decode('utf-8')
    return u'-'.join(string.split())


##################
# email functions
#################
@debug_wrapper(debug=True)
def mail_notification_subscribe(_from, _to, message,
                                subject="good news for u from somesite"):
    msg = MIMEText(message, _charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = _from
    msg['To'] = _to
    servak = smtplib.SMTP('localhost')
    servak.sendmail(_from,
                    [_to],
                    msg.as_string())
    servak.quit()


@debug_wrapper(debug=True)
def mailsend(_from, _to, message, attach=None, hostname=None):
    """send email __from, __to """
    msg = MIMEText(message, _charset='utf-8')
    msg['Subject'] = "Recovery password "
    msg['From'] = _from
    msg['To'] = _to
    servak = smtplib.SMTP('localhost')
    servak.sendmail(_from,
                    [_to],
                    msg.as_string())
    servak.quit()


###########################
# random filters for jinja2
###########################
@debug_wrapper(debug=True)
def datetimeformat(value, format='%d-%m-%Y'):
    return value.strftime(format)


@debug_wrapper(debug=True)
def yes_no(flag):
    """filter checker bool flag"""
    return u'Прочитано' if flag else u'Непрочитано'


@debug_wrapper(debug=True)
def cap():
    """simple captcha"""
    a, b = randint(1, 10), randint(1, 10)
    return (a, b, a + b)


@debug_wrapper(debug=True)
def check_cap(a, b, r, request):
    """simple captcha"""
    try:
        return bool((int(request.form[a]) + int(request.form[b])) == int(request.form[r]))
    except:
        return False



@debug_wrapper(debug=True)
def answer_yes_no(flag):
    """filter checker flag"""
    return u'Есть ответ' if flag else u'Нет ответа'



@debug_wrapper(debug=True)
def text_from_markdown(html_to_text):
    """clear text htmltags for edit in post example"""
    return ''.join(BeautifulSoup(html_to_text).findAll(text=True))


@debug_wrapper(debug=True)
def tags_split(post_tags):
    """tags spliter"""
    return map(string.strip, post_tags.split(','))


@debug_wrapper(debug=True)
def getfilelist(path=None):
    """get list all files in spec dir"""
    result = []
    for dir, sub, files in [x for x in os.walk(path if path else os.path.abspath(__file__)) if x]:
        if dir:
            for f in files:
                result.append('/'.join((dir, f)))
    return result


@debug_wrapper(debug=True)
def captcha(debug=False):
    """simple captcha"""
    a, b = (randint(1, 10), randint(1, 10))
    return a, b, a + b


@debug_wrapper(debug=True)
def allowed_file(filename, ext_list_file):
    """check filename for allowed set"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ext_list_file


########################################################
# some function for work in base64 [convert and more...]
########################################################

# конвертирует картинку в строку base64 формата для записи в базу данных
img_to_b64 = lambda (img): base64.encodestring(open(img, "rb").read())

# конвертирует строку base64 в картинку указанного имени файла
img_from_b64 = lambda (img64, img): open(img, "wb").write(base64.decodestring(img64))


def shop_pic_save(img, sizer=(250, 250)):
    """получает картинку с полным путем, изменяет ее размер на нужный по дефолту 250х250 пикселей,
    конвертирует измененую картинку в base64 и возвращает полученую строку. Переменый файл используемый
    при конвертации, удаляется"""
    p, f = os.path.split(img)
    if f:
        fname, ext = os.path.splitext(f)
    tmpimg = '/'.join([p, 'tmp' + f])
    Image.open(img).resize(sizer, Image.ANTIALIAS).save(tmpimg)
    b64 = img_to_b64(tmpimg)
    os.remove(tmpimg)
    add_for_img_src = ext and 'data:image/{};base64,'.format(ext[1:]) or 'data:image/{};base64,'.format('png')

    return add_for_img_src + b64

