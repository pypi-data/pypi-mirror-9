from pyethereum import tester as t
s = t.state()
c = s.contract('examples/returnten.se')
t.enable_logging()
print s.send(t.k0, c, 0, [])
s.block.set_code(c, '600a6014601e828183020160005460206000f2505050'.decode('hex'))
print s.send(t.k0, c, 0, [])
