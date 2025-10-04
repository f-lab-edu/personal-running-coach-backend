class CustomError(Exception):
    """
    detail = 클라이언트 오류 메세지용
    context = 내부 로깅용
    """
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

    def __str__(self):
        return f"{self.status_code}: {self.context}"

    
class TokenExpiredError(CustomError):
    status_code = 401
    detail = "Token has expired"
        
class TokenInvalidError(CustomError):
    status_code = 401
    detail = "Invalid Token"

class NotModifiedError(CustomError):
    status_code = 304
    detail = "resource has not been modified"
    

class DBError(CustomError):
    pass

class InternalError(CustomError):
    pass

class NotFoundError(CustomError):
    status_code = 404
    detail="resource coult not be found"

class ValidationError(CustomError):
    status_code = 400
    detail = "invalid request"
