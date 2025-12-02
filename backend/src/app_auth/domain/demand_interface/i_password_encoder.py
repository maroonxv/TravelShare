

class IPasswordEncoder:
    def encode(self, password: str) -> str:
        pass
    
    def verify(self, password: str, password_hash: str) -> bool:
        pass