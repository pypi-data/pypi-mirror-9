import datetime

class HelperString(object):
    @staticmethod
    def to_uni(obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return obj.decode('gbk')
        elif isinstance(obj, (int, long)):
            return unicode(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        else:
            return obj

    @staticmethod
    def to_str(obj):
        if isinstance(obj, unicode):
            return obj.encode('utf-8')
        else:
            return obj

    @staticmethod
    def shorten(s, placeholder=u'...', max_legnth=64):
        if len(s) > len(placeholder) and len(s) > max_legnth:
            return s[:max_legnth-3] + placeholder + s[-len(placeholder):]
        return s

    @staticmethod
    def shorten_filename(filename, placeholder=u'...', max_length=64):
        filename = HelperString.to_uni(filename)

        if len(filename) > len(placeholder) and len(filename) > max_length:
            fn, ext = os.path.splitext(filename)
            shorten = fn[:max_length-len(placeholder)] + placeholder + fn[-len(placeholder):] + ext
        else:
            shorten = filename
        return shorten
