import re


class DomoticzVersion:

    pattern = re.compile(r'^\s*(\d+)\.(\d+)(\s*Beta)?\s*$')

    def __init__(self, year, minor, is_beta=False):
        self.year = year
        self.minor = minor
        self.is_beta = is_beta

    @staticmethod
    def try_parse(version_str):
        match = DomoticzVersion.pattern.match(version_str)
        if not match:
            return False, None

        year = int(match.group(1))
        minor = int(match.group(2))
        is_beta = match.group(3) is not None
        return True, DomoticzVersion(year, minor, is_beta)

    def __lt__(self, other):
        if self.year != other.year:
            return self.year < other.year
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.is_beta and not other.is_beta

    def __eq__(self, other):
        return (self.year == other.year and
                self.minor == other.minor and
                self.is_beta == other.is_beta)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not (self < other or self == other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __str__(self):
        return f"{self.year}.{self.minor}" + (" Beta" if self.is_beta else "")

    def __repr__(self):
        return f"DomoticzVersion('{self}')"
