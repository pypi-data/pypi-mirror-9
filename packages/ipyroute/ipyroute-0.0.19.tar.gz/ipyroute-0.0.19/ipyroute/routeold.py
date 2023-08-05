
class Nexthop(Base):
    regex = re.compile(r'nexthop via (?P<addr>\S+)\s+'
                       r'dev (?P<dev>\S+) '
                       r'weight (?P<weight>\d+)')
    casts = dict(addr=IPAddress)

class Route(Base):
    regex = re.compile(r'(?P<network>\S+)\s+'
                       r'(dev (?P<dev>\S+)\s*)?'
                       r'(proto (?P<proto>\S+)\s*)?'
                       r'(src (?P<src>\S+)\s*)?'
                       r'(metric (?P<metric>\d+)\s*)?'
                       r'(mtu (?P<mtu>\d+)\s*)?'
                       r'(advmss (?P<advmss>\d+)\s*)?')

    casts = dict(network=IPNetwork,
                 src=IPAddress,
                 metric=int,
                 mtu=int,
                 advmss=int)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        if self.network == 'default':
            self.network = '0.0.0.0/0'
        self.network = IPNetwork(self.network)
        if self.src is not None:
            self.src = IPAddress(self.src)
        # cast fields to int
        for field in ('metric', 'mtu', 'advmss'):
            if getattr(self, field) is not None:
                setattr(self, field, int(getattr(self, field)))

    @classmethod
    def _get(cls, *args):
        for line in IPR.ipv4.route.show(*args):
            yield line
        for line in IPR.ipv6.route.show(*args):
            yield line

    @classmethod
    def from_string(cls, ipstr):
        match = cls.regex.match(ipstr)
        if not match:
            raise Exception
        result = match.groupdict()
        nhops = Nexthop.regex.finditer(ipstr)
        result['nexthops'] = [Nexthop(**n.groupdict()) for n in nhops]
        return cls(**result)
