SSH executor for Sloth CI app extension that replaces the default executor and runs actions on a remote host (or multiple hosts) via SSH.

Config params::

    # Use the sloth-ci.ext.ssh_exec module.
    module: ssh_exec

    # Hosts, comma-delimited. Optional port number can be provided after ':' (if not specified, 22 is used).
    hosts:
        - ssh.example.com
        - myserver.com:23

    # Username to use for authentication.
    username: admin

    # Password to use for authentication or to unlock a private key.
    # password: foobar

    # Additional private key files. If not specified, only the keys from the default location are loaded (i.e. ~/.ssh).
    # keys: 
    #   - ~/my_ssh_keys/key_rsa
    #   - somekey

Username, password, and keys params are optional.


