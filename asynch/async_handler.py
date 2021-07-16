"""this module is the heart for asynchronous logging and audit"""
import concurrent.futures

class AsyncExecutors:
    """Singleton class to manage concurrent thread generation"""
    class __impl:
        """impl class for AsyncExecutors"""
        def __init__(self):
            self.audit_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            self.logger_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        def get_audit_executor(self):
            """returns auditing thread"""
            return self.audit_executor
        def get_logger_executor(self):
            """returns logger_executer"""
            return self.logger_executor

    instance = None

    def __new__(cls):
        if not AsyncExecutors.instance:
            AsyncExecutors.instance = AsyncExecutors.__impl()
        return AsyncExecutors.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
