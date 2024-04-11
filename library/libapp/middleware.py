from typing import Any


class LibraryMiddleware:
    # in this function we can perfom initialization task
    def __init__(self,get_respone):
        print("Middleware Initialized !!")
        self.get_response = get_respone

    # this function is called for each request
    def __call__(self,request):
        # Code to be executed before view is called
        response = self.get_response(request)
        # Code to be executed after view is called
        return response
