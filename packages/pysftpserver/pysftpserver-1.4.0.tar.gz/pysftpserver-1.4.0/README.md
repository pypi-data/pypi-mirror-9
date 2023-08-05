#pysftpserver
An OpenSSH SFTP wrapper written in Python.

##Features
* Possibility to [automatically jail users](#authorized_keys_magic) in a virtual chroot environment as soon as they login.
* Possibility to [automatically forward SFTP requests to another server](#usage).
* Compatible with both Python 2 and Python 3.
* Fully extensible and customizable (examples below).
* Totally conforms to the [SFTP RFC](https://filezilla-project.org/specs/draft-ietf-secsh-filexfer-02.txt).

##Installation
Simply install pysftpserver with pip:
```bash
$ pip install pysftpserver # add the --user flag to install it just for you
```

**Note**: if you'd like to use the [automatic forwarding storage](#usage) you have to explicitly specify the paramiko dependency:
```bash
$ pip install pysftpserver[pysftpproxy]
```

Otherwise, you could always clone this repository and manually launch `setup.py`:
```bash
$ git clone https://github.com/unbit/pysftpserver.git
$ cd pysftpserver
$ python setup.py install
```

##Usage
We provide a couple of fully working examples:

* **pysftpjail**: an SFTP storage that jails users in a virtual chroot environment.
* **pysftpproxy**: an SFTP storage that acts as a proxy, forwarding each request to another SFTP server.

You'll find both our storages in your `$PATH` after the installation, so you can simply launch them by using the appropriate command line executable / arguments:

```
$ pysftpjail -h

usage: pysftpjail [-h] [--logfile LOGFILE] [--umask UMASK] chroot

An OpenSSH SFTP server wrapper that jails the user in a chroot directory.

positional arguments:
  chroot                the path of the chroot jail

optional arguments:
  -h, --help            show this help message and exit
  --logfile LOGFILE, -l LOGFILE
                        path to the logfile
  --umask UMASK, -u UMASK
                        set the umask of the SFTP server
```

```
$ pysftpproxy -h

usage: pysftpproxy [-h] [-l LOGFILE] [-k private-key-path] [-p PORT] [-a]
                   [-c ssh config path] [-n known_hosts path] [-d]
                   user[:password]@hostname

An OpenSSH SFTP server proxy that forwards each request to a remote server.

positional arguments:
  user[:password]@hostname
                        the ssh-url ([user[:password]@]hostname) of the remote
                        server. The hostname can be specified as a
                        ssh_config's hostname too. Every missing information
                        will be gathered from there

optional arguments:
  -h, --help            show this help message and exit
  -l LOGFILE, --logfile LOGFILE
                        path to the logfile
  -k private-key-path, --key private-key-path
                        private key identity path (defaults to ~/.ssh/id_rsa)
  -p PORT, --port PORT  SSH remote port (defaults to 22)
  -a, --ssh-agent       enable ssh-agent support
  -c ssh config path, --ssh-config ssh config path
                        path to the ssh-configuration file (default to
                        ~/.ssh/config)
  -n known_hosts path, --known-hosts known_hosts path
                        path to the openSSH known_hosts file
  -d, --disable-known-hosts
                        disable known_hosts fingerprint checking (security
                        warning!)
```

###authorized_keys magic
With `pysftpjail` you can jail any user in the virtual chroot as soon as she connects to the SFTP server.
You can do it by simply prepending the `pysftpjail` command to the user entry in your SSH `authorized_keys` file, e.g.:
```
command="pysftpjail path_to_your_jail" ssh-rsa AAAAB3[... and so on]
```

Probably, you'll want to add the following options too:
```
no-port-forwarding,no-x11-forwarding,no-agent-forwarding
```

Achieving as final result:
```
command="pysftpjail path_to_your_jail",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ssh-rsa AAAAB3[... and so on]
```

Obviusly, you could do the same with `pysftpproxy`.

##Customization
We provide two complete examples of SFTP storage: simple and jailed.
Anyway, you can subclass our [generic abstract storage](pysftpserver/abstractstorage.py) and you can adapt it to your needs.
Any contribution is welcomed, as always. :+1:

###Real world customization: MongoDB / GridFS storage
[MongoDB](http://www.mongodb.org/) is an open, NOSQL, document database.
[GridFS](http://docs.mongodb.org/manual/core/gridfs/) is a specification for storing and retrieving arbitrary files in a MongoDB database.
The following example will show how to build a storage that handles files in a MongoDB / GridFS database.

####Preliminary requirements
I assume you already have a MongoDB database running somewhere and you are using a [`virtualenv`](https://virtualenv.readthedocs.org/en/latest/virtualenv.html).
Let's install the MongoDB Python driver, `pymongo`, with:
```bash
$ pip install pymongo
```

Now clone this project's repository and install the base package in development mode.
```bash
$ git clone https://github.com/unbit/pysftpserver.git
$ cd pysftpserver
$ python setup.py develop
```
*Info for those who are asking:* development mode will let us modify the source of the packages and use it globally without needing to reinstall it.

Now you're ready to create the storage.

####New storage class
Let's create a new storage (save it as `pysftpserver/mongostorage.py`) that subclasses the [abstract storage](pysftpserver/abstractstorage.py) class.

```python
"""MongoDB GridFS SFTP storage."""

from pysftpserver.abstractstorage import SFTPAbstractServerStorage
from pysftpserver.pysftpexceptions import SFTPNotFound
import pymongo
import gridfs


class SFTPServerMongoStorage(SFTPAbstractServerStorage):
    """MongoDB GridFS SFTP storage class."""

    def __init__(self, home, remote, port, db_name):
        """Home sweet home.

        NOTE: you should set your home to something reasonable.
        Instruct the client to connect to your MongoDB.
        """
        self.home = "/"
        client = pymongo.MongoClient(remote, port)
        db = client[db_name]
        self.gridfs = gridfs.GridFS(db)

    def open(self, filename, flags, mode):
        """Return the file handle."""
        filename = filename.decode()  # needed in Python 3
        if self.gridfs.exists(filename=filename):
            return self.gridfs.find({'filename': filename})[0]

        raise SFTPNotFound

    def read(self, handle, off, size):
        """Read size from the handle. Offset is ignored."""
        return handle.read(size)

    def close(self, handle):
        """Close the file handle."""
        handle.close()

    """
    Warning: 
        this implementation is incomplete, many required methods are missing.
    """
```

As you can see, it's all pretty straight-forward.

In the `init` method, we initialize the MongoDB client, select the database to use and then we initialize GridFS.
Then, in the `open` method, we check if the file exists and return it's handler; in the `read` and `close` methods we simply forward the calls to the GridFS.

####Testing the new storage
I strongly encourage you to test your newly created storage. 
Here's an example (save it as `pysftpserver/tests/test_server_mongo.py`):

```python
import unittest
import os
from shutil import rmtree

import pymongo
import gridfs

from pysftpserver.server import *
from pysftpserver.mongostorage import SFTPServerMongoStorage
from pysftpserver.tests.utils import *

"""To run this tests you must have an instance of MongoDB running somewhere."""
REMOTE = "localhost"
PORT = 1727
DB_NAME = "mydb"


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        client = pymongo.MongoClient(REMOTE, PORT)
        db = client[DB_NAME]
        cls.gridfs = gridfs.GridFS(db)

    def setUp(self):
        os.chdir(t_path())
        self.home = 'home'

        if not os.path.isdir(self.home):
            os.mkdir(self.home)

        self.server = SFTPServer(
            SFTPServerMongoStorage(REMOTE, PORT, DB_NAME),
            logfile=t_path('log'),
            raise_on_error=True
        )

    def tearDown(self):
        os.chdir(t_path())
        rmtree(self.home)

    def test_read(self):
        s = b"This is a test file."
        f_name = "test"  # put expects a non byte string!
        b_f_name = b"test"

        f = self.gridfs.put(s, filename=f_name)
        self.server.input_queue = sftpcmd(
            SSH2_FXP_OPEN,
            sftpstring(b_f_name),
            sftpint(SSH2_FXF_CREAT),
            sftpint(0)
        )
        self.server.process()
        handle = get_sftphandle(self.server.output_queue)

        self.server.output_queue = b''  # reset the output queue
        self.server.input_queue = sftpcmd(
            SSH2_FXP_READ,
            sftpstring(handle),
            sftpint64(0),
            sftpint(len(s)),
        )
        self.server.process()
        data = get_sftpdata(self.server.output_queue)

        self.assertEqual(s, data)

        self.server.output_queue = b''  # reset output queue
        self.server.input_queue = sftpcmd(
            SSH2_FXP_CLOSE,
            sftpstring(handle)
        )
        self.server.process()

        # Cleanup!
        self.gridfs.delete(f)

    @classmethod
    def tearDownClass(cls):
        os.unlink(t_path("log"))  # comment me to see the log!
        rmtree(t_path("home"), ignore_errors=True)
```

####Final results
Finally, you can create a binary to comfortably launch the server using the created storage.
Save it as `bin/pysftpmongo`.

```python
#!/usr/bin/env python
"""pysftpmongo executable."""

import argparse
from pysftpserver.server import SFTPServer
from pysftpserver.mongostorage import SFTPServerMongoStorage


def main():
    parser = argparse.ArgumentParser(
        description='An OpenSSH SFTP server wrapper that uses a MongoDB/GridFS storage.'
    )

    parser.add_argument('remote', type=str,
                        help='the remote address of the MongoDB instance')
    parser.add_argument('port', type=int,
                        help='the remote port of the MongoDB instance')
    parser.add_argument('db_name', type=str,
                        help='the name of the DB to use')
    parser.add_argument('--logfile', '-l', dest='logfile',
                        help='path to the logfile')

    args = parser.parse_args()
    SFTPServer(
        storage=SFTPServerMongoStorage(
            args.remote,
            args.port,
            args.db_name
        ),
        logfile=args.logfile
    ).run()


if __name__ == '__main__':
    main()
```

Now, `chmod` the binary and check that it starts without a hitch:
```bash
$ chmod +x bin/pysftpmongo
$ bin/pysftpmongo "localhost" 1727 "mydb"
```

Finally, you should edit the `setup.py` `scripts` field to include your new binary. 
Now, running `python setup.py install` will put it somewhere in your `$PATH`, for later ease: e.g. when [using it in the authorized_keys file](#authorized_keys_magic).

A sneak peek of the final result (in the `authorized_keys` file):
```
command="pysftpmongo REMOTE_TO_YOUR_DB REMOTE_PORT DB_NAME",no-port-forwarding,no-x11-forwarding,no-agent-forwarding ssh-rsa AAAAB3[... and so on]
```

That's it!

####Code used in this example
All the code used in this example can be found in the [`examples/mongodb_gridfs`](examples/mongodb_gridfs/) directory of this repository.

##FileZilla compatibility
FileZilla requires the `longname` returned with each `SSH2_FXP_NAME` response (e.g. each time `readdir` is called) to be a string of the same format of the output of `ls -l` (`-rw-r--r--  1 aldur staff 9596 Dec 29 18:36 README.md`).

So, if you want to keep compatibility with FileZilla, be sure to include a proper `longname` field to the stats dictionary you return from your storage, as we do [here](pysftpserver/storage.py#L78).

##Tests
You can use [nose](https://nose.readthedocs.org/en/latest/) for tests.
From the project directory, simply run:
```bash
$ nosetests
$ python setup.py test # alternatively
```
