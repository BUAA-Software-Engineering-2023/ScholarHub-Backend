import re
from django.core.exceptions import ValidationError

class PasswordCharacterValidator:
    """
    验证密码是否至少包含大小写字母、数字、特殊字符中的若干种
    """

    DEFAULT_SPECIAL_CHARACTERS = ('!', '@' , '#', '$', '%', '&', '*', '_', '-', '.', '?')

    def __init__(self, min_count=2, special_characters=DEFAULT_SPECIAL_CHARACTERS):
        self.min_count = min_count
        self.special_characters = special_characters

    def validate(self, password, user=None):
        count = 0
        if re.search('[a-z]', password):
            count += 1
        if re.search('[A-Z]', password):
            count += 1
        if re.search('[0-9]', password):
            count += 1
        for ch in self.special_characters:
            if ch in password:
                count += 1

        if count < self.min_count:
            raise ValidationError(
                f"密码中必须至少包含大小写字母、数字及特殊字符"
                f"{''.join(self.special_characters)}中的{self.min_count}种",
                code="password_character_category_single",
            )