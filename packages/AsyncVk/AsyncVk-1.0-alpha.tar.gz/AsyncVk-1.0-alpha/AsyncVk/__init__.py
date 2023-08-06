from AsyncVk.api import APISession as API
from AsyncVk.api import VkError, VkAuthorizationError, VkAPIMethodError

from AsyncVk.mixins import EnterCaptchaMixin


class EnterCaptchaAPI(EnterCaptchaMixin, API):
    pass
