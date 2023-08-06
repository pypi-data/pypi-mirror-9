from cara import cara

# Forward declarations:
GenericStruct = cara.TemplatedStruct(name="GenericStruct", id=0xc28eb01bb298f405, templates=["T"])
GenericStruct.ann = cara.Annotation(name="ann", id=0xec21f3de00f5c11a)
GenericStruct.Nested = cara.TemplatedStruct(name="Nested", id=0xcd5f714f70e51b45, templates=["U"])
GenericStruct.Nongeneric = cara.Struct(name="Nongeneric", id=0xf26800c2a5ae21ce)
GenericIface = cara.TemplatedInterface(name="GenericIface", id=0xbf820f5543f82685, templates=["T"])
GenericIface.Nested = cara.TemplatedStruct(name="Nested", id=0xff0bcdfc110560cf, templates=["U"])
enumAnnotation = cara.Annotation(name="enumAnnotation", id=0xd80973714f063b6e)
BasicEnum = cara.Enum(name="BasicEnum", enumerants=[cara.Enumerant(name="first", ordinal=0), cara.Enumerant(name="second", ordinal=1)])
value = cara.Const(name="value", id=0xbee870091df820a2)

# Finishing declarations:
GenericStruct.ann.FinishDeclaration(
    type=GenericStruct.Template(0), applies_to=cara.Annotation.ALL)
GenericStruct.Nested.FinishDeclaration(
    fields=[cara.Field(id=0, name="first", type=GenericStruct[GenericStruct.Template(0)].Nested[GenericStruct.Template(0)]), cara.Field(id=1, name="second", type=GenericStruct[GenericStruct.Nested.Template(0)])])
GenericStruct.Nongeneric.FinishDeclaration(
    fields=[cara.Field(id=0, name="templated", type=GenericStruct.Template(0)), cara.Field(id=1, name="doubleTemplated", type=GenericStruct[cara.Text])])
GenericStruct.FinishDeclaration(
    fields=[cara.Field(id=0, name="field", type=GenericStruct[GenericStruct.Template(0)]), cara.Field(id=1, name="defaulted", default='defaulteds', type=cara.Text), cara.Field(id=2, name="list", type=cara.List(GenericStruct[GenericStruct.Template(0)]))])
GenericIface.Nested.FinishDeclaration(
    fields=[cara.Field(id=0, name="field", type=GenericStruct.Nested[GenericIface.Template(0)])])
GenericIface.FinishDeclaration(
    superclasses=[], methods=[cara.TemplatedMethod(id=0, name="templated", templates=["X"], params=[cara.Param(id=0, name="in", type=GenericIface.Template(0))], results=[cara.Param(id=0, name="out", type=cara.MethodTemplate(0))]), cara.Method(id=1, name="normal", params=[cara.Param(id=0, name="in", type=GenericIface.Template(0))], results=[cara.Param(id=0, name="out", type=GenericIface.Template(0))])])
enumAnnotation.FinishDeclaration(type=cara.Int32, applies_to=["enumerant"])
BasicEnum.FinishDeclaration(
    enumerants=[cara.Enumerant(name="first", ordinal=0, annotations=[enumAnnotation(3)]), cara.Enumerant(name="second", ordinal=1)])
value.FinishDeclaration(
    type=cara.Int8, value=0, annotations=[GenericStruct[cara.Text].ann('ann')])
