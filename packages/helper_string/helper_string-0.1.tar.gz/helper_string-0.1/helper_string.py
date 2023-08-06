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