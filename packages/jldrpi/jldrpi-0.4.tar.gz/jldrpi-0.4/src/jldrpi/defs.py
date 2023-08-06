'''
    Created on Mar 8, 2015
    @author: jldupont
'''

class Pin(object):
    
    PULL_UP = 'u'
    PULL_DOWN = 'd'
    EDGE_RISING = 'r'
    EDGE_FALLING = 'f'
    
    def __init__(self, pin_number, pull, edge):
        
        self.pin_number = pin_number
        self.pull = pull
        self.edge = edge
        
    @classmethod
    def parse_and_validate(cls, pin_number, props):
        
        pd = cls.PULL_DOWN in props
        pu = cls.PULL_UP in props
        
        if pd and pu:
            raise Exception("Either pull-up or pull-down, not both")
        
        er = cls.EDGE_RISING in props
        ef = cls.EDGE_FALLING in props
        
        if er and ef:
            raise Exception("Either rising edge or falling edge, not both")
    
        pull = pd and cls.PULL_DOWN   or pu and cls.PULL_UP
        edge = er and cls.EDGE_RISING or ef and cls.EDGE_FALLING
        
        return (pin_number, pull, edge)

