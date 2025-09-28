class CustomError(Exception):
    status_code: int = 500
    detail: str = "Internal Server Error"
    context: str = ""

    def __init__(self, detail: str = None, status_code: int = None, 
                 original_exception: Exception = None, context:str=None):
        if detail:
            self.detail = detail
        if status_code:
            self.status_code = status_code
        self.original_exception = original_exception
        self.context = context if context else detail
        super().__init__(self.detail)

    
class TokenExpiredError(CustomError):
    status_code = 401
        
class TokenInvalidError(CustomError):
    status_code = 401

class NotModifiedError(CustomError):
    status_code = 304
    

class DBError(CustomError):
    pass

class InternalError(CustomError):
    pass

class NotFoundError(CustomError):
    status_code = 404

class ValidationError(CustomError):
    status_code = 400
