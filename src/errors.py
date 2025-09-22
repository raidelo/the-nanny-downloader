class InvalidDeliveryMethod(BaseException):
    def __init__(self, delivery_method: str, *args, **kwargs):
        super().__init__(delivery_method, *args, **kwargs)


class InvalidChapter(BaseException):
    def __init__(self, chapter: str, *args, **kwargs):
        super().__init__(chapter, *args, **kwargs)
