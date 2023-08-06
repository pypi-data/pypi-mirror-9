from cara import cara

# Forward declarations:
namespace = cara.Annotation(name="namespace", id=0xb9c6f99ebf805f2c, qualname="namespace.c++.capnp")
name = cara.Annotation(name="name", id=0xf264a779fef191ce, qualname="name.c++.capnp")

# Finishing declarations:
namespace.FinishDeclaration(type=cara.Text, applies_to=["file"])
name.FinishDeclaration(
    type=cara.Text, applies_to=["struct", "interface", "group", "enum", "field", "union", "group", "enumerant", "param", "method"])

__annotations__ = [namespace('capnp::annotations')]
