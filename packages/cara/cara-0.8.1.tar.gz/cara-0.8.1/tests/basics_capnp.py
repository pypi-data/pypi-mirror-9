from cara import cara

# Forward declarations:
from cara.capnp import persistent_capnp
from cara.capnp import rpc_twoparty_capnp
from cara.capnp import rpc_capnp
from cara.capnp import schema_capnp
Basic = cara.Struct(name="Basic", id=0xda4526f9985b0c2b)
SemiAdvanced = cara.Struct(name="SemiAdvanced", id=0x88c872054893a170)
SimpleInterface = cara.Interface(name="SimpleInterface", id=0xf7e2531f951c57a0)

# Finishing declarations:
Basic.FinishDeclaration(
    fields=[cara.Field(id=0, name="field", type=cara.Int32), cara.Field(id=1, name="type", type=schema_capnp.Type), cara.Field(id=2, name="list", type=cara.List(Basic)), cara.Field(id=3, name="ints", type=cara.List(cara.Int32)), cara.Field(id=4, name="nested", type=Basic)])
SemiAdvanced.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=2, name="unnamed", type=cara.Int8), cara.Field(id=3, name="unionField", type=cara.Data)]), cara.Group(id=0, name="namedGroup", fields=[cara.Field(id=0, name="first", type=cara.Text)]), cara.Group(id=1, name="namedUnion", fields=[cara.Union(fields=[cara.Field(id=0, name="this", type=cara.Int32), cara.Field(id=1, name="that", type=cara.Int64)])])])
SimpleInterface.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="structOut", params=[cara.Param(id=0, name="input", type=cara.Int32)], results=Basic), cara.Method(id=1, name="structIn", params=Basic, results=[cara.Param(id=0, name="output", type=cara.Int32)]), cara.Method(id=2, name="multipleOut", params=[], results=[cara.Param(id=0, name="one", type=cara.Int32), cara.Param(id=1, name="two", type=cara.Int32)])])
