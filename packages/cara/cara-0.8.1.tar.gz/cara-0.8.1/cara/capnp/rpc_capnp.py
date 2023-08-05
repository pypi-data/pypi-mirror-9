from cara import cara

# Forward declarations:
from cara.capnp import cxx_capnp
Message = cara.Struct(name="Message", id=0x91b79f1f808db032)
Bootstrap = cara.Struct(name="Bootstrap", id=0xe94ccf8031176ec4)
Call = cara.Struct(name="Call", id=0x836a53ce789d4cd4)
Return = cara.Struct(name="Return", id=0x9e19b28d3db3573a)
Finish = cara.Struct(name="Finish", id=0xd37d2eb2c2f80e63)
Resolve = cara.Struct(name="Resolve", id=0xbbc29655fa89086e)
Release = cara.Struct(name="Release", id=0xad1a6c0d7dd07497)
Disembargo = cara.Struct(name="Disembargo", id=0xf964368b0fbd3711)
Provide = cara.Struct(name="Provide", id=0x9c6a046bfbc1ac5a)
Accept = cara.Struct(name="Accept", id=0xd4c9b56290554016)
Join = cara.Struct(name="Join", id=0xfbe1980490e001af)
MessageTarget = cara.Struct(name="MessageTarget", id=0x95bc14545813fbc1)
Payload = cara.Struct(name="Payload", id=0x9a0e61223d96743b)
CapDescriptor = cara.Struct(name="CapDescriptor", id=0x8523ddc40b86b8b0)
PromisedAnswer = cara.Struct(name="PromisedAnswer", id=0xd800b1d6cd6f1ca0)
PromisedAnswer.Op = cara.Struct(name="Op", id=0xf316944415569081)
ThirdPartyCapDescriptor = cara.Struct(name="ThirdPartyCapDescriptor", id=0xd37007fde1f0027d)
Exception = cara.Struct(name="Exception", id=0xd625b7063acf691a)
Exception.Type = cara.Enum(name="Type", enumerants=[cara.Enumerant(name="failed", ordinal=0), cara.Enumerant(name="overloaded", ordinal=1), cara.Enumerant(name="disconnected", ordinal=2), cara.Enumerant(name="unimplemented", ordinal=3)])

# Finishing declarations:
Message.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="unimplemented", type=Message), cara.Field(id=1, name="abort", type=Exception), cara.Field(id=2, name="call", type=Call), cara.Field(id=3, name="return", type=Return), cara.Field(id=4, name="finish", type=Finish), cara.Field(id=5, name="resolve", type=Resolve), cara.Field(id=6, name="release", type=Release), cara.Field(id=7, name="obsoleteSave", type=cara.AnyPointer), cara.Field(id=8, name="bootstrap", type=Bootstrap), cara.Field(id=9, name="obsoleteDelete", type=cara.AnyPointer), cara.Field(id=10, name="provide", type=Provide), cara.Field(id=11, name="accept", type=Accept), cara.Field(id=12, name="join", type=Join), cara.Field(id=13, name="disembargo", type=Disembargo)])])
Bootstrap.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="deprecatedObjectId", type=cara.AnyPointer)])
Call.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="target", type=MessageTarget), cara.Field(id=2, name="interfaceId", type=cara.Uint64), cara.Field(id=3, name="methodId", type=cara.Uint16), cara.Field(id=4, name="params", type=Payload), cara.Group(id=5, name="sendResultsTo", fields=[cara.Union(fields=[cara.Field(id=0, name="caller", type=cara.Void), cara.Field(id=1, name="yourself", type=cara.Void), cara.Field(id=2, name="thirdParty", type=cara.AnyPointer)])]), cara.Field(id=6, name="allowThirdPartyTailCall", default=False, type=cara.Bool)])
Return.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=2, name="results", type=Payload), cara.Field(id=3, name="exception", type=Exception), cara.Field(id=4, name="canceled", type=cara.Void), cara.Field(id=5, name="resultsSentElsewhere", type=cara.Void), cara.Field(id=6, name="takeFromOtherQuestion", type=cara.Uint32), cara.Field(id=7, name="acceptFromThirdParty", type=cara.AnyPointer)]), cara.Field(id=0, name="answerId", type=cara.Uint32), cara.Field(id=1, name="releaseParamCaps", default=True, type=cara.Bool)])
Finish.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="releaseResultCaps", default=True, type=cara.Bool)])
Resolve.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=1, name="cap", type=CapDescriptor), cara.Field(id=2, name="exception", type=Exception)]), cara.Field(id=0, name="promiseId", type=cara.Uint32)])
Release.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.Uint32), cara.Field(id=1, name="referenceCount", type=cara.Uint32)])
Disembargo.FinishDeclaration(
    fields=[cara.Field(id=0, name="target", type=MessageTarget), cara.Group(id=1, name="context", fields=[cara.Union(fields=[cara.Field(id=0, name="senderLoopback", type=cara.Uint32), cara.Field(id=1, name="receiverLoopback", type=cara.Uint32), cara.Field(id=2, name="accept", type=cara.Void), cara.Field(id=3, name="provide", type=cara.Uint32)])])])
Provide.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="target", type=MessageTarget), cara.Field(id=2, name="recipient", type=cara.AnyPointer)])
Accept.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="provision", type=cara.AnyPointer), cara.Field(id=2, name="embargo", type=cara.Bool)])
Join.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="target", type=MessageTarget), cara.Field(id=2, name="keyPart", type=cara.AnyPointer)])
MessageTarget.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="importedCap", type=cara.Uint32), cara.Field(id=1, name="promisedAnswer", type=PromisedAnswer)])])
Payload.FinishDeclaration(
    fields=[cara.Field(id=0, name="content", type=cara.AnyPointer), cara.Field(id=1, name="capTable", type=cara.List(CapDescriptor))])
CapDescriptor.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="none", type=cara.Void), cara.Field(id=1, name="senderHosted", type=cara.Uint32), cara.Field(id=2, name="senderPromise", type=cara.Uint32), cara.Field(id=3, name="receiverHosted", type=cara.Uint32), cara.Field(id=4, name="receiverAnswer", type=PromisedAnswer), cara.Field(id=5, name="thirdPartyHosted", type=ThirdPartyCapDescriptor)])])
PromisedAnswer.Op.FinishDeclaration(
    fields=[cara.Union(fields=[cara.Field(id=0, name="noop", type=cara.Void), cara.Field(id=1, name="getPointerField", type=cara.Uint16)])])
PromisedAnswer.FinishDeclaration(
    fields=[cara.Field(id=0, name="questionId", type=cara.Uint32), cara.Field(id=1, name="transform", type=cara.List(PromisedAnswer.Op))])
ThirdPartyCapDescriptor.FinishDeclaration(
    fields=[cara.Field(id=0, name="id", type=cara.AnyPointer), cara.Field(id=1, name="vineId", type=cara.Uint32)])
Exception.Type.FinishDeclaration(
    enumerants=[cara.Enumerant(name="failed", ordinal=0), cara.Enumerant(name="overloaded", ordinal=1), cara.Enumerant(name="disconnected", ordinal=2), cara.Enumerant(name="unimplemented", ordinal=3)])
Exception.FinishDeclaration(
    fields=[cara.Field(id=0, name="reason", type=cara.Text), cara.Field(id=1, name="obsoleteIsCallersFault", type=cara.Bool), cara.Field(id=2, name="obsoleteDurability", type=cara.Uint16), cara.Field(id=3, name="type", type=Exception.Type)])

__annotations__ = [cxx_capnp.namespace('capnp::rpc')]
