from cara import cara

# Forward declarations:
from cara.capnp import cxx_capnp
Node = cara.Struct(name="Node", id=0xe682ab4cf923a417)
Node.Parameter = cara.Struct(name="Parameter", id=0xb9521bccf10fa3b1)
Node.NestedNode = cara.Struct(name="NestedNode", id=0xdebf55bbfa0fc242)
Field = cara.Struct(name="Field", id=0x9aad50a41f4af45f)
Field.noDiscriminant = cara.Const(name="noDiscriminant", id=0x97b14cbe7cfec712)
Enumerant = cara.Struct(name="Enumerant", id=0x978a7cebdc549a4d)
Superclass = cara.Struct(name="Superclass", id=0xa9962a9ed0a4d7f8)
Method = cara.Struct(name="Method", id=0x9500cce23b334d80)
Type = cara.Struct(name="Type", id=0xd07378ede1f9cc60)
Brand = cara.Struct(name="Brand", id=0x903455f06065422b)
Brand.Scope = cara.Struct(name="Scope", id=0xabd73485a9636bc9)
Brand.Binding = cara.Struct(name="Binding", id=0xc863cd16969ee7fc)
Value = cara.Struct(name="Value", id=0xce23dcd2d7b00c9b)
Annotation = cara.Struct(name="Annotation", id=0xf1c8950dab257542)
ElementSize = cara.Enum(name="ElementSize", enumerants=[cara.Enumerant(name="empty", ordinal=0), cara.Enumerant(name="bit", ordinal=1), cara.Enumerant(name="byte", ordinal=2), cara.Enumerant(name="twoBytes", ordinal=3), cara.Enumerant(name="fourBytes", ordinal=4), cara.Enumerant(name="eightBytes", ordinal=5), cara.Enumerant(name="pointer", ordinal=6), cara.Enumerant(name="inlineComposite", ordinal=7)])
CodeGeneratorRequest = cara.Struct(name="CodeGeneratorRequest", id=0xbfc546f6210ad7ce)
CodeGeneratorRequest.RequestedFile = cara.Struct(name="RequestedFile", id=0xcfea0eb02e810062)
CodeGeneratorRequest.RequestedFile.Import = cara.Struct(name="Import", id=0xae504193122357e5)

# Finishing declarations:
Node.Parameter.FinishDeclaration(
    fields=[cara.Field(id=0, name="name", type=cara.Text)])
Node.NestedNode.FinishDeclaration(
    fields=[cara.Field(id=0, name="name", type=cara.Text), cara.Field(id=1, name="id", type=cara.Uint64)])
Node.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=6, name="file", type=cara.Void), cara.Group(id=7, name="struct", fields=[cara.Field(id=0, name="dataWordCount", type=cara.Uint16), cara.Field(id=1, name="pointerCount", type=cara.Uint16), cara.Field(id=2, name="preferredListEncoding", type=ElementSize), cara.Field(id=3, name="isGroup", type=cara.Bool), cara.Field(id=4, name="discriminantCount", type=cara.Uint16), cara.Field(id=5, name="discriminantOffset", type=cara.Uint32), cara.Field(id=6, name="fields", type=cara.List(Field))]), cara.Group(id=8, name="enum", fields=[cara.Field(id=0, name="enumerants", type=cara.List(Enumerant))]), cara.Group(id=9, name="interface", fields=[cara.Field(id=0, name="methods", type=cara.List(Method)), cara.Field(id=1, name="superclasses", type=cara.List(Superclass))]), cara.Group(id=10, name="const", fields=[cara.Field(id=0, name="type", type=Type), cara.Field(id=1, name="value", type=Value)]), cara.Group(id=11, name="annotation", fields=[cara.Field(id=0, name="type", type=Type), cara.Field(id=1, name="targetsFile", type=cara.Bool), cara.Field(id=2, name="targetsConst", type=cara.Bool), cara.Field(id=3, name="targetsEnum", type=cara.Bool), cara.Field(id=4, name="targetsEnumerant", type=cara.Bool), cara.Field(id=5, name="targetsStruct", type=cara.Bool), cara.Field(id=6, name="targetsField", type=cara.Bool), cara.Field(id=7, name="targetsUnion", type=cara.Bool), cara.Field(id=8, name="targetsGroup", type=cara.Bool), cara.Field(id=9, name="targetsInterface", type=cara.Bool), cara.Field(id=10, name="targetsMethod", type=cara.Bool), cara.Field(id=11, name="targetsParam", type=cara.Bool), cara.Field(id=12, name="targetsAnnotation", type=cara.Bool)])]), cara.Field(id=0, name="id", type=cara.Uint64), cara.Field(id=1, name="displayName", type=cara.Text), cara.Field(id=2, name="displayNamePrefixLength", type=cara.Uint32), cara.Field(id=3, name="scopeId", type=cara.Uint64), cara.Field(id=4, name="nestedNodes", type=cara.List(Node.NestedNode)), cara.Field(id=5, name="annotations", type=cara.List(Annotation)), cara.Field(id=12, name="parameters", type=cara.List(Node.Parameter)), cara.Field(id=13, name="isGeneric", type=cara.Bool)])
Field.noDiscriminant.FinishDeclaration(type=cara.Uint16, value=65535)
Field.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Group(id=4, name="slot", fields=[cara.Field(id=0, name="offset", type=cara.Uint32), cara.Field(id=1, name="type", type=Type), cara.Field(id=2, name="defaultValue", type=Value), cara.Field(id=3, name="hadExplicitDefault", type=cara.Bool)]), cara.Group(id=5, name="group", fields=[cara.Field(id=0, name="typeId", type=cara.Uint64)])]), cara.Field(id=0, name="name", type=cara.Text), cara.Field(id=1, name="codeOrder", type=cara.Uint16), cara.Field(id=2, name="annotations", type=cara.List(Annotation)), cara.Field(id=3, name="discriminantValue", default=65535, type=cara.Uint16), cara.Group(id=6, name="ordinal", fields=[cara.Union(fields=[cara.Field(id=0, name="implicit", type=cara.Void), cara.Field(id=1, name="explicit", type=cara.Uint16)])])])
Enumerant.FinishDeclaration(
    fields=[cara.Field(id=0, name="name", type=cara.Text), cara.Field(id=1, name="codeOrder", type=cara.Uint16), cara.Field(id=2, name="annotations", type=cara.List(Annotation))])
Superclass.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.Uint64), cara.Field(id=1, name="brand", type=Brand)])
Method.FinishDeclaration(
    fields=[cara.Field(id=0, name="name", type=cara.Text), cara.Field(id=1, name="codeOrder", type=cara.Uint16), cara.Field(id=2, name="paramStructType", type=cara.Uint64), cara.Field(id=3, name="resultStructType", type=cara.Uint64), cara.Field(id=4, name="annotations", type=cara.List(Annotation)), cara.Field(id=5, name="paramBrand", type=Brand), cara.Field(id=6, name="resultBrand", type=Brand), cara.Field(id=7, name="implicitParameters", type=cara.List(Node.Parameter))])
Type.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="void", type=cara.Void), cara.Field(id=1, name="bool", type=cara.Void), cara.Field(id=2, name="int8", type=cara.Void), cara.Field(id=3, name="int16", type=cara.Void), cara.Field(id=4, name="int32", type=cara.Void), cara.Field(id=5, name="int64", type=cara.Void), cara.Field(id=6, name="uint8", type=cara.Void), cara.Field(id=7, name="uint16", type=cara.Void), cara.Field(id=8, name="uint32", type=cara.Void), cara.Field(id=9, name="uint64", type=cara.Void), cara.Field(id=10, name="float32", type=cara.Void), cara.Field(id=11, name="float64", type=cara.Void), cara.Field(id=12, name="text", type=cara.Void), cara.Field(id=13, name="data", type=cara.Void), cara.Group(id=14, name="list", fields=[cara.Field(id=0, name="elementType", type=Type)]), cara.Group(id=15, name="enum", fields=[cara.Field(id=0, name="typeId", type=cara.Uint64), cara.Field(id=1, name="brand", type=Brand)]), cara.Group(id=16, name="struct", fields=[cara.Field(id=0, name="typeId", type=cara.Uint64), cara.Field(id=1, name="brand", type=Brand)]), cara.Group(id=17, name="interface", fields=[cara.Field(id=0, name="typeId", type=cara.Uint64), cara.Field(id=1, name="brand", type=Brand)]), cara.Group(id=18, name="anyPointer", fields=[cara.Union(fields=[cara.Field(id=0, name="unconstrained", type=cara.Void), cara.Group(id=1, name="parameter", fields=[cara.Field(id=0, name="scopeId", type=cara.Uint64), cara.Field(id=1, name="parameterIndex", type=cara.Uint16)]), cara.Group(id=2, name="implicitMethodParameter", fields=[cara.Field(id=0, name="parameterIndex", type=cara.Uint16)])])])])])
Brand.Scope.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=1, name="bind", type=cara.List(Brand.Binding)), cara.Field(id=2, name="inherit", type=cara.Void)]), cara.Field(id=0, name="scopeId", type=cara.Uint64)])
Brand.Binding.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="unbound", type=cara.Void), cara.Field(id=1, name="type", type=Type)])])
Brand.FinishDeclaration(
    fields=[cara.Field(id=0, name="scopes", type=cara.List(Brand.Scope))])
Value.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="void", type=cara.Void), cara.Field(id=1, name="bool", type=cara.Bool), cara.Field(id=2, name="int8", type=cara.Int8), cara.Field(id=3, name="int16", type=cara.Int16), cara.Field(id=4, name="int32", type=cara.Int32), cara.Field(id=5, name="int64", type=cara.Int64), cara.Field(id=6, name="uint8", type=cara.Uint8), cara.Field(id=7, name="uint16", type=cara.Uint16), cara.Field(id=8, name="uint32", type=cara.Uint32), cara.Field(id=9, name="uint64", type=cara.Uint64), cara.Field(id=10, name="float32", type=cara.Float32), cara.Field(id=11, name="float64", type=cara.Float64), cara.Field(id=12, name="text", type=cara.Text), cara.Field(id=13, name="data", type=cara.Data), cara.Field(id=14, name="list", type=cara.AnyPointer), cara.Field(id=15, name="enum", type=cara.Uint16), cara.Field(id=16, name="struct", type=cara.AnyPointer), cara.Field(id=17, name="interface", type=cara.Void), cara.Field(id=18, name="anyPointer", type=cara.AnyPointer)])])
Annotation.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.Uint64), cara.Field(id=1, name="value", type=Value), cara.Field(id=2, name="brand", type=Brand)])
ElementSize.FinishDeclaration(
    enumerants=[cara.Enumerant(name="empty", ordinal=0), cara.Enumerant(name="bit", ordinal=1), cara.Enumerant(name="byte", ordinal=2), cara.Enumerant(name="twoBytes", ordinal=3), cara.Enumerant(name="fourBytes", ordinal=4), cara.Enumerant(name="eightBytes", ordinal=5), cara.Enumerant(name="pointer", ordinal=6), cara.Enumerant(name="inlineComposite", ordinal=7)])
CodeGeneratorRequest.RequestedFile.Import.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.Uint64), cara.Field(id=1, name="name", type=cara.Text)])
CodeGeneratorRequest.RequestedFile.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.Uint64), cara.Field(id=1, name="filename", type=cara.Text), cara.Field(id=2, name="imports", type=cara.List(CodeGeneratorRequest.RequestedFile.Import))])
CodeGeneratorRequest.FinishDeclaration(
    fields=[cara.Field(id=0, name="nodes", type=cara.List(Node)), cara.Field(id=1, name="requestedFiles", type=cara.List(CodeGeneratorRequest.RequestedFile))])

__annotations__ = [cxx_capnp.namespace('capnp::schema')]
