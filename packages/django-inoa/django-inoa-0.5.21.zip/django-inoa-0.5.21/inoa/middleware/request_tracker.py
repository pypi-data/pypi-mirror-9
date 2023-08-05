# -*- coding: utf-8 -*-
import threading


class RequestTrackerMiddleware:
    """
    Makes the current thread's last processed request accessible anywhere
    in the code through the get_request() method.
    """
    def __init__(self):
        if 'inoa_tracker_thread_local' not in __builtins__:
            __builtins__['inoa_tracker_thread_local'] = threading.local()

    def process_request(self, request):
        __builtins__['inoa_tracker_thread_local'].request = request

    def process_response(self, request, response):
        __builtins__['inoa_tracker_thread_local'].request = None
        return response

    @staticmethod
    def get_request():
        try:
            return __builtins__['inoa_tracker_thread_local'].request
        except:
            return None

    @staticmethod
    def get_user():
        try:
            return __builtins__['inoa_tracker_thread_local'].request.user
        except:
            return None
