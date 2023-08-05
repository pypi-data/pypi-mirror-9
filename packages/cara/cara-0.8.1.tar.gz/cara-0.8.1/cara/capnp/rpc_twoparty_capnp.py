from cara import cara

# Forward declarations:
from cara.capnp import cxx_capnp
Side = cara.Enum(name="Side", enumerants=[cara.Enumerant(name="server", ordinal=0), cara.Enumerant(name="client", ordinal=1)])
VatId = cara.Struct(name="VatId", id=0xd20b909fee733a8e)
ProvisionId = cara.Struct(name="ProvisionId", id=0xb88d09a9c5f39817)
RecipientId = cara.Struct(name="RecipientId", id=0x89f389b6fd4082c1)
ThirdPartyCapId = cara.Struct(name="ThirdPartyCapId", id=0xb47f4979672cb59d)
JoinKeyPart = cara.Struct(name="JoinKeyPart", id=0x95b29059097fca83)
JoinResult = cara.Struct(name="JoinResult", id=0x9d263a3630b7ebee)

# Finishing declarations:
Side.FinishDeclaration(
    enumerants=[cara.Enumerant(name="server", ordinal=0), cara.Enumerant(name="client", ordinal=1)])
VatId.FinishDeclaration(fields=[cara.Field(id=0, name="side", type=Side)])
ProvisionId.FinishDeclaration(
    fields=[cara.Field(id=0, name="joinId", type=cara.Uint32)])
RecipientId.FinishDeclaration(fields=[])
ThirdPartyCapId.FinishDeclaration(fields=[])
JoinKeyPart.FinishDeclaration(
    fields=[cara.Field(id=0, name="joinId", type=cara.Uint32), cara.Field(id=1, name="partCount", type=cara.Uint16), cara.Field(id=2, name="partNum", type=cara.Uint16)])
JoinResult.FinishDeclaration(
    fields=[cara.Field(id=0, name="joinId", type=cara.Uint32), cara.Field(id=1, name="succeeded", type=cara.Bool), cara.Field(id=2, name="cap", type=cara.AnyPointer)])

__annotations__ = [cxx_capnp.namespace('capnp::rpc::twoparty')]
