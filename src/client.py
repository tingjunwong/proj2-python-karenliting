import argparse
import xmlrpc.client
import os

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="SurfStore client")
	parser.add_argument('hostport', help='host:port of the server')
	parser.add_argument('basedir', help='The base directory')
	parser.add_argument('blocksize', type=int, help='Block size')
	args = parser.parse_args()

	try:
		metadatapath = args.basedir+"/index.txt"
		hostport = args.hostport
		blocksize = args.blocksize
		client  = xmlrpc.client.ServerProxy('http://localhost:8080')
		# Test ping
		client.surfstore.ping()
		print("Ping() successful")
		# read index.txt
		hashlist = []
		if os.path.isfile(metadatapath):#if index.txt exist
			with open(metadatapath) as f:
		    for line in f:
		    	fileinfo = line.split()
		    	filename = fileinfo[0]
		    	version = fileinfo[1]
		    	for i in range(2,len(fileinfo)):
		    		hashlist.append(fileinfo[i])

		        print(":"+line.rstrip('\n'))
		    print("fileinfo:"+fileinfo)
		    print("version:"+version)
		    print("hashlist:")
		    print(hashlist)
		        
		else:#if not exist create
			f = open(metadatapath,"w+")
			f.write("filename v h1")


	except Exception as e:
		print("Client: " + str(e))


# 1. Local checkup
	# 1.1 calculate hash on all files, is the file updated locally? 
	
	
	# 1.2 if updated, update index.html


# 2. Download FileInfoMap from server



# 3. Update files
	# 3.1 [DOWNLOAD] if((local_version < remote_version) || 
	# 					((local_version = remote_version) & (local_hash != remote_hash)))
		# 3.1.1 download file

		# 3.1.2 update index.html


	# 3.2 [UPDATE]	if((local_version = remote_version + 1)
		# [UPLOAD]
		# 3.2.1 upload file
			# putblock(hashlist[0~n])


		# 3.2.2 update remote FileInfoMap
			# updateFile(filename, version, blocklist)


		# [DELETE]
		# 3.2.3 update remote FileInfoMap(set hash list to 0) 
			# updateFile(filename, version, blocklist)