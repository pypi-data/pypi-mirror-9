from cara import cara

# Forward declarations:
Root = cara.Struct(name="Root", id=0xc54ab961578fcb62)
Root.SubType1 = cara.Struct(name="SubType1", id=0xc42609b5a4b3e6cd)
Root.Host = cara.Struct(name="Host", id=0xaaccf12b1f9b52aa)

# Finishing declarations:
Root.SubType1.FinishDeclaration(
    fields=[cara.Field(id=0, name="subField", type=Root.Host), cara.Field(id=1, name="recurse", type=Root)])
Root.Host.FinishDeclaration(
    fields=[cara.Field(id=0, name="hostname", type=cara.Text), cara.Field(id=1, name="port", type=cara.Int16)])
Root.FinishDeclaration(
    fields=[cara.Field(id=0, name="field", type=Root.SubType1)])
