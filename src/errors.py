class InvalidDeliveryMethod(BaseException):
    def __init__(self, delivery_method: str, *args, **kwargs):
        self.delivery_method = delivery_method
        super().__init__(delivery_method, *args, **kwargs)


class InvalidChapter(BaseException):
    def __init__(self, chapter: str, *args, **kwargs):
        self.chapter = chapter
        super().__init__(chapter, *args, **kwargs)
