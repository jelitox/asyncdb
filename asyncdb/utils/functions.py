""" asyncDB utils.
Various functions for asyncdb
"""
import os
import binascii
import hashlib
import time
import datetime
from datetime import timedelta
from datetime import date
import dateutil.parser
from dateutil import parser
from dateutil.relativedelta import relativedelta
from typing import Callable
import builtins
import redis
import dateparser
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pytz

CACHE_HOST = os.getenv("CACHEHOST", default="localhost")
CACHE_PORT = os.getenv("CACHEPORT", default=6379)
CACHE_URL = "redis://{}:{}".format(CACHE_HOST, CACHE_PORT)
CACHE_DB = os.getenv("QUERYSET_DB", default=0)
QUERY_VARIABLES = f"redis://{CACHE_HOST}:{CACHE_PORT}/{CACHE_DB}"

CACHEDB = redis.StrictRedis.from_url(QUERY_VARIABLES)


class SafeDict(dict):
    """
    SafeDict.

    Allow to using partial format strings

    """

    def __missing__(self, key):
        """Missing method for SafeDict."""
        return "{" + key + "}"


def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


# hash utilities
def get_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def truncate_decimal(value):
    head, sep, tail = value.partition(".")
    return head


"""
Date-time Functions
"""
# date utilities
def current_year():
    return datetime.datetime.now().year


def current_month():
    return datetime.datetime.now().month


def today(mask="%m/%d/%Y"):
    return time.strftime(mask)


def get_current_date():
    return datetime.utcnow().date()


def a_visit():
    return timezone.now() + timezone.timedelta(minutes=30)


def due_date():
    return timezone.now() + timezone.timedelta(days=1)


def year(value):
    if value:
        try:
            newdate = dateutil.parser.parse(value)
            # dt = datetime.datetime.strptime(newdate.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            return newdate.date().year
        except ValueError:
            dt = value[:-4]
            dt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            return dt.date().year
    else:
        return None


def get_last_week_date(mask="%Y-%m-%d"):
    today = date.today()
    offset = (today.weekday() - 5) % 7
    last_saturday = today - timedelta(days=offset)
    return last_saturday.strftime(mask)


def month(value):
    if value:
        try:
            newdate = dateutil.parser.parse(value)
            return newdate.date().month
        except ValueError:
            dt = value[:-4]
            dt = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            return dt.date().month
    else:
        return None


def fdom():
    return (datetime.datetime.now()).strftime("%Y-%m-01")


def ldom():
    return (datetime.datetime.now() + relativedelta(day=31)).strftime("%Y-%m-%d")


def now():
    return datetime.datetime.now()


def due_date(days=1):
    return datetime.datetime.now() + timedelta(days=days)


def yesterday():
    return (datetime.datetime.now() - timedelta(1)).strftime("%Y-%m-%d")


def isdate(value):
    try:
        parser.parse(value)
        return True
    except ValueError:
        return False


is_date = isdate


def first_dow(mask="%Y-%m-%d"):
    today = datetime.datetime.now()
    fdow = today - timedelta(today.weekday())
    return fdow.strftime(mask)


def midnight_yesterday(mask="%m/%d/%Y"):
    midnight = datetime.datetime.combine(
        datetime.datetime.now() - timedelta(1), datetime.datetime.min.time()
    )
    return midnight.strftime(mask)


def to_midnight(value, mask="%Y-%m-%d"):
    midnight = datetime.datetime.combine(
        (value + timedelta(1)), datetime.datetime.min.time()
    )
    return midnight.strftime(mask)


"""
Formatting Functions
"""


def format_date(value="2019-01-01", mask="%Y-%m-%d %H:%M:%S"):
    """
    format_date.

        Convert an string into date an return with other format
    """
    if isinstance(value, datetime.datetime):
        return value.strftime(mask)
    else:
        try:
            d = datetime.datetime.strptime(str(value), "%Y-%m-%d")
            print(d)
            return d.strftime(mask)
        except (TypeError, ValueError) as err:
            print(err)
            raise ValueError(err)
            return None


def to_date(value, mask="%Y-%m-%d %H:%M:%S", tz=None):
    if isinstance(value, datetime.datetime):
        # print('to_date 1', value)
        return value
    else:
        try:
            result = datetime.datetime.strptime(str(value), mask)
            if tz is not None:
                result = result.replace(tzinfo=pytz.timezone(tz))
            # print('to_date 2', value, result)
            return result
        except Exception:
            # print('to_date 3', 'dateparser')
            return dateparser.parse(str(value), languages=["en", "es"])


def to_time(value, mask="%H:%M:%S"):
    if value == 0:
        return datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    if isinstance(value, datetime.datetime):
        return value
    else:
        if len(str(value)) < 6:
            value = str(value).zfill(6)
        try:
            return datetime.datetime.strptime(str(value), mask)
        except ValueError:
            return datetime.datetime.strptime(str(value), "%H:%M:%S")


def build_date(value, mask="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, list):
        dt = to_date(value[0], mask=mask[0])
        mt = to_time(value[1], mask=mask[1]).time()
        return datetime.datetime.combine(dt, mt)
    elif isinstance(value, datetime.datetime):
        return value
    else:
        if value == 0:
            return datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            return datetime.datetime.strptime(str(value), mask)


def epoch_to_date(value):
    if value:
        s, ms = divmod(value, 1000.0)
        return datetime.datetime.fromtimestamp(s, pytz.utc)
    else:
        return None


def trim(value):
    if isinstance(value, str):
        return value.strip()
    else:
        return value


def extract_string(value, exp=r"_((\d+)_(\d+))_", group=1, parsedate=False):
    match = re.search(r"{}".format(exp), value)
    if match:
        result = (
            match.group(group)
            if not parsedate
            else dateparser.parse(match.group(group))
        )
        return result


"""
Validation and data-type functions
"""


def isdate(value):
    try:
        parser.parse(value)
        return True
    except ValueError:
        return False


def isinteger(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def isnumber(value):
    try:
        complex(value)  # for int, long, float and complex
    except ValueError:
        return False
    return True


def is_string(value):
    if type(value) is str:
        return True
    else:
        return False


def is_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def plain_uuid(obj):
    return str(obj).replace("-", "")


def validate_type_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        pass


def is_boolean(value):
    if isinstance(value, bool):
        return True
    elif value == "null" or value == "NULL":
        return True
    elif value == "true" or value == "TRUE":
        return True
    else:
        return False


def to_boolean(value):
    if isinstance(value, bool):
        return value
    elif value == None:
        return False
    elif value == "null" or value == "NULL":
        return False
    elif value == "true" or value == "TRUE" or value == "True":
        return True
    elif value == "false" or value == "FALSE":
        return False
    else:
        return bool(value)


def to_double(value):
    if isinstance(value, int):
        return float(value)
    elif "," in value:
        val = value.replace(",", ".")
    else:
        val = value
    try:
        return float(val)
    except (ValueError, TypeError) as err:
        print(err)
        try:
            return Decimal(val)
        except Exception as e:
            print(e)
            return None


"""
"""
PG_CONSTANTS = ["CURRENT_DATE", "CURRENT_TIMESTAMP"]


def is_pgconstant(value):
    return value in PG_CONSTANTS


UDF = ["CURRENT_YEAR", "CURRENT_MONTH", "TODAY", "YESTERDAY", "FDOM", "LDOM"]


def is_udf(value: str, *args, **kwargs) -> Callable:
    fn = None
    try:
        f = value.lower()
        if value in UDF:
            fn = globals()[f](*args, **kwargs)
        else:
            func = globals()[f]
            if not func:
                try:
                    func = getattr(builtins, f)
                except AttributeError:
                    return None
            if func and callable(func):
                try:
                    fn = func(*args, **kwargs)
                except Exception as err:
                    raise Exception(err)
    finally:
        return fn


"""
Redis Functions
"""


def is_program_date(value, *args):
    try:
        if CACHEDB.exists(value):
            return True
        else:
            return False
    except Exception:
        return False


def get_program_date(value, yesterday: bool = False, *args):
    opt = None
    try:
        if CACHEDB.exists(value):
            result = CACHEDB.get(value)
            if result:
                opt = str(result.decode("utf-8"))
    finally:
        if not opt and yesterday:
            return yesterday()
        else:
            return opt