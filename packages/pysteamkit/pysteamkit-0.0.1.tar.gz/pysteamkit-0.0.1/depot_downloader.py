import gevent.monkey; gevent.monkey.patch_all()
import argparse, logging, os
import binascii, json, re, struct
from getpass import getpass
from gevent.pool import Pool
from gevent.coros import Semaphore
from gevent.hub import sleep
from operator import attrgetter

from pysteamkit.crypto import CryptoUtil
from pysteamkit.cdn_client_pool import CDNClientPool
from pysteamkit.depot_manifest import DepotManifest
from pysteamkit.steam_base import EResult, EServerType, EDepotFileFlag
from pysteamkit.steam3.cdn_client import CDNClient
from pysteamkit.steam3.client import SteamClient
from pysteamkit.steamid import SteamID
from pysteamkit.util import Util

log = logging.getLogger('dd')
																
umask = None
if os.name == 'posix':
	umask = os.umask(0)
			
class SteamClientHandler(object):
	def __init__(self, args, install):
		self.args = args
		self.install = install
		self.auth_code = None
		
	def try_initialize_connection(self, client):
		alternate_steamid = 0
		if self.args.altinstance:
			if not self.args.username in self.install['accounts']:
				log.info("Cannot use alternate instance without first logging into account '%s'", self.args.username)
			else:
				steamid = SteamID(int(self.install['accounts'][self.args.username]))
				steamid.instance = 2
				alternate_steamid = steamid.steamid
			
		if self.args.username:
			logon_result = client.login(self.args.username, self.args.password, steamid=alternate_steamid, auth_code = self.auth_code)
		else:
			logon_result = client.login_anonymous()

		if logon_result.eresult == EResult.AccountLogonDenied:
			client.disconnect()
			log.info("Steam Guard is enabled on this account. Please enter the authentication code sent to your email address.")
			self.auth_code = raw_input('Auth code: ')
			return client.initialize()

		if logon_result.eresult != EResult.OK:
			log.error("logon failed %d", logon_result.eresult)
			return False
				
		if client.steamid.instance == 1:
			self.install['accounts'][self.args.username] = str(client.steamid.steamid)
			save_install_data(self.install)
			
			if self.args.altinstance:
				log.info("Switching to alternate instance..")
				client.disconnect()
				return client.initialize()
		
		log.info("Signed into Steam3 as %s" % (str(client.steamid),))
		if self.args.cellid == None:
			log.warn("No cell id specified, using Steam3 specified: %d" % (logon_result.cell_id,))
			self.args.cellid = logon_result.cell_id
		return True
			
	def handle_disconnected(self, client, user_reason):
		if not user_reason:
			for x in range(5):
				sleep(x+1)
				if client.initialize():
					return True
		return False
	
	def get_sentry_file(self, username):
		filename = 'sentry_%s.bin' % (username,)

		if not os.path.exists(filename):
			return None
			
		with open(filename, 'rb') as f:
			return f.read()

	def store_sentry_file(self, username, sentryfile):
		filename = 'sentry_%s.bin' % (username,)
		with open(filename, 'wb') as f:
			f.write(sentryfile)
			
	def handle_message(self, emsg, msg):
		emsg = Util.get_msg(emsg)


class DownloaderError(RuntimeError):
	pass


class DepotDownloader(object):
	def __init__(self, client, install):
		self.install = install
		self.client = client
		self.steamapps = client.steamapps
		self.sessiontoken = client.get_session_token()
		self.appid = None
		self.depots = None
		self.depot_keys = None
		self.manifest_ids = None
		self.existing_manifest_ids = None
		self.manifests = None
		self.path_prefix = None
		self.total_bytes_downloaded = 0
		self.total_download_size = 0
		self.net_action_pool = Pool(4)
		self.file_semaphore = Semaphore(8)
		
	def setup_cdnclient_pool(self, content_servers, appid, app_ticket, steamid):
		self.ccpool = CDNClientPool(self.steamapps, content_servers, appid, app_ticket, steamid)
			
	def get_app_ticket(self, appid):
		app_ticket = self.steamapps.get_app_ticket(appid)
		return app_ticket.ticket if app_ticket else None
		
	def get_depots_for_app(self, appid, filter):
		if not 'depots' in self.steamapps.app_cache[appid]:
			return []
		return [int(key) for key,values in self.steamapps.app_cache[appid]['depots'].iteritems() if key.isdigit() and (not filter or int(key) in filter)]
		
	def get_depot(self, appid, depotid):
		return self.steamapps.app_cache[appid]['depots'][str(depotid)]

	def get_depot_keystar(self, args):
		return self.get_depot_key(*args)
		
	def get_depot_key(self, appid, depotid):
		depot_key_result = self.steamapps.get_depot_key(depotid, appid)
		if depot_key_result.eresult != EResult.OK:
			return (depotid, None)

		return (depotid, depot_key_result.depot_encryption_key)
		
	def get_depot_manifeststar(self, args):
		return self.get_depot_manifest(*args)
		
	def get_depot_manifest(self, depotid, manifestid):
		ticket = self.get_app_ticket(depotid)
		try:
			client = self.ccpool.get_client(depotid, ticket)
		except:
			log.error("Unable to initialize any CDN clients for depot id %s manifest %s", depotid, manifestid)
			return (depotid, manifestid, None, 404)
			
		(status, manifest) = client.download_depot_manifest(depotid, manifestid)

		if manifest or client.mark_failed_request():
			self.ccpool.return_client(client)

		if manifest:
			return (depotid, manifestid, manifest, status)
		else:
			return (depotid, manifestid, None, status)
		
	def get_depot_chunkstar(self, args):
		return self.get_depot_chunk(*args)
		
	def get_depot_chunk(self, depotid, chunk):
		ticket = self.get_app_ticket(depotid)
		try:
			client = self.ccpool.get_client(depotid, ticket)
		except:
			log.error("Unable to initialize any CDN clients for depot id %s chunk %s", depotid, chunk.sha.encode('hex'))
			return (chunk, None, None, None)

		status = None
		chunk_data = None
		
		try:
			(status, chunk_data) = client.download_depot_chunk(depotid, chunk.sha.encode('hex'))
		except Exception as exc:
			log.error("Caught exception while downloading chunk %s: %s", chunk.sha.encode('hex'), exc)
			status = 0
			
		if chunk_data or client.mark_failed_request():
			self.ccpool.return_client(client)
			
		if chunk_data:
			return (chunk, chunk.offset, chunk_data, status)
		else:
			return (chunk, None, None, status)

	def get_app_info(self, appids, licenseids=None):
		product_info = self.steamapps.get_product_info(apps=appids, packages=licenseids)
		needs_token = [x.appid for x in product_info.apps if x.missing_token]
		
		if needs_token:
			tokens = self.steamapps.get_access_tokens(needs_token)
			if not tokens.app_access_tokens:
				raise DownloaderError("Unable to get access tokens for app %s" % (appids,))
			app_token_request = [(x.appid, x.access_token) for x in tokens.app_access_tokens]
			product_info = self.steamapps.get_product_info(apps=app_token_request, packages=licenseids)
			
		return product_info
					
	def set_appid(self, appid):
		licenses = self.steamapps.get_licenses()
		licenses = [x.package_id for x in licenses] if licenses else [17906]
		log.info("Licenses: %s", ', '.join(str(x) for x in licenses))
		
		product_info = self.get_app_info([appid], licenses)

		valid_apps = [x.appid for x in product_info.apps]
		if appid not in valid_apps:
			raise DownloaderError("Could not find an app for id %d" % (appid,))
		if not self.steamapps.has_license_for_app(appid):
			raise DownloaderError("You do not have a license for app %d"
					% (appid,))
					
		self.appid = appid
			
	def set_depots(self, depots_in=None, branch='public', betapassword=None):
		assert self.appid
		
		manifest_ids_req = []
		depot_filter = []
		
		if depots_in and len(depots_in) > 0:
			unzipped_depots_in = zip(*[map(int, x.split(':')) for x in depots_in])
			if len(unzipped_depots_in) > 1:
				(depot_filter, manifest_ids_req) = unzipped_depots_in
			else:
				(depot_filter, ) = unzipped_depots_in
				
		depots = self.get_depots_for_app(self.appid, depot_filter)
		if not depots:
			raise DownloaderError("No depots available for app %d "
					"given filter %s" % (self.appid, depot_filter))

		# get app info for any dependencies
		app_dependencies = set()
		for depotid in depots:
			depot = self.get_depot(self.appid, depotid)
			depends_app = depot.get('depotfromapp')
			
			if depends_app and depot.get('sharedinstall'):
				app_dependencies.add(int(depends_app))

		if len(app_dependencies) > 0:
			log.info("Fetching application dependencies")
			self.get_app_info(list(app_dependencies))
				
		log.info("Fetching decryption keys")
		depot_keys = {}
		keys = [(self.appid, depotid) for depotid in depots]
		
		for (depotid, depot_key) in self.net_action_pool.imap(self.get_depot_keystar, keys):
			if depot_key is None:
				#TODO: filter this out before with license checks
				log.warn("Could not get depot key for depot %d, skipped", depotid)
			else:
				depot_keys[depotid] = depot_key
			
		manifest_ids = {}
		existing_manifest_ids = {}
		
		for i in xrange(len(manifest_ids_req)):
			manifest_ids[depot_filter[i]] = manifest_ids_req[i]
			
		for depotid in depots:
			depot = self.get_depot(self.appid, depotid)
			log.info('Depot %d: "%s"', depotid, depot['name'])
					
			existing_manifest = self.install['manifests'].get(str(depotid))
			if existing_manifest:
				existing_manifest_ids[depotid] = existing_manifest
				
			if not depot_keys.get(depotid):
				log.warn("No depot key available for %d", depotid)
				continue
			elif depotid in manifest_ids:
				continue

			depends_app = depot.get('depotfromapp')
			if depends_app and depot.get('sharedinstall'):
				log.debug('Forwarded manifest request for depot %d to app %d', depotid, int(depends_app))
				depot = self.get_depot(int(depends_app), depotid)
				
			manifests = depot.get('manifests')
			encrypted_manifests = depot.get('encryptedmanifests')
			if manifests and manifests.get(branch):
				manifest = manifests[branch]
			elif encrypted_manifests and encrypted_manifests.get(branch):
				while not betapassword:
					betapassword = raw_input('Please enter the password for branch %s:' % (branch,))
					
				encrypted_gid = binascii.a2b_hex(encrypted_manifests[branch].get('encrypted_gid'))
				manifest_bytes = CryptoUtil.verify_and_decrypt_password(encrypted_gid, betapassword)
				
				if manifest_bytes == False:
					log.error("Unable to decrypt manifest for branch %s with given password", branch)
					return False
					
				(manifest,) = struct.unpack('q', manifest_bytes)
			else:
				log.error("Unable to find manifest for branch %s", branch)
				return False
				
			manifest_ids[depotid] = manifest

		self.manifest_ids = manifest_ids
		self.existing_manifest_ids = existing_manifest_ids
		self.depot_keys = depot_keys
		return True
		
	def set_path_prefix(self, path_prefix):
		self.path_prefix = path_prefix
		Util.makedir(path_prefix)		
		
	def _check_or_add_manifest_files(self, manifest_ids, manifests, manifests_to_retrieve):
		for (depotid, manifestid) in manifest_ids.iteritems():
			if os.path.exists('depots/%d_%s.manifest' % (depotid, manifestid)):
				with open('depots/%d_%s.manifest' % (depotid, manifestid), 'rb') as f:
					depot_manifest = DepotManifest()
					depot_manifest.parse(f.read())

					manifests[manifestid] = depot_manifest
			else:
				manifests_to_retrieve.append((depotid, manifestid))
				
	def download_depot_manifests(self, additional_depot_manifests={}):
		manifests_to_retrieve = []
		depot_manifests_retrieved = []
		manifests = {}
		num_tries = 0

		self._check_or_add_manifest_files(self.manifest_ids, manifests, manifests_to_retrieve)
		self._check_or_add_manifest_files(self.existing_manifest_ids, manifests, manifests_to_retrieve)
		self._check_or_add_manifest_files(additional_depot_manifests, manifests, manifests_to_retrieve)
		
		while len(depot_manifests_retrieved) < len(manifests_to_retrieve) and num_tries < 4:
			num_tries += 1
			manifests_needed = [(depotid, manifestid) for (depotid, manifestid) in manifests_to_retrieve if depotid not in depot_manifests_retrieved]
			
			for (depotid, manifestid, manifest, status) in self.net_action_pool.imap(self.get_depot_manifeststar, manifests_needed):
				if manifest:
					log.info("Got manifest %s for %d", manifestid, depotid)
					depot_manifests_retrieved.append(depotid)
					
					depot_manifest = DepotManifest()
					depot_manifest.parse(manifest)
					
					if not depot_manifest.decrypt_filenames(self.depot_keys[depotid]):
						log.error("Could not decrypt depot manifest for %d", depotid)
						return None
						
					manifests[manifestid] = depot_manifest

					with open('depots/%d_%s.manifest' % (depotid, manifestid), 'wb') as f:
						f.write(depot_manifest.serialize())
				elif status == 401:
					log.error("Did not have sufficient access to download manifest for %d", depotid)
					return None
				else:
					log.error("Missed depot manifest for %d", depotid)
					return None
		
		self.manifests = manifests
		return self.manifest_ids

	def record_depot_state(self, depotid, manifestid):
		self.install['manifests'][str(depotid)] = str(manifestid)
		
	def build_and_verify_download_list(self, appid, verify_all, filelist = None):
		total_download_size = 0
		depot_download_list = []

		# Get process umask, for chmod'ing files later on.
		if os.name == 'posix':
			os.umask(umask)

		for (depotid, manifestid) in self.manifest_ids.iteritems():
			manifest = self.manifests[manifestid]
			depot = self.get_depot(appid, depotid)
			depot_files = []
			files_changed = None
			files_deleted = []
			existing_file_dictionary = {}
			
			existing_manifest_id = self.existing_manifest_ids.get(depotid)
			if existing_manifest_id:
				existing_manifest = self.manifests[existing_manifest_id]
				(files_changed, files_deleted) = existing_manifest.get_files_changed(manifest)
				existing_file_dictionary = existing_manifest.file_dictionary

			for file in files_deleted:
				translated = file.replace('\\', os.path.sep)
				real_path = os.path.join(self.path_prefix, translated)
				
				log.debug("Deleting %s", real_path)
				try:
					os.unlink(real_path)
				except:
					#TODO: handle directories
					pass
					
			for file in manifest.files:
				if filelist and not file_matches_filter(file.filename, filelist):
					continue
					
				sorted_current_chunks = sorted(file.chunks, key=attrgetter('offset'))				
				translated = file.filename.replace('\\', os.path.sep)
				real_path = os.path.join(self.path_prefix, translated)
					
				if file.flags & EDepotFileFlag.Directory:
					Util.makedir(real_path)
					continue
					
				Util.makedir(os.path.dirname(real_path))
				
				if os.path.exists(real_path):
					log.debug("Verifying %s", translated)
					if os.name == 'posix' and file.flags & EDepotFileFlag.Executable:
						# Make it executable while honoring the local umask
						os.chmod(real_path, 0775 & ~umask)
					st = os.lstat(real_path)
					if (not verify_all
							and (files_changed is None or file.filename not in files_changed)
							and file.size == st.st_size):
						continue

					sorted_file_chunks = None
					chunks_needed = []
					existing_chunks = []
					existing_chunk_hashes = {}
					existing_file_mapping = existing_file_dictionary.get(file.filename)

					if existing_file_mapping:
						sorted_file_chunks = sorted(existing_file_mapping.chunks, key=attrgetter('offset'))
					else:
						sorted_file_chunks = sorted_current_chunks
										
					with open(real_path, 'rb') as f:
						for chunk in sorted_file_chunks:
							f.seek(chunk.offset)
							bytes = f.read(chunk.cb_original)
							
							if Util.adler_hash(bytes) == chunk.crc:
								existing_chunk_hashes[chunk.sha] = chunk
								if not existing_file_mapping:
									existing_chunks.append((chunk, chunk))
							elif not existing_file_mapping:
								chunks_needed.append(chunk)
								total_download_size += chunk.cb_original

					if existing_file_mapping:
						for chunk in sorted_current_chunks:
							existing_chunk = existing_chunk_hashes.get(chunk.sha)
							if existing_chunk:
								existing_chunks.append((chunk, existing_chunk))
								continue
								
							total_download_size += chunk.cb_original
							chunks_needed.append(chunk)
							
					if len(chunks_needed) > 0 or file.size != st.st_size:
						depot_files.append((file, chunks_needed, existing_chunks))
				else:
					total_download_size += file.size
					depot_files.append((file, sorted_current_chunks, None))
					
					
			if len(depot_files) > 0:
				depot_download_list.append((appid, depotid, manifestid, depot_files))
			else:
				self.record_depot_state(depotid, manifestid)
				
		return (depot_download_list, total_download_size)
			
	def reset_download_counters(self, total_download_size):
		self.total_bytes_downloaded = 0
		self.total_download_size = total_download_size
	
	def perform_download_actions(self, depot_download_list):
		depot_downloads = [gevent.spawn(self.perform_depot_download, depot_data) for depot_data in depot_download_list]
		gevent.joinall(depot_downloads)
		
		if self.total_bytes_downloaded < self.total_download_size:
			log.info("[%s/%s] Incomplete" % (Util.sizeof_fmt(self.total_bytes_downloaded), Util.sizeof_fmt(self.total_download_size)))
		else:
			log.info("[%s/%s] Completed" % (Util.sizeof_fmt(self.total_bytes_downloaded), Util.sizeof_fmt(self.total_download_size)))
		
	def perform_depot_download(self, depot_data):
		(appid, depotid, manifestid, depot_files) = depot_data
		
		depot = self.get_depot(appid, depotid)
		log.info("Downloading \"%s\"" % (depot['name'],))

		depot_file_downloads = [gevent.spawn(self.perform_file_download_and_update, (depotid, file_data)) for file_data in depot_files]
		gevent.joinall(depot_file_downloads)
		
		self.record_depot_state(depotid, manifestid)

	def perform_file_download_and_update(self, depotfiledata):
		(depotid, file_data) = depotfiledata
		(file, chunks_need, chunks_have) = file_data
		
		translated = file.filename.replace('\\', os.path.sep)
		real_path = os.path.join(self.path_prefix, translated)
		
		self.file_semaphore.acquire()

		if not os.path.exists(real_path):
			with open(real_path, 'w+b') as f:
				f.truncate(0)
					
		with open(real_path, 'rb') as freal:
			with open(real_path + '.partial', 'w+b') as f:
				f.truncate(file.size)
				chunks_completed = []
					
				if chunks_have is not None:
					for (chunk, prev_chunk) in chunks_have:
						freal.seek(prev_chunk.offset)
						f.seek(chunk.offset)
						f.write(freal.read(chunk.cb_original))
						
				while len(chunks_completed) < len(chunks_need):
					downloads = [(depotid, chunk) for chunk in chunks_need if not chunk.offset in chunks_completed]
					
					for (chunk, offset, chunk_data, status) in self.net_action_pool.imap(self.get_depot_chunkstar, downloads):
						if status is None:
							log.error("Unable to download chunk %s, out of CDN servers to try", chunk.sha.encode('hex'))
							self.file_semaphore.release()
							return
						elif status != 200:
							log.warn("Chunk failed %s %d", chunk.sha.encode('hex'), status)
							continue
								
						chunk_data = CDNClient.process_chunk(chunk_data, self.depot_keys[depotid])
						f.seek(offset)
						f.write(chunk_data)
						self.total_bytes_downloaded += len(chunk_data)
						chunks_completed.append(offset)
			
		if os.name != 'posix':
			os.unlink(real_path)
			
		try:
			os.rename(real_path + '.partial', real_path)
		except OSError:
			log.warning('Failed to rename %s to %s', real_path + '.partial', real_path)
			
		if os.name == 'posix' and file.flags & EDepotFileFlag.Executable:
			# Make it executable while honoring the local umask
			os.chmod(real_path, 0775 & ~umask)

		self.file_semaphore.release()
		
		log.info("[%s/%s] %s" % (Util.sizeof_fmt(self.total_bytes_downloaded),
			Util.sizeof_fmt(self.total_download_size), translated))
		
def initialize(args, install):
	while args.username and not args.password:
		args.password = getpass('Please enter the password for "' + args.username + '": ')
	
	client = SteamClient(SteamClientHandler(args, install))
	if not client.initialize():
		log.error("Unable to connect")
		return False

	return client

def load_install_data():
	if os.path.exists('install.json'):
		with open('install.json', 'r') as f:
			try:
				json_install = json.load(f)
				#upgrade
				if not 'accounts' in json_install:
					json_install['accounts'] = {}
				return json_install
			except ValueError:
				log.warn("Unable to load install data")
				
	return {'manifests': {}, 'accounts': {}}

def save_install_data(install):
	with open('install.json', 'w') as f:
		json.dump(install, f, sort_keys=True, indent=4, separators=(',', ': '))

def load_filelist(file):
	regexes = []
	plain = []
	with open(file, 'r') as f:
		lines = f.readlines()
		for line in lines:
			line = line.rstrip(' \t\r\n\0')
			regex = re.compile(line)
			if regex:
				regexes.append(regex)
			else:
				plain.append(line)
	return (regexes, plain)
	
def file_matches_filter(filename, filefilter):
	(regexes, plain) = filefilter
	for regex in regexes:
		if regex.match(filename):
			return True
	for name in plain:
		if filename == name:
			return True
	return False
	
def main():
	parser = argparse.ArgumentParser(description='DepotDownloader downloads depots.')
	parser.add_argument('appid', type=int, help='AppID to download')
	parser.add_argument('--branch', type=str, default='public', help='Application branch to download')
	parser.add_argument('--betapassword', type=str, help='Password supplied for branch')
	parser.add_argument('--dir', type=str, default='downloads/', help='Directory to operate within')
	parser.add_argument('--depots', type=str, nargs='*', help='Specific depots to download')
	parser.add_argument('--username', type=str, help='Username to sign in with')
	parser.add_argument('--password', type=str, help='Account password')
	parser.add_argument('--cellid', type=int, help='Cell ID to use for downloads')
	parser.add_argument('--verify-all', action='store_true', default=False, help='Specify to verify all files')
	parser.add_argument('--filelist', type=str, help='Specify a file filter')
	parser.add_argument('--altinstance', action='store_true', 
				help='Use an alternate account instance. Requires logging into the account once')
	parser.add_argument('--verbose', action='store_true',
                help='Print lots of extra output')
	parser.add_argument('--diffdepot', type=int, help='Diff depot id to operate on')
	parser.add_argument('--diffmanifest', type=int, help='Diff depot manifest with a target manifest id')
	
	args = parser.parse_args()

	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
			datefmt='%X',
                        level=logging.DEBUG if args.verbose else logging.INFO)
	
	filefilter = None
	if args.filelist:
		filefilter = load_filelist(args.filelist)
		
	install = load_install_data()
	Util.makedir('depots/')
	
	client = initialize(args, install)
	
	if client == False:
		return
		
	dl = DepotDownloader(client, install)
	dl.set_appid(args.appid)
	
	if not dl.set_depots(args.depots, args.branch, args.betapassword):
		return
	
	log.info("Building CDN server list")
	base_server_list = client.server_list[EServerType.CS]
	
	if base_server_list == None or len(base_server_list) == 0:
		log.error("No content servers to bootstrap from")
		return
	
	content_servers = None
	for (ip, port) in base_server_list:
		content_servers = CDNClient.fetch_server_list(ip, port, args.cellid)
		if content_servers:
			break
	
	if not content_servers:
		log.error("Unable to find any content servers for cell id %d" % (args.cellid,))
		return
		
	log.info("Found %d content servers" % (len(content_servers),))
	
	app_ticket = dl.get_app_ticket(args.appid)
	dl.setup_cdnclient_pool(content_servers, args.appid, app_ticket, client.steamid)
	
	additional = {}
	if args.diffmanifest and args.diffdepot:
		additional = {args.diffdepot: args.diffmanifest}
		
	log.info("Downloading depot manifests")
	depot_manifestids = dl.download_depot_manifests(additional)
	
	if depot_manifestids is None:
		return
		
	if args.diffmanifest and args.diffdepot:
		manifest_current = dl.manifests[depot_manifestids[args.diffdepot]]
		manifest_target = dl.manifests[args.diffmanifest]
		
		if depot_manifestids[args.diffdepot] == args.diffmanifest:
			log.info("Depot %s manifest %s is the same as current manifest %s", args.diffdepot, args.diffmanifest, depot_manifestids[args.diffdepot])
		else:
			log.info("Depot %s manifest %s and current manifest %s differ by:", args.diffdepot, args.diffmanifest, depot_manifestids[args.diffdepot])
			files_changed, files_deleted = manifest_current.get_files_changed(manifest_target)
			log.info("Modified: %s", ', '.join(files_changed))
			log.info("Deleted: %s", ', '.join(files_deleted))
		return
		
	dl.set_path_prefix(args.dir)

	log.info("Verifying existing files")
	(depot_download_list, total_download_size) = dl.build_and_verify_download_list(args.appid, args.verify_all, filelist = filefilter)	
	save_install_data(install)
	
	if total_download_size > 0:
		log.info('%s to download' % (Util.sizeof_fmt(total_download_size),))
	else:
		log.info('Nothing to download')
		return

	dl.reset_download_counters(total_download_size)
	dl.perform_download_actions(depot_download_list)
	save_install_data(install)

try:
	main()
except KeyboardInterrupt:
	pass