from cara import cara

# Forward declarations:
namespace = cara.Annotation(name="namespace", id=0xb9c6f99ebf805f2c)
name = cara.Annotation(name="name", id=0xf264a779fef191ce)

# Finishing declarations:
namespace.FinishDeclaration(type=cara.Text, applies_to=["file"])
name.FinishDeclaration(
    type=cara.Text, applies_to=["struct", "interface", "group", "enum", "field", "union", "group", "enumerant", "param", "method"])

__annotations__ = [namespace('capnp::annotations')]
