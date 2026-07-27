class MemAPIException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {"detail": self.detail, "status_code": self.status_code}
