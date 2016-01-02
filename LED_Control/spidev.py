# dummy so can test on machine without a spi
class SpiDev():
    
    bits_per_word = None
    cshigh = None
    loop = None
    lsbfirst = None
    max_speed_hz = None
    mode = None
    threewire = None

    def open(self, a, b):
        pass
    def xfer2(self, a):
        print a

