import argparse
import xmlrpc.client
import os
import hashlib


def hasLocalUpdate(a, b):
	diff = list(set(a) - set(b)) + list(set(b) - set(a))
	if diff is not []:
		return True
	else:
		return False



if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="SurfStore client")
	parser.add_argument('hostport', help='host:port of the server')
	parser.add_argument('basedir', help='The base directory')
	parser.add_argument('blocksize', type=int, help='Block size')
	args = parser.parse_args()

	try:
		metadatapath = args.basedir+"/index.txt"
		basedir = args.basedir
		hostport = args.hostport
		blocksize = args.blocksize
		client  = xmlrpc.client.ServerProxy('http://localhost:8080')
		# Test ping
		client.surfstore.ping()
		print("Ping() successful")
		# TODO: base directory does not exist?
		# read index.txt
		
		
		index_filelist = []
		add_filelist = []
		nameToVersion = {}
		nameTOHashs = {}
		if not(os.path.isfile(metadatapath)):
			open(metadatapath, "w+")

		with open(metadatapath) as f:
			for line in f:
				fileinfo = line.split()
				filename = fileinfo[0]
				version = fileinfo[1]
				index_filelist.append(filename)
				nameToVersion[filename] = version
				hashs = []
				for i in range(2,len(fileinfo)):
					hashs.append(fileinfo[i])
				nameTOHashs[filename] = hashs
		

		base_filelist = os.listdir(basedir)
		with open(metadatapath, "w") as f:
			for file in base_filelist:
				if file in index_filelist:
					continue
				elif file == "index.txt":
					continue
				else:
					# TODO: write after calculate hash
					f.write(file)
					f.write(" 1")
					f.write(" h1 h2 h3\n")
					add_filelist.append(file)

# 1. Local checkup
	# 1.1 calculate hash on all files, is the file updated locally? 
		for filename in index_filelist:
			file = open(args.basedir+"/"+filename, "rb")	#TODO: read binary
			new_hashs = []
			while True:
				chunk = file.read(blocksize)
				if not chunk:
					break
				h = hashlib.sha256(chunk).hexdigest()
				new_hashs.append(h)
			if hasLocalUpdate(new_hashs, nameTOHashs[filename]):
				nameToVersion[filename] += 1		

		for filename in add_filelist:
			nameToVersion[filename] = 1


# 2. Download FileInfoMap from server
		server_nameToVersion = {}
		server_nameToHashs = {}

		server_nameToVersion, server_nameToHashs = client.surfstore.getfileinfomap()

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


	except Exception as e:
		print("Client: " + str(e))