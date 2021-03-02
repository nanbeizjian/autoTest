from configparser import ConfigParser


class MyConf:

    def __init__(self, filename, encoding="utf8"):
        self.filename = filename
        self.encoding = encoding
        self.conf = ConfigParser()
        self.conf.read(filename, encoding)

    def get_str(self, section, option):
        return self.conf.get(section, option)

    def get_int(self, section, option):
        return self.conf.getint(section, option)

    def get_float(self, section, option):
        return self.conf.getfloat(section, option)

    def get_bool(self, section, option):
        pass

    def write_data(self, section, option, value):
        self.conf.set(section, option, value)


if __name__ == '__main__':
    conf=MyConf('config.ini')
    print(conf.get_str( "test", "name"))
