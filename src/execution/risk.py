class RateLimiter:
    def __init__(self, max_submissions: int):
        self.max_submissions = max_submissions
        self.count = 0

    def allow(self) -> bool:
        self.count += 1
        return self.count <= self.max_submissions
