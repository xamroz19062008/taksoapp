from django.http import JsonResponse

class BlockOldAppVersionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.minimum_version = "1.2.0"  # Минимально допустимая версия

    def __call__(self, request):
        version = request.headers.get("App-Version")

        if version and self.is_version_outdated(version):
            return JsonResponse({
                "detail": "Iltimos, ilovani yangilang. Yangi versiya talab qilinadi.",
                "force_update": True
            }, status=426)  # 426 Upgrade Required

        return self.get_response(request)

    def is_version_outdated(self, version):
        def to_tuple(v):
            return tuple(map(int, (v.split("."))))
        try:
            return to_tuple(version) < to_tuple(self.minimum_version)
        except:
            return True  # Если версия указана неправильно — блокируем
