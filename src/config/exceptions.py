class TokenError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        
    def __str__(self):
        return f"{self.status_code}. {self.detail}"
    
class TokenExpiredError(TokenError):
    def __init__(self, status_code, detail):
        super().__init__(status_code, detail)
        
class TokenInvalidError(TokenError):
    def __init__(self, status_code, detail):
        super().__init__(status_code, detail)
    