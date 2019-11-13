import argparse
import xmlrpc.client
import os
import hashlib
import sys

def hasDiffHashs(a, b):
	diff = list(set(a) - set(b)) + list(set(b) - set(a))
	if len(diff)!=0:
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
		
		
		index_filelist = []
		add_filelist = []
		delete_filelist = []
		nameToVersion = {}
		nameToHashs = {}

		if not(os.path.isdir(basedir)):
			print("Make base directory")
			os.mkdir(basedir)
		
		if not(os.path.isfile(metadatapath)):
			print("Make index.txt")
			open(metadatapath, "w+")

# 0. List all files
		# Read index.txt						[index_filelist] : files listed in index.txt
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
		
		# Read base directory					[base_filelist] : files in base directory
		base_filelist = os.listdir(basedir)
		if '.DS_Store' in base_filelist: 
			base_filelist.remove('.DS_Store')
		if 'index.txt' in base_filelist:
			base_filelist.remove('index.txt')

		# Find new added files					[add_filelist] : files in base directory that weren't in index.txt
		add_filelist = list(set(base_filelist) - set(index_filelist))


		# Find files that client deleted		[delete_filelist] : files in index.txt but not in base directory
		delete_filelist = list(set(index_filelist) - set(base_filelist))
	
	
		#										[all_filelist] : all files locally, even the deleted ones
		all_filelist = index_filelist + add_filelist

		print("Index filelist  = {0}".format(index_filelist))
		print("Base filelist   = {0}".format(base_filelist))
		print("Add filelist    = {0}".format(add_filelist))
		print("Delete filelist = {0}".format(delete_filelist))


# 1. Local checkup
	# 1.1 update info temprorily
		# files that I deleted/added/updated
		for filename in base_filelist:

			if filename in delete_filelist:
				nameToVersion[filename] += 1
				nameToHashs[filename] = [0]	
				continue
			
			elif filename in add_filelist:
				nameToVersion[filename] = 1
				file = open("base/try.txt", "rb")
				new_hashs = []
				print("chunking add files")
				while True:
					chunk = file.read(blocksize)
					if not chunk:
						break
					else:
						print("chunk = {0}".format(chunk))
						h = hashlib.sha256(chunk).hexdigest()
						print("hash = {0}".format(h))
						new_hashs.append(h)
				nameToHashs[filename] = new_hashs
				continue

			else:
				file = open(args.basedir+"/"+filename, "rb")
				new_hashs = []
				while True:
					print("chunking index file")
					chunk = file.read(blocksize)
					if not chunk:
						break
					else:
						print("chunk = {0}".format(chunk))
						h = hashlib.sha256(chunk).hexdigest()
						print("hash = {0}".format(h))
						new_hashs.append(h)
				if hasDiffHashs(new_hashs, nameToHashs[filename]):		# If updated locally, update the temporary version and hashs
					nameToVersion[filename] += 1
					nameToHashs[filename] = new_hashs
		


# 2. Download FileInfoMap from server
		server_nameToVersion = {}
		server_nameToHashs = {}
		server_nameToVersion, server_nameToHashs = client.surfstore.getfileinfomap()


		#										[server_filelist] : files that have info on server
		server_filelist = server_nameToVersion.keys()

		#										[download_filelist] : files that are on the server but not locally
		download_filelist = list(set(server_filelist) - set(all_filelist))
		
		
		print("Server file		= {0}".format(server_filelist))
		print("Download file	= {0}".format(download_filelist))



# 3. Update files	
		#[DOWNLOAD files that were never in the base directory]
		for filename in download_filelist:
			print("Download file: {0}".format(filename))
			nameToVersion[filename] = server_nameToVersion[filename]
			nameToHashs[filename] = server_nameToHashs[filename]
			with open(args.basedir+"/"+filename, "w+") as f:
				for h in nameToHashs[filename]:
					f.write(client.surfstore.get(h))

		#[UPLOAD files that were never in the server]
		for filename in add_filelist:
			print("Add file: {0}".format(filename))
			client_version = nameToVersion[filename]
			client_hashs = nameToHashs[filename]
			if filename not in server_filelist:
				print("[A] updatefile version{0}".format(client_version))
				client.surfstore.updatefile(filename, client_version, client_hashs)
				file = open("base/try.txt", "rb")
				while True:
					chunk = file.read(blocksize)
					if not chunk:
						break
					else:
						print(type(chunk))
						h = hashlib.sha256(chunk).hexdigest()
						success = client.surfstore.putblock(h, chunk)
						print("putblock {0}".format(success))
			else:
				if client_version <= server_nameToVersion[filename]:
					nameToVersion[filename] = server_nameToVersion[filename]
					nameToHashs[filename] = server_nameToHashs[filename]
					with open(args.basedir+"/"+filename, "w") as f:
						for h in nameToHashs[filename]:
							f.write(client.surfstore.getblock(h))


		for filename in index_filelist:
			client_version = nameToVersion[filename]
			client_hashs = nameToHashs[filename]
			print("cleint version = {0}  || server version = {1}".format(client_version, server_nameToVersion[filename]))
			# 3.1 [DOWNLOAD] if((local_version < remote_version) || 
			# ((local_version = remote_version) & (local_hash != remote_hash)))					
			if (client_version < server_nameToVersion[filename]) or (client_version == server_nameToVersion[filename]) and hasDiffHashs(client_hashs, server_nameToHashs[filename]):
				# 3.1.1 update index.html
				nameToVersion[filename] = server_nameToVersion[filename]
				nameToHashs[filename] = server_nameToHashs[filename]
				client_hashs = nameToHashs[filename]
				# 3.1.2 download file
				with open(args.basedir+"/"+filename, "w") as f:
					for h in client_hashs:
						f.write(client.surfstore.get(h))


			# 3.2 [UPDATE]	if((local_version = remote_version + 1)
			if client_version > server_nameToVersion[filename]:
				# [DELETE]
				if client_hashs == [0]:
					print("[B] updatefile version{0}".format(client_version))
					client.surfstore.updatefile(filename, client_version, client_hashs)
				# [UPLOAD]
				else:
					# 3.2.1 update remote FileInfoMap
					print("[C] updatefile version{0}".format(client_version))
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
							client.surfstore.putblock(h, chunk)

		for file in all_filelist:
			with open(metadatapath, "w+") as f:
				f.write(file+" "+str(nameToVersion[file]))
				print("num of hashs = {0}".format(len(nameToHashs[file])))
				for h in nameToHashs[file]:
					f.write(" "+(str(h)))
			f.close()


	except Exception as e:
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print("Unexpected error:", sys.exc_info()[0])
		print("Client: " + str(e))