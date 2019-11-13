from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import hashlib

server_hashlist = []
nameToVersion = dict()
nameToHashs = dict()

Blocks = dict()

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class threadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# A simple ping, returns true
def ping():
    """A simple ping method"""
    print("Ping()")
    return True

# Gets a block, given a specific hash value
def getblock(h):
    """Gets a block"""
    print(h)
    blockData = Blocks[h]
    print(blockData)
    return blockData

# Puts a block
def putblock(h, b):
    """Puts a block"""
    print("PutBlock()")
    print(h)
    print(b)
    print(type(b))
    Blocks[h] = b
    server_hashlist.append(h)
    return True

# Given a list of blocks, return the subset that are on this server
def hasblocks(client_hashlist):
    """Determines which blocks are on this server"""
    print("HasBlocks()")
    intersection_list = [value for value in client_hashlist if value in server_hashlist]
    return intersection_list


# Retrieves the server's FileInfoMap
def getfileinfomap():
    """Gets the fileinfo map"""
    print("GetFileInfoMap()")
    print("======== FILEMAP ========")
    for f in nameToVersion.keys():
        print("===== File : {0} =====".format(f))
        print("Version : {0}".format(nameToVersion[f]))
        print("Hashs : {0}".format(nameToHashs[f]))
    return nameToVersion, nameToHashs


# Update a file's fileinfo entry
def updatefile(filename, version, hashlist):
    """Updates a file's fileinfo entry"""
    print("UpdateFile()")
    nameToVersion[filename] = version
    nameToHashs[filename] = hashlist

    print("===== Update File : {0} =====".format(filename))
    print("Version : {0}".format(nameToVersion[filename]))
    print("Hashs : {0}".format(nameToHashs[filename]))
    return True






# PROJECT 3 APIs below

# Queries whether this metadata store is a leader
# Note that this call should work even when the server is "crashed"
def isLeader():
    """Is this metadata store a leader?"""
    print("IsLeader()")
    return True

# "Crashes" this metadata store
# Until Restore() is called, the server should reply to all RPCs
# with an error (unless indicated otherwise), and shouldn't send
# RPCs to other servers
def crash():
    """Crashes this metadata store"""
    print("Crash()")
    return True

# "Restores" this metadata store, allowing it to start responding
# to and sending RPCs to other nodes
def restore():
    """Restores this metadata store"""
    print("Restore()")
    return True


# "IsCrashed" returns the status of this metadata node (crashed or not)
# This method should always work, even when the node is crashed
def isCrashed():
    """Returns whether this node is crashed or not"""
    print("IsCrashed()")
    return True

if __name__ == "__main__":
    try:
        print("Attempting to start XML-RPC Server...")
        server = threadedXMLRPCServer(('localhost', 8080), requestHandler=RequestHandler)
        server.register_introspection_functions()
        server.register_function(ping,"surfstore.ping")
        server.register_function(getblock,"surfstore.getblock")
        server.register_function(putblock,"surfstore.putblock")
        server.register_function(hasblocks,"surfstore.hasblocks")
        server.register_function(getfileinfomap,"surfstore.getfileinfomap")
        server.register_function(updatefile,"surfstore.updatefile")

        server.register_function(isLeader,"surfstore.isleader")
        server.register_function(crash,"surfstore.crash")
        server.register_function(restore,"surfstore.restore")
        server.register_function(isCrashed,"surfstore.iscrashed")
        print("Started successfully.")
        print("Accepting requests. (Halt program to stop.)")
        server.serve_forever()
    except Exception as e:
        print("Server: " + str(e))
