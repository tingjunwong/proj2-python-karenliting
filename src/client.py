import argparse
import xmlrpc.client

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="SurfStore client")
	parser.add_argument('hostport', help='host:port of the server')
	parser.add_argument('basedir', help='The base directory')
	parser.add_argument('blocksize', type=int, help='Block size')
	args = parser.parse_args()

	try:
		client  = xmlrpc.client.ServerProxy('http://localhost:8080')
		# Test ping
		client.surfstore.ping()
		print("Ping() successful")

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