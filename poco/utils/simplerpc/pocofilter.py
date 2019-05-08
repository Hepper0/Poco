import threading

local = threading.local()

# class PocoFilter(object):
#
#     NodeType=None
#     SubType= "*"
#     Condition={}
#
#
# def init_filter():
#     PocoFilter.NodeType = None
#     PocoFilter.SubType = "*"
#     PocoFilter.Condition = {}

class PocoFilter(object):
    def __init__(self):
        self.NodeType = None
        self.SubType = "*"
        self.Condition = {}

