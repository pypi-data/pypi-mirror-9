# -*- coding: utf-8 -*-
# pylint: disable=C0301,W0105,W0401,W0614

import struct


# pylint: disable=C0103
struct_B = struct.Struct('<B')
struct_BB = struct.Struct('<BB')
struct_BBB = struct.Struct('<BBB')
struct_BBBB = struct.Struct('<BBBB')
struct_BBBBB = struct.Struct('<BBBBB')
struct_BL = struct.Struct("<BL")
struct_LB = struct.Struct("<LB")
struct_L = struct.Struct("<L")
struct_LL = struct.Struct("<LL")
struct_LLL = struct.Struct("<LLL")
struct_LLLL = struct.Struct("<LLLL")
struct_LLLLL = struct.Struct("<LLLLL")
struct_Q = struct.Struct("<Q")
struct_BQ = struct.Struct("<BQ")


REQUEST_TYPE_INSERT = 13
REQUEST_TYPE_SELECT = 17
REQUEST_TYPE_UPDATE = 19
REQUEST_TYPE_DELETE = 21
REQUEST_TYPE_CALL = 22
REQUEST_TYPE_PING = 65280

BOX_RETURN_TUPLE = 1
BOX_ADD = 2
BOX_REPLACE = 4


UPDATE_OPERATION_CODE = {
    0       : (0, 3),
    '='     : (0, 3),
    'assign': (0, 3),
    1       : (1, 3),
    '+'     : (1, 3),
    'add'   : (1, 3),
    2       : (2, 3),
    '&'     : (2, 3),
    'and'   : (2, 3),
    3       : (3, 3),
    '^'     : (3, 3),
    'xor'   : (3, 3),
    4       : (4, 3),
    '|'     : (4, 3),
    'or'    : (4, 3),
    5       : (5, 5),
    ':'     : (5, 5),
    'splice': (5, 5),
    6       : (6, 2),
    'del'   : (6, 2),
    'delete': (6, 2),
    7       : (7, 3),
    'ins'   : (7, 3),
    'insert': (7, 3),
}

# Default value for socket timeout (seconds)
SOCKET_TIMEOUT = None
# Default maximum number of attempts to reconnect
RECONNECT_MAX_ATTEMPTS = 10
# Default delay between attempts to reconnect (seconds)
RECONNECT_DELAY = 0.1
# Number of reattempts in case of server
# return completion_status == 1 (try again)
RETRY_MAX_ATTEMPTS = 10
