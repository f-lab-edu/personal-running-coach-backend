class TokenError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        
    def __str__(self):
        return f"{self.status_code}. {self.detail}"
    
class TokenExpiredError(TokenError):
    pass
        
class TokenInvalidError(TokenError):
    def __init__(self, status_code, detail, token_type=None):
        super().__init__(status_code, detail)
        self.token_type = token_type
        
    def __str__(self):
        return f"[{self.token_type}] {self.status_code}. {self.detail}"
    

class DBError(Exception):
    """
    DB 레이어에서 발생하는 모든 에러의 공통 커스텀 예외.
    """
    def __init__(self, message: str, original_exception: Exception = None):
        self.status_code = 500
        self.message = message
        self.original_exception = original_exception
        super().__init__(message)


        
class InternalError(Exception):
    def __init__(self, message: str = "Internal Server Error", exception: Exception = None):
        self.status_code = 500
        self.message = message
        self.original_exception = exception
        super().__init__(message)


class AdapterError(Exception):
    """어댑터 계층의 모든 예외 기본 클래스"""
    def __init__(self, message: str, exception:Exception=None):
        self.message = message
        self.original_exception = exception
        super().__init__(message)

class AdapterNotFoundError(AdapterError):
    status_code = 404

class AdapterValidationError(AdapterError):
    status_code = 400
