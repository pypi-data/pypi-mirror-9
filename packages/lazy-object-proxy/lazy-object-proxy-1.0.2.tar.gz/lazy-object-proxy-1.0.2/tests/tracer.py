import sys
import os
import linecache

from lazy_object_proxy.slots import Proxy
from django.utils.functional import SimpleLazyObject

def dumbtrace(frame, event, args):
    sys.stdout.write("%015s:%-3s %06s %s" % (
        os.path.basename(frame.f_code.co_filename),
        frame.f_lineno,
        event,
        linecache.getline(frame.f_code.co_filename, frame.f_lineno)
    ))
    return dumbtrace


for Implementation in Proxy, SimpleLazyObject:
    print("Testing %s ..." % Implementation.__name__)
    obj = Implementation(lambda: 'foobar')
    str(obj)
    sys.settrace(dumbtrace)
    str(obj)
    sys.settrace(None)



