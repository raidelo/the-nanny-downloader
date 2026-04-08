from pathlib import Path


class DeliveryMethodNotFound(BaseException):
    def __init__(self, delivery_method: str, *args, **kwargs):
        self.delivery_method = delivery_method
        super().__init__(delivery_method, *args, **kwargs)


class ChapterNotFound(BaseException):
    def __init__(self, chapter: str, *args, **kwargs):
        self.chapter = chapter
        super().__init__(chapter, *args, **kwargs)


class InvalidChapterFormat(BaseException):
    def __init__(self, chapter: str, *args, **kwargs):
        self.chapter = chapter
        super().__init__(chapter, *args, **kwargs)


class InvalidTRIDMappingFileFormat(BaseException):
    def __init__(self, path: Path, *args, **kwargs):
        self.path = path
        super().__init__(path, *args, **kwargs)
