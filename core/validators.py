from django.core.exceptions import ValidationError


class FileSizeValidator:
    # 2.5MB - 2621440
    # 5MB - 5242880
    # 10MB - 10485760
    # 20MB - 20971520
    # 50MB - 52428800
    # 100MB 104857600
    # 250MB - 214958080
    # 500MB - 429916160 
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        filesize = value.size
        if filesize > self.max_size:
            raise ValidationError(f"File should be less than or equal to {self.max_size / (1024 * 1024)} MB")
        return value
