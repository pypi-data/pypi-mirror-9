"""
High level node object, to access node attribute 
and browse address space
"""

import opcua.uaprotocol as ua

class Node(object):
    """
    High level node object, to access node attribute 
    and browse address space
    """
    def __init__(self, server, nodeid):
        self.server = server
        self.nodeid = None
        if isinstance(nodeid, ua.NodeId):
            self.nodeid = nodeid
        elif type(nodeid) in (str, bytes):
            self.nodeid = ua.NodeId.from_string(nodeid)
        else:
            raise Exception("argument to node must be a NodeId object or a string defining a nodeid found {} of type {}".format(nodeid, type(nodeid)))

    def __str__(self):
        return "Node({})".format(self.nodeid)
    __repr__ = __str__

    def get_name(self):
        result = self.get_attribute(ua.AttributeIds.BrowseName)
        return result.Value

    def get_value(self):
        result = self.get_attribute(ua.AttributeIds.Value)
        return result.Value

    def _value(self):
        result = self.get_attribute(ua.AttributeIds.Value)
        return result.Value

    def set_value(self, value, varianttype=None):
        variant = None
        if type(value) == ua.Variant:
            variant = value
        else:
            variant = ua.Variant(value, varianttype)
        self.set_attribute(ua.AttributeIds.Value, ua.DataValue(variant))

    def set_attribute(self, attributeid, datavalue):
        attr = ua.WriteValue()
        attr.NodeId = self.nodeid
        attr.AttributeId = attributeid
        attr.Value = datavalue
        result = self.server.write([attr])
        result[0].check()

    def get_attribute(self, attr):
        rv = ua.ReadValueId()
        rv.NodeId = self.nodeid
        rv.AttributeId = attr
        params = ua.ReadParameters()
        params.NodesToRead.append(rv)
        result = self.server.read(params)
        result[0].StatusCode.check()
        return result[0].Value

    def get_children(self):
        desc = ua.BrowseDescription()
        desc.BrowseDirection = ua.BrowseDirection.Forward
        desc.ReferenceTypeId = ua.TwoByteNodeId(ua.ObjectIds.References)
        desc.IncludeSubtypes = True
        desc.NodeClassMask = ua.NodeClass.Unspecified
        desc.ResultMask = ua.BrowseResultMask.None_
 
        desc.NodeId = self.nodeid
        params = ua.BrowseParameters()
        params.NodesToBrowse.append(desc)
        results = self.server.browse(params)
        nodes = []
        for desc in results[0].References:
            node = Node(self.server, desc.NodeId)
            nodes.append(node)
        return nodes

    def get_child(self, path):
        rpath = ua.RelativePath()
        for item in path:
            el = ua.RelativePathElement()
            el.ReferenceTypeId = ua.TwoByteNodeId(ua.ObjectIds.HierarchicalReferences)
            el.IsInverse = False
            el.IncludeSubTypes = True
            if type(item) == ua.QualifiedName:
                el.TargetName = item
            else:
                el.TargetName = ua.QualifiedName.from_string(item)
            rpath.Elements.append(el)
        bpath = ua.BrowsePath()
        bpath.StartingNode = self.nodeid
        bpath.RelativePath = rpath
        result = self.server.translate_browsepaths_to_nodeids([bpath])
        result = result[0]
        result.StatusCode.check()
        #FIXME: seems this method may return several nodes
        return Node(self.server, result.Targets[0].TargetId)

      
