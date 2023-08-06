
class ID:
  VENDOR  = 0x0a21
  PRODUCT = 0x8001

import usb.core
import usb.util
def scan ( ):
  dev = usb.core.find(idVendor=ID.VENDOR)
  return dev

class UsbLink (object):
  def __init__(self, dev):
    self.dev = dev
  def configure (self):
    if self.dev:
      cfg =  self.dev.get_active_configuration( )
      self.interface = cfg[(0,0)]
      ep = usb.util.find_descriptor(self.interface)
      self.ep = ep
      if self.dev.is_kernel_driver_active(self.interface):
        self.dev.detach_kernel_driver(self.interface)
      usb.util.claim_interface(self.dev, self.interface)
  def close (self):
    usb.util.dispose_resources(self.dev)
    self.dev.attach_kernel_driver(self.interface)
  def read (self, n):
    return bytearray(self.ep.read(n))
  def write (self, msg):
    return self.ep.write(msg)

if __name__ == '__main__':
  dev = scan( )
  link = UsbLink(dev)
  link.configure( )
  link.close( )

