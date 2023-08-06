from cara import cara

# Forward declarations:
FooIface = cara.Interface(name="FooIface", id=0xeeca3ba9835a9a0d)
BarIface = cara.Interface(name="BarIface", id=0xd63f1d7e6494a052)
BazIface = cara.Interface(name="BazIface", id=0xf7aafa416ba1c7cf)
ThreeIface = cara.Interface(name="ThreeIface", id=0xf90734ca6579a203)
ThreeIface.Simple = cara.Interface(name="Simple", id=0x99fad0b689a011e0)
Super = cara.Interface(name="Super", id=0x8eba26837f31aad3)
Inherit = cara.Interface(name="Inherit", id=0xc1e5b0041eb80410)
InheritAcceptor = cara.Interface(name="InheritAcceptor", id=0xf58a805436827b56)

# Finishing declarations:
FooIface.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="callback", params=[cara.Param(id=0, name="foo", type=FooIface)], results=[])])
BarIface.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="returnCb", params=[], results=[cara.Param(id=0, name="cb", type=BazIface)])])
BazIface.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="call", params=[cara.Param(id=0, name="is_called", type=cara.Bool)], results=[])])
ThreeIface.Simple.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="normalMethod", params=[cara.Param(id=0, name="input", type=cara.Text)], results=[cara.Param(id=0, name="output", type=cara.Text)])])
ThreeIface.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="returnIface", params=[], results=[cara.Param(id=0, name="return", type=ThreeIface.Simple)]), cara.Method(id=1, name="acceptIface", params=[cara.Param(id=0, name="accept", type=ThreeIface.Simple)], results=[])])
Super.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="superMethod", params=[], results=[]), cara.Method(id=1, name="overlapped", params=[], results=[]), cara.Method(id=2, name="second", params=[], results=[])])
Inherit.FinishDeclaration(
    superclasses=[Super], methods=[cara.Method(id=0, name="inheritedMethod", params=[], results=[]), cara.Method(id=1, name="third", params=[], results=[]), cara.Method(id=2, name="overlapped", params=[], results=[])])
InheritAcceptor.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="accept", params=[cara.Param(id=0, name="iface", type=Inherit)], results=[])])
