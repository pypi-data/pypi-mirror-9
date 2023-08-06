import bbio

class Nokia5110(object):
  def __init__(self, cs_pin, spi_port, sce_pin, dc_pin, rst_pin):
    self.spi_port = spi_port
    self.sce_pin = sce_pin
    self.dc_pin = dc_pin
    self.rst_pin = rst_pin
    for pin in (sce_pin, dc_pin, rst_pin):
      bbio.pinMode(pin, bbio.OUTPUT)
      bbio.digitalWrite(pin, bbio.HIGH)
    