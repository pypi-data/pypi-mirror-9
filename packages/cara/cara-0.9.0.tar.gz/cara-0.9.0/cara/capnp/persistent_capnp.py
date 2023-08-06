from cara import cara

# Forward declarations:
from cara.capnp import cxx_capnp
Persistent = cara.TemplatedInterface(name="Persistent", id=0xc8cb212fcd9f5691, templates=["SturdyRef"])
Persistent.SaveParams = cara.Struct(name="SaveParams", id=0xf76fba59183073a5)
Persistent.SaveResults = cara.Struct(name="SaveResults", id=0xb76848c18c40efbf)
RealmGateway = cara.TemplatedInterface(name="RealmGateway", id=0x84ff286cd00a3ed4, templates=["InternalRef", "ExternalRef"])

# Finishing declarations:
Persistent.SaveParams.FinishDeclaration(fields=[])
Persistent.SaveResults.FinishDeclaration(
    fields=[cara.Field(id=0, name="sturdyRef", type=Persistent.Template(0))])
Persistent.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="save", params=Persistent.SaveParams, results=Persistent.SaveResults)])
RealmGateway.FinishDeclaration(
    superclasses=[], methods=[cara.Method(id=0, name="import", params=[cara.Param(id=0, name="cap", type=Persistent[RealmGateway.Template(1)]), cara.Param(id=1, name="params", type=Persistent[RealmGateway.Template(0)].SaveParams)], results=Persistent[RealmGateway.Template(0)].SaveResults), cara.Method(id=1, name="export", params=[cara.Param(id=0, name="cap", type=Persistent[RealmGateway.Template(0)]), cara.Param(id=1, name="params", type=Persistent[RealmGateway.Template(1)].SaveParams)], results=Persistent[RealmGateway.Template(1)].SaveResults)])

__annotations__ = [cxx_capnp.namespace('capnp')]
