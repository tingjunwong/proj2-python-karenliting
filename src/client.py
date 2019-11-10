import argparse
import xmlrpc.client
import os
import hashlib
import sys

def hasDiffHashs(a, b):
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
		delete_filelist = []
		nameToVersion = {}
		nameToHashs = {}

		if not(os.path.isdir(basedir)):
			os.mkdir(basedir)
		
		if not(os.path.isfile(metadatapath)):
			open(metadatapath, "w+")

		with open(metadatapath) as f:
			for line in f:
				fileinfo = line.split()
				filename = fileinfo[0]
				version = fileinfo[1]
				index_filelist.append(filename)
				nameToVersion[filename] = int(version)
				hashs = []
				for i in range(2,len(fileinfo)):
					hashs.append(fileinfo[i])
				nameToHashs[filename] = hashs
		

		base_filelist = os.listdir(basedir)
		if '.DS_Store' in base_filelist: 
			base_filelist.remove('.DS_Store')
		if 'index.txt' in base_filelist:
			base_filelist.remove('index.txt')
		with open(metadatapath, "w") as f:
			for file in base_filelist:
				if file in index_filelist:
					continue
				else:
					# TODO: write after calculate hash
					add_filelist.append(file)



# 1. Local checkup
	# 1.1 update index.txt temprorily

		# files that i deleted
		delete_filelist = list(set(index_filelist) - set(base_filelist))
		for filename in delete_filelist:
			nameToVersion[filename] += 1
			nameToHashs[filename] = [0]

		# files that i added
		for filename in add_filelist:
			nameToVersion[filename] = int(0)
			nameToHashs[filename] = []
		print("Add filelist  = {0}".format(add_filelist))
		print("Base filelist  = {0}".format(base_filelist))

		for filename in base_filelist:
			print(nameToVersion)
		# files that i updated or no modified
		for filename in base_filelist:
			file = open(args.basedir+"/"+filename, "rb")
			new_hashs = []
			while True:
				chunk = file.read(blocksize)
				if not chunk:
					break
				h = hashlib.sha256(chunk).hexdigest()
				new_hashs.append(h)
			if hasDiffHashs(new_hashs, nameToHashs[filename]):
				nameToVersion[filename] += 1
				nameToHashs[filename] = new_hashs
		

		all_filelist = index_filelist + add_filelist


# 2. Download FileInfoMap from server
		server_nameToVersion = {}
		server_nameToHashs = {}

		server_nameToVersion, server_nameToHashs = client.surfstore.getfileinfomap()





# 3. Update files
		server_filelist = server_nameToVersion.keys()
		print("Server file: {0}".format(server_filelist))

		download_filelist = list(set(server_filelist) - set(all_filelist))
		for filename in download_filelist:
			print("Download file: {0}".format(filename))
			nameToVersion[filename] = server_nameToVersion[filename]
			nameToHashs[filename] = server_nameToHashs[filename]
			with open(args.basedir+"/"+filename, "w+") as f:
				for h in client_hashs:
					f.write(client.surfstore.get(h))

		
		for filename in add_filelist:
			print("Add file: {0}".format(filename))
			client_version = nameToVersion[filename]
			client_hashs = nameToHashs[filename]
			if filename not in server_filelist:
				client.surfstore.updatefile(filename, client_version, client_hashs)
				file = open(args.basedir+"/"+filename, "rb")
				while True:
					chunk = file.read(blocksize)
					if not chunk:
						break
					h = hashlib.sha256(chunk).hexdigest()
					success = client.surfstore.putblock(chunk)
					print(success)
			else:
				if client_version <= server_nameToVersion[filename]:
					nameToVersion[filename] = server_nameToVersion[filename]
					nameToHashs[filename] = server_nameToHashs[filename]
					with open(args.basedir+"/"+filename, "w") as f:
						for h in client_hashs:
							f.write(client.surfstore.getblock(h))




		for filename in index_filelist:
			print("Index file: {0}".format(filename))
			client_version = nameToVersion[filename]
			client_hashs = nameToHashs[filename]
	# 3.1 [DOWNLOAD] if((local_version < remote_version) || 
	# ((local_version = remote_version) & (local_hash != remote_hash)))					
			if client_version < server_nameToVersion[filename]:
				# 3.1.1 update index.html
				nameToVersion[filename] = server_nameToVersion[filename]
				nameToHashs[filename] = server_nameToHashs[filename]
				# 3.1.2 download file
				with open(args.basedir+"/"+filename, "w") as f:
					for h in client_hashs:
						f.write(client.surfstore.get(h))

			if (client_version == server_nameToVersion[filename]) and hasDiffHashs(client_hashs, server_nameToHashs[filename]):
				# 3.1.1 update index.html
				nameToVersion[filename] = server_nameToVersion[filename]
				nameToHashs[filename] = server_nameToHashs[filename]
				# 3.1.2 download file
				with open(args.basedir+"/"+filename, "w") as f:
					for h in client_hashs:
						f.write(client.surfstore.get(h))


	# 3.2 [UPDATE]	if((local_version = remote_version + 1)
			if client_version > server_nameToVersion[filename]:
				# [DELETE]
				if client_hashs == [0]:
					client.surfstore.updatefile(filename, client_version, client_hashs)
				# [UPLOAD]
				# 3.2.1 update remote FileInfoMap
				else:
					client.surfstore.updatefile(filename, client_version, client_hashs)
				
				# 3.2.2 upload file
					upToDateHashs = client.surfstore.hasblocks(client_hashs)
					file = open(args.basedir+"/"+filename, "rb")
					while True:
						chunk = file.read(blocksize)
						if not chunk:
							break
						h = hashlib.sha256(chunk).hexdigest()
						if h not in upToDateHashs:
							client.surfstroe.putblock(chunk)

		

	except Exception as e:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print("Unexpected error:", sys.exc_info()[0])
		print("Client: " + str(e))