from sftpsyncer.sftpagent import SyncAgent
import dsmsfilepackager.exceptions

from functools import wraps
import hashlib
import json
import logging
import magic
import os

logger = logging.getLogger(name=__name__)


class ManifestItem(object):
    def __init__(self, rel_path, abs_path=None, type=None, sha256=None,
                 size=None):
        self.path = rel_path
        self.abs_path = abs_path
        self.type = type if type is not None else self._get_file_type()
        self.sha256 = sha256 if sha256 is not None else self._get_file_sha256()
        # file size may be 0
        self.size = size if size is not None else self._get_file_size()

    def verify_abs_path(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.abs_path:
                raise RuntimeError("You can't access this method without "
                                   "setting abs_path")
            return func(self, *args, **kwargs)
        return wrapper

    @verify_abs_path
    def _get_file_type(self):
        """
        Only used on regular init
        """
        return magic.from_file(self.abs_path)

    @verify_abs_path
    def _get_file_size(self):
        """
        Only used on regular init
        """
        return os.path.getsize(self.abs_path)

    @verify_abs_path
    def _get_file_sha256(self):
        """
        Only used on regular init
        """
        sha256 = hashlib.sha256()
        block_size = 128

        with open(self.abs_path, "rb") as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    @classmethod
    def init_from_dict(cls, d):
        path = d.keys()[0]
        abs_path = None
        type = d[path]["type"]
        size = d[path]["size"]
        sha256 = d[path]["sha256"]

        return cls(path, abs_path=abs_path, type=type, size=size,
                   sha256=sha256)

    def to_dict(self):
        return ({
            self.path: {
                "size": self.size,
                "type": self.type,
                "sha256": self.sha256,
            }
        })


class Manifest(object):
    def __init__(self):
        self.items = {}

    def add(self, manifest_item):
        if not isinstance(manifest_item, ManifestItem):
            raise TypeError("Must be of type ManifestItem")
        self.items[manifest_item.path] = manifest_item

    @property
    def files(self):
        return self.items.keys()

    def get(self, file_name):
        return self.items[file_name]

    def to_dict(self):
        items_dict = {}

        for file, file_data in self.items.items():
            items_dict.update(file_data.to_dict())

        return items_dict

    @classmethod
    def init_from_dict(cls, item_dict):
        self = cls()
        for file, file_data in item_dict.items():
            self.add(ManifestItem.init_from_dict({file: file_data}))
        return self


class DSMSFilePackage(SyncAgent):
    def __init__(self, target_id=None, job_id=None, uid=None, **kwargs):
        """
        Create a new DSMSFilePackage.
        target_id: int
        job_id: int
        uid: str (should be unique to this package)
        """

        self.MANIFEST_FILENAME = ".manifest"
        self.manifest = Manifest()
        self.target_id = str(target_id)
        self.job_id = str(job_id)
        self.uid = str(uid) if uid else None

        for v in ["target_id", "job_id"]:
            val = getattr(self, v)
            try:
                if not val or val != str(int(val)):
                    raise ValueError("Couldn't convert %s to int" % val)
            except Exception:
                raise ValueError("Must define %s as int, got %s" % (v, val))

        if not self.uid:
            raise ValueError(
                "Must supply uid unique ID string: currently %s" % self.uid)

        # reset the local root to one that reflects target, job, and uid
        kwargs["local_root"] = os.path.join(kwargs["local_root"],
                                            self.relative_path)
        if not os.path.isdir(kwargs["local_root"]):
            os.makedirs(kwargs["local_root"])

        kwargs["remote_root"] = os.path.join(kwargs["remote_root"],
                                             self.relative_path)
        super(DSMSFilePackage, self).__init__(**kwargs)

    @classmethod
    def init_from_env(cls, target_id=None, job_id=None, uid=None):
        """
        Create a new DSMSFilePackage based on env variables, namely:
            DSMS_FILE_CACHE_ROOT, DSMS_SFTP_ADDRESS, DSMS_SFTP_PORT,
            DSMS_SFTP_USER, DSMS_SFTP_REMOTE_ROOT, DSMS_SFTP_KEY_PATH,
            SFTP_FAKE_CONN
        """
        kw = {}
        kw["local_root"] = os.environ.get("DSMS_FILE_CACHE_ROOT")
        kw["hostname"] = os.environ.get("DSMS_SFTP_ADDRESS")
        kw["host_port"] = os.environ.get("DSMS_SFTP_PORT")
        kw["username"] = os.environ.get("DSMS_SFTP_USER")
        kw["remote_root"] = os.environ.get("DSMS_SFTP_REMOTE_ROOT")
        kw["key_path"] = os.environ.get("DSMS_SFTP_KEY_PATH")
        kw["fake_connection"] = os.environ.get("SFTP_FAKE_CONN")

        return cls(target_id, job_id, uid, **kw)

    def add(self, rel_file_path):
        self.upload_queue.add(rel_file_path)
        self.add_manifest(rel_file_path)

    def add_manifest(self, rel_file_path):
        abs_file = os.path.join(self.local_root, rel_file_path)
        self.manifest.add(ManifestItem(rel_file_path, abs_path=abs_file))

    def add_dir(self, rel_dir_path):
        self.upload_queue.add_dir(rel_dir_path,
                                  file_callback=self.add_manifest)

    @property
    def local_path(self):
        return self.local_root

    @property
    def relative_path(self):
        """
        Get path based on target, job, and uid
        """
        return os.path.join(self.target_id, self.job_id, self.uid)

    def _load_manifest(self):
        try:
            with self.open(self.MANIFEST_FILENAME) as f:
                return Manifest.init_from_dict(json.load(f))
        except dsmsfilepackager.exceptions.FileNotFound:
            raise RuntimeError("Couldn't find manifest. You need to finish() "
                               "the package first.")

    def generate_manifest_file(self):
        manifest_path = self._rel_path_to_abs_local(self.MANIFEST_FILENAME)
        with open(manifest_path, "w") as f:
            json.dump(self.manifest.to_dict(), f)

    def finish(self, disconnect_after=True):
        """
        Finalize file manifest, then add the manifest to the list
        disconnect_after: automatically disconnect after completing upload
        """
        self.generate_manifest_file()
        self.upload_queue.add(self.MANIFEST_FILENAME)
        if disconnect_after:
            self.disconnect()

    def finish_and_upload(self, disconnect_after=True):
        """
        Finalize file manifest, then upload all files in list.
        disconnect_after: automatically disconnect after completing upload
        """
        self.finish(disconnect_after=False)
        self.push()
        if disconnect_after:
            self.disconnect()

    @classmethod
    def fetch(cls, target_id=None, job_id=None, uid=None, **kwargs):
        self = cls(target_id, job_id, uid, **kwargs)
        self.manifest = self._load_manifest()
        return self
