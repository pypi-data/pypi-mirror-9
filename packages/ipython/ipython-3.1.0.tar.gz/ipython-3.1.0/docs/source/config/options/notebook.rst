IPython notebook options
========================

To configure the IPython kernel, see :doc:`kernel`.

NotebookApp.allow_credentials : Bool
    Default: `False`

    Set the Access-Control-Allow-Credentials: true header

NotebookApp.allow_origin : Unicode
    Default: `''`

    Set the Access-Control-Allow-Origin header
    
    Use '*' to allow any origin to access your server.
    
    Takes precedence over allow_origin_pat.


NotebookApp.allow_origin_pat : Unicode
    Default: `''`

    Use a regular expression for the Access-Control-Allow-Origin header
    
    Requests from an origin matching the expression will get replies with:
    
        Access-Control-Allow-Origin: origin
    
    where `origin` is the origin of the request.
    
    Ignored if allow_origin is set.


NotebookApp.base_project_url : Unicode
    Default: `'/'`

    DEPRECATED use base_url

NotebookApp.base_url : Unicode
    Default: `'/'`

    The base URL for the notebook server.
    
    Leading and trailing slashes can be omitted,
    and will automatically be added.


NotebookApp.browser : Unicode
    Default: `u''`

    Specify what command to use to invoke a web
    browser when opening the notebook. If not specified, the
    default browser will be determined by the `webbrowser`
    standard library module, which allows setting of the
    BROWSER environment variable to override it.


NotebookApp.certfile : Unicode
    Default: `u''`

    The full path to an SSL/TLS certificate file.

NotebookApp.cluster_manager_class : Type
    Default: `<class 'IPython.html.services.clusters.clustermanager.Cluster...`

    The cluster manager class to use.

NotebookApp.config_manager_class : Type
    Default: `<class 'IPython.html.services.config.manager.ConfigManager'>`

    The config manager class to use

NotebookApp.contents_manager_class : Type
    Default: `<class 'IPython.html.services.contents.filemanager.FileConten...`

    The notebook manager class to use.

NotebookApp.cookie_secret : Bytes
    Default: `''`

    The random bytes used to secure cookies.
    By default this is a new random number every time you start the Notebook.
    Set it to a value in a config file to enable logins to persist across server sessions.
    
    Note: Cookie secrets should be kept private, do not share config files with
    cookie_secret stored in plaintext (you can read the value from a file).


NotebookApp.cookie_secret_file : Unicode
    Default: `u''`

    The file where the cookie secret is stored.

NotebookApp.copy_config_files : Bool
    Default: `False`

    Whether to install the default config files into the profile dir.
    If a new profile is being created, and IPython contains config files for that
    profile, then they will be staged into the new directory.  Otherwise,
    default config files will be automatically generated.


NotebookApp.default_url : Unicode
    Default: `'/tree'`

    The default URL to redirect to from `/`

NotebookApp.enable_mathjax : Bool
    Default: `True`

    Whether to enable MathJax for typesetting math/TeX
    
    MathJax is the javascript library IPython uses to render math/LaTeX. It is
    very large, so you may want to disable it if you have a slow internet
    connection, or for offline use of the notebook.
    
    When disabled, equations etc. will appear as their untransformed TeX source.


NotebookApp.extra_config_file : Unicode
    Default: `u''`

    Path to an extra config file to load.
    
    If specified, load this config file in addition to any other IPython config.


NotebookApp.extra_nbextensions_path : List
    Default: `[]`

    extra paths to look for Javascript notebook extensions

NotebookApp.extra_static_paths : List
    Default: `[]`

    Extra paths to search for serving static files.
    
    This allows adding javascript/css to be available from the notebook server machine,
    or overriding individual files in the IPython

NotebookApp.extra_template_paths : List
    Default: `[]`

    Extra paths to search for serving jinja templates.
    
    Can be used to override templates from IPython.html.templates.

NotebookApp.file_to_run : Unicode
    Default: `''`

    No description

NotebookApp.ip : Unicode
    Default: `'localhost'`

    The IP address the notebook server will listen on.

NotebookApp.ipython_dir : Unicode
    Default: `u''`

    
    The name of the IPython directory. This directory is used for logging
    configuration (through profiles), history storage, etc. The default
    is usually $HOME/.ipython. This option can also be specified through
    the environment variable IPYTHONDIR.


NotebookApp.jinja_environment_options : Dict
    Default: `{}`

    Supply extra arguments that will be passed to Jinja environment.

NotebookApp.kernel_manager_class : Type
    Default: `<class 'IPython.html.services.kernels.kernelmanager.MappingKe...`

    The kernel manager class to use.

NotebookApp.kernel_spec_manager_class : Type
    Default: `<class 'IPython.kernel.kernelspec.KernelSpecManager'>`

    
    The kernel spec manager class to use. Should be a subclass
    of `IPython.kernel.kernelspec.KernelSpecManager`.
    
    The Api of KernelSpecManager is provisional and might change
    without warning between this version of IPython and the next stable one.


NotebookApp.keyfile : Unicode
    Default: `u''`

    The full path to a private key file for usage with SSL/TLS.

NotebookApp.log_datefmt : Unicode
    Default: `'%Y-%m-%d %H:%M:%S'`

    The date format used by logging formatters for %(asctime)s

NotebookApp.log_format : Unicode
    Default: `'[%(name)s]%(highlevel)s %(message)s'`

    The Logging format template

NotebookApp.log_level : 0|10|20|30|40|50|'DEBUG'|'INFO'|'WARN'|'ERROR'|'CRITICAL'
    Default: `30`

    Set the log level by value or name.

NotebookApp.login_handler_class : Type
    Default: `<class 'IPython.html.auth.login.LoginHandler'>`

    The login handler class to use.

NotebookApp.logout_handler_class : Type
    Default: `<class 'IPython.html.auth.logout.LogoutHandler'>`

    The logout handler class to use.

NotebookApp.mathjax_url : Unicode
    Default: `''`

    The url for MathJax.js.

NotebookApp.notebook_dir : Unicode
    Default: `u''`

    The directory to use for notebooks and kernels.

NotebookApp.open_browser : Bool
    Default: `True`

    Whether to open in a browser after starting.
    The specific browser used is platform dependent and
    determined by the python standard library `webbrowser`
    module, unless it is overridden using the --browser
    (NotebookApp.browser) configuration option.


NotebookApp.overwrite : Bool
    Default: `False`

    Whether to overwrite existing config files when copying

NotebookApp.password : Unicode
    Default: `u''`

    Hashed password to use for web authentication.
    
    To generate, type in a python/IPython shell:
    
      from IPython.lib import passwd; passwd()
    
    The string should be of the form type:salt:hashed-password.


NotebookApp.port : Integer
    Default: `8888`

    The port the notebook server will listen on.

NotebookApp.port_retries : Integer
    Default: `50`

    The number of additional ports to try if the specified port is not available.

NotebookApp.profile : Unicode
    Default: `u'default'`

    The IPython profile to use.

NotebookApp.pylab : Unicode
    Default: `'disabled'`

    
    DISABLED: use %pylab or %matplotlib in the notebook to enable matplotlib.


NotebookApp.reraise_server_extension_failures : Bool
    Default: `False`

    Reraise exceptions encountered loading server extensions?

NotebookApp.server_extensions : List
    Default: `[]`

    Python modules to load as notebook server extensions. This is an experimental API, and may change in future releases.

NotebookApp.session_manager_class : Type
    Default: `<class 'IPython.html.services.sessions.sessionmanager.Session...`

    The session manager class to use.

NotebookApp.ssl_options : Dict
    Default: `{}`

    Supply SSL options for the tornado HTTPServer.
    See the tornado docs for details.

NotebookApp.tornado_settings : Dict
    Default: `{}`

    Supply overrides for the tornado.web.Application that the IPython notebook uses.

NotebookApp.trust_xheaders : Bool
    Default: `False`

    Whether to trust or not X-Scheme/X-Forwarded-Proto and X-Real-Ip/X-Forwarded-For headerssent by the upstream reverse proxy. Necessary if the proxy handles SSL

NotebookApp.verbose_crash : Bool
    Default: `False`

    Create a massive crash report when IPython encounters what may be an
    internal error.  The default is to append a short message to the
    usual traceback

NotebookApp.webapp_settings : Dict
    Default: `{}`

    DEPRECATED, use tornado_settings

NotebookApp.websocket_url : Unicode
    Default: `''`

    The base URL for websockets,
    if it differs from the HTTP server (hint: it almost certainly doesn't).
    
    Should be in the form of an HTTP origin: ws[s]://hostname[:port]


KernelManager.autorestart : Bool
    Default: `False`

    Should we autorestart the kernel if it dies.

KernelManager.connection_file : Unicode
    Default: `''`

    JSON file in which to store connection info [default: kernel-<pid>.json]
    
    This file will contain the IP, ports, and authentication key needed to connect
    clients to this kernel. By default, this file will be created in the security dir
    of the current profile, but can be specified by absolute path.


KernelManager.control_port : Integer
    Default: `0`

    set the control (ROUTER) port [default: random]

KernelManager.hb_port : Integer
    Default: `0`

    set the heartbeat port [default: random]

KernelManager.iopub_port : Integer
    Default: `0`

    set the iopub (PUB) port [default: random]

KernelManager.ip : Unicode
    Default: `u''`

    Set the kernel's IP address [default localhost].
    If the IP address is something other than localhost, then
    Consoles on other machines will be able to connect
    to the Kernel, so be careful!

KernelManager.kernel_cmd : List
    Default: `[]`

    DEPRECATED: Use kernel_name instead.
    
    The Popen Command to launch the kernel.
    Override this if you have a custom kernel.
    If kernel_cmd is specified in a configuration file,
    IPython does not pass any arguments to the kernel,
    because it cannot make any assumptions about the 
    arguments that the kernel understands. In particular,
    this means that the kernel does not receive the
    option --debug if it given on the IPython command line.


KernelManager.shell_port : Integer
    Default: `0`

    set the shell (ROUTER) port [default: random]

KernelManager.stdin_port : Integer
    Default: `0`

    set the stdin (ROUTER) port [default: random]

KernelManager.transport : 'tcp'|'ipc'
    Default: `'tcp'`

    No description

ProfileDir.location : Unicode
    Default: `u''`

    Set the profile location directly. This overrides the logic used by the
    `profile` option.

Session.buffer_threshold : Integer
    Default: `1024`

    Threshold (in bytes) beyond which an object's buffer should be extracted to avoid pickling.

Session.copy_threshold : Integer
    Default: `65536`

    Threshold (in bytes) beyond which a buffer should be sent without copying.

Session.debug : Bool
    Default: `False`

    Debug output in the Session

Session.digest_history_size : Integer
    Default: `65536`

    The maximum number of digests to remember.
    
    The digest history will be culled when it exceeds this value.


Session.item_threshold : Integer
    Default: `64`

    The maximum number of items for a container to be introspected for custom serialization.
    Containers larger than this are pickled outright.


Session.key : CBytes
    Default: `''`

    execution key, for signing messages.

Session.keyfile : Unicode
    Default: `''`

    path to file containing execution key.

Session.metadata : Dict
    Default: `{}`

    Metadata dictionary, which serves as the default top-level metadata dict for each message.

Session.packer : DottedObjectName
    Default: `'json'`

    The name of the packer for serializing messages.
    Should be one of 'json', 'pickle', or an import name
    for a custom callable serializer.

Session.session : CUnicode
    Default: `u''`

    The UUID identifying this session.

Session.signature_scheme : Unicode
    Default: `'hmac-sha256'`

    The digest scheme used to construct the message signatures.
    Must have the form 'hmac-HASH'.

Session.unpacker : DottedObjectName
    Default: `'json'`

    The name of the unpacker for unserializing messages.
    Only used with custom functions for `packer`.

Session.username : Unicode
    Default: `u'minrk'`

    Username for the Session. Default is your system username.

MappingKernelManager.default_kernel_name : Unicode
    Default: `'python2'`

    The name of the default kernel to start

MappingKernelManager.kernel_manager_class : DottedObjectName
    Default: `'IPython.kernel.ioloop.IOLoopKernelManager'`

    The kernel manager class.  This is configurable to allow
    subclassing of the KernelManager for customized behavior.


MappingKernelManager.root_dir : Unicode
    Default: `u''`

    No description

ContentsManager.checkpoints : Instance
    No description

ContentsManager.checkpoints_class : Type
    Default: `<class 'IPython.html.services.contents.checkpoints.Checkpoints'>`

    No description

ContentsManager.checkpoints_kwargs : Dict
    Default: `{}`

    No description

ContentsManager.hide_globs : List
    Default: `[u'__pycache__', '*.pyc', '*.pyo', '.DS_Store', '*.so', '*.dy...`

    
    Glob patterns to hide in file and directory listings.


ContentsManager.pre_save_hook : Any
    Python callable or importstring thereof
    
    To be called on a contents model prior to save.
    
    This can be used to process the structure,
    such as removing notebook outputs or other side effects that
    should not be saved.
    
    It will be called as (all arguments passed by keyword)::
    
        hook(path=path, model=model, contents_manager=self)
    
    - model: the model to be saved. Includes file contents.
      Modifying this dict will affect the file that is stored.
    - path: the API path of the save destination
    - contents_manager: this ContentsManager instance


ContentsManager.untitled_directory : Unicode
    Default: `'Untitled Folder'`

    The base name used when creating untitled directories.

ContentsManager.untitled_file : Unicode
    Default: `'untitled'`

    The base name used when creating untitled files.

ContentsManager.untitled_notebook : Unicode
    Default: `'Untitled'`

    The base name used when creating untitled notebooks.

FileContentsManager.checkpoints : Instance
    No description

FileContentsManager.checkpoints_class : Type
    Default: `<class 'IPython.html.services.contents.checkpoints.Checkpoints'>`

    No description

FileContentsManager.checkpoints_kwargs : Dict
    Default: `{}`

    No description

FileContentsManager.hide_globs : List
    Default: `[u'__pycache__', '*.pyc', '*.pyo', '.DS_Store', '*.so', '*.dy...`

    
    Glob patterns to hide in file and directory listings.


FileContentsManager.post_save_hook : Any
    Python callable or importstring thereof
    
    to be called on the path of a file just saved.
    
    This can be used to process the file on disk,
    such as converting the notebook to a script or HTML via nbconvert.
    
    It will be called as (all arguments passed by keyword)::
    
        hook(os_path=os_path, model=model, contents_manager=instance)
    
    - path: the filesystem path to the file just written
    - model: the model representing the file
    - contents_manager: this ContentsManager instance


FileContentsManager.pre_save_hook : Any
    Python callable or importstring thereof
    
    To be called on a contents model prior to save.
    
    This can be used to process the structure,
    such as removing notebook outputs or other side effects that
    should not be saved.
    
    It will be called as (all arguments passed by keyword)::
    
        hook(path=path, model=model, contents_manager=self)
    
    - model: the model to be saved. Includes file contents.
      Modifying this dict will affect the file that is stored.
    - path: the API path of the save destination
    - contents_manager: this ContentsManager instance


FileContentsManager.root_dir : Unicode
    Default: `u''`

    No description

FileContentsManager.save_script : Bool
    Default: `False`

    DEPRECATED, use post_save_hook

FileContentsManager.untitled_directory : Unicode
    Default: `'Untitled Folder'`

    The base name used when creating untitled directories.

FileContentsManager.untitled_file : Unicode
    Default: `'untitled'`

    The base name used when creating untitled files.

FileContentsManager.untitled_notebook : Unicode
    Default: `'Untitled'`

    The base name used when creating untitled notebooks.

NotebookNotary.algorithm : 'sha1'|'sha224'|'sha384'|'sha256'|'sha512'|'md5'
    Default: `'sha256'`

    The hashing algorithm used to sign notebooks.

NotebookNotary.cache_size : Integer
    Default: `65535`

    The number of notebook signatures to cache.
    When the number of signatures exceeds this value,
    the oldest 25% of signatures will be culled.


NotebookNotary.db_file : Unicode
    Default: `u''`

    The sqlite file in which to store notebook signatures.
    By default, this will be in your IPython profile.
    You can set it to ':memory:' to disable sqlite writing to the filesystem.


NotebookNotary.secret : Bytes
    Default: `''`

    The secret key with which notebooks are signed.

NotebookNotary.secret_file : Unicode
    Default: `u''`

    The file where the secret key is stored.

KernelSpecManager.whitelist : Set
    Default: `set([])`

    Whitelist of allowed kernel names.
    
    By default, all installed kernels are allowed.

