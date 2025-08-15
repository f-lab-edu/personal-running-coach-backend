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