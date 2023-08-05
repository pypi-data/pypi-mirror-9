

class DatabaseAlias(str):
    config_prefix = 'database'

    @property
    def name(self):
        return self.split(':')[-1]

    @property
    def prefix(self):
        return self.split(':')[0]

    @classmethod
    def fromname(cls, name):
        if ':' in name:
            raise ValueError("Database alias names may not contain ':'")
        return cls(':'.join([cls.config_prefix, name]))
