IPython Qt console options
==========================

To configure the IPython kernel, see :doc:`kernel`.

IPythonQtConsoleApp.auto_create : Bool
    Default: `False`

    Whether to create profile dir if it doesn't exist

IPythonQtConsoleApp.confirm_exit : CBool
    Default: `True`

    
    Set to display confirmation dialog on exit. You can always use 'exit' or 'quit',
    to force a direct exit without any confirmation.

IPythonQtConsoleApp.connection_file : Unicode
    Default: `''`

    JSON file in which to store connection info [default: kernel-<pid>.json]
    
    This file will contain the IP, ports, and authentication key needed to connect
    clients to this kernel. By default, this file will be created in the security dir
    of the current profile, but can be specified by absolute path.


IPythonQtConsoleApp.control_port : Integer
    Default: `0`

    set the control (ROUTER) port [default: random]

IPythonQtConsoleApp.copy_config_files : Bool
    Default: `False`

    Whether to install the default config files into the profile dir.
    If a new profile is being created, and IPython contains config files for that
    profile, then they will be staged into the new directory.  Otherwise,
    default config files will be automatically generated.


IPythonQtConsoleApp.display_banner : CBool
    Default: `True`

    Whether to display a banner upon starting the QtConsole.

IPythonQtConsoleApp.existing : CUnicode
    Default: `''`

    Connect to an already running kernel

IPythonQtConsoleApp.extra_config_file : Unicode
    Default: `u''`

    Path to an extra config file to load.
    
    If specified, load this config file in addition to any other IPython config.


IPythonQtConsoleApp.hb_port : Integer
    Default: `0`

    set the heartbeat port [default: random]

IPythonQtConsoleApp.hide_menubar : CBool
    Default: `False`

    Start the console window with the menu bar hidden.

IPythonQtConsoleApp.iopub_port : Integer
    Default: `0`

    set the iopub (PUB) port [default: random]

IPythonQtConsoleApp.ip : Unicode
    Default: `u''`

    Set the kernel's IP address [default localhost].
    If the IP address is something other than localhost, then
    Consoles on other machines will be able to connect
    to the Kernel, so be careful!

IPythonQtConsoleApp.ipython_dir : Unicode
    Default: `u''`

    
    The name of the IPython directory. This directory is used for logging
    configuration (through profiles), history storage, etc. The default
    is usually $HOME/.ipython. This option can also be specified through
    the environment variable IPYTHONDIR.


IPythonQtConsoleApp.kernel_name : Unicode
    Default: `'python'`

    The name of the default kernel to start.

IPythonQtConsoleApp.log_datefmt : Unicode
    Default: `'%Y-%m-%d %H:%M:%S'`

    The date format used by logging formatters for %(asctime)s

IPythonQtConsoleApp.log_format : Unicode
    Default: `'[%(name)s]%(highlevel)s %(message)s'`

    The Logging format template

IPythonQtConsoleApp.log_level : 0|10|20|30|40|50|'DEBUG'|'INFO'|'WARN'|'ERROR'|'CRITICAL'
    Default: `30`

    Set the log level by value or name.

IPythonQtConsoleApp.maximize : CBool
    Default: `False`

    Start the console window maximized.

IPythonQtConsoleApp.overwrite : Bool
    Default: `False`

    Whether to overwrite existing config files when copying

IPythonQtConsoleApp.plain : CBool
    Default: `False`

    Use a plaintext widget instead of rich text (plain can't print/save).

IPythonQtConsoleApp.profile : Unicode
    Default: `u'default'`

    The IPython profile to use.

IPythonQtConsoleApp.shell_port : Integer
    Default: `0`

    set the shell (ROUTER) port [default: random]

IPythonQtConsoleApp.sshkey : Unicode
    Default: `''`

    Path to the ssh key to use for logging in to the ssh server.

IPythonQtConsoleApp.sshserver : Unicode
    Default: `''`

    The SSH server to use to connect to the kernel.

IPythonQtConsoleApp.stdin_port : Integer
    Default: `0`

    set the stdin (ROUTER) port [default: random]

IPythonQtConsoleApp.stylesheet : Unicode
    Default: `''`

    path to a custom CSS stylesheet

IPythonQtConsoleApp.transport : 'tcp'|'ipc'
    Default: `'tcp'`

    No description

IPythonQtConsoleApp.verbose_crash : Bool
    Default: `False`

    Create a massive crash report when IPython encounters what may be an
    internal error.  The default is to append a short message to the
    usual traceback

IPythonWidget.ansi_codes : Bool
    Default: `True`

    Whether to process ANSI escape codes.

IPythonWidget.banner : Unicode
    Default: `u''`

    No description

IPythonWidget.buffer_size : Integer
    Default: `500`

    
    The maximum number of lines of text before truncation. Specifying a
    non-positive number disables text truncation (not recommended).


IPythonWidget.clear_on_kernel_restart : Bool
    Default: `True`

    Whether to clear the console when the kernel is restarted

IPythonWidget.confirm_restart : Bool
    Default: `True`

    Whether to ask for user confirmation when restarting kernel

IPythonWidget.editor : Unicode
    Default: `''`

    
    A command for invoking a system text editor. If the string contains a
    {filename} format specifier, it will be used. Otherwise, the filename
    will be appended to the end the command.


IPythonWidget.editor_line : Unicode
    Default: `u''`

    
    The editor command to use when a specific line number is requested. The
    string should contain two format specifiers: {line} and {filename}. If
    this parameter is not specified, the line number option to the %edit
    magic will be ignored.


IPythonWidget.enable_calltips : Bool
    Default: `True`

    Whether to draw information calltips on open-parentheses.

IPythonWidget.execute_on_complete_input : Bool
    Default: `True`

    Whether to automatically execute on syntactically complete input.
    
    If False, Shift-Enter is required to submit each execution.
    Disabling this is mainly useful for non-Python kernels,
    where the completion check would be wrong.


IPythonWidget.font_family : Unicode
    Default: `u''`

    The font family to use for the console.
    On OSX this defaults to Monaco, on Windows the default is
    Consolas with fallback of Courier, and on other platforms
    the default is Monospace.


IPythonWidget.font_size : Integer
    Default: `0`

    The font size. If unconfigured, Qt will be entrusted
    with the size of the font.


IPythonWidget.gui_completion : 'plain'|'droplist'|'ncurses'
    Default: `'ncurses'`

    
    The type of completer to use. Valid values are:
    
    'plain'   : Show the available completion as a text list
                Below the editing area.
    'droplist': Show the completion in a drop down list navigable
                by the arrow keys, and from which you can select
                completion by pressing Return.
    'ncurses' : Show the completion as a text list which is navigable by
                `tab` and arrow keys.


IPythonWidget.height : Integer
    Default: `25`

    The height of the console at start time in number
    of characters (will double with `vsplit` paging)


IPythonWidget.history_lock : Bool
    Default: `False`

    No description

IPythonWidget.in_prompt : Unicode
    Default: `'In [<span class="in-prompt-number">%i</span>]: '`

    No description

IPythonWidget.include_other_output : Bool
    Default: `False`

    Whether to include output from clients
    other than this one sharing the same kernel.
    
    Outputs are not displayed until enter is pressed.


IPythonWidget.input_sep : Unicode
    Default: `'\\n'`

    No description

IPythonWidget.kind : 'plain'|'rich'
    Default: `'plain'`

    
    The type of underlying text widget to use. Valid values are 'plain',
    which specifies a QPlainTextEdit, and 'rich', which specifies a
    QTextEdit.


IPythonWidget.lexer_class : DottedObjectName
    Default: `<IPython.utils.traitlets.Undefined object at 0x101ee8310>`

    The pygments lexer class to use.

IPythonWidget.out_prompt : Unicode
    Default: `'Out[<span class="out-prompt-number">%i</span>]: '`

    No description

IPythonWidget.output_sep : Unicode
    Default: `''`

    No description

IPythonWidget.output_sep2 : Unicode
    Default: `''`

    No description

IPythonWidget.paging : 'inside'|'hsplit'|'vsplit'|'custom'|'none'
    Default: `'inside'`

    
    The type of paging to use. Valid values are:
    
    'inside'
       The widget pages like a traditional terminal.
    'hsplit'
       When paging is requested, the widget is split horizontally. The top
       pane contains the console, and the bottom pane contains the paged text.
    'vsplit'
       Similar to 'hsplit', except that a vertical splitter is used.
    'custom'
       No action is taken by the widget beyond emitting a
       'custom_page_requested(str)' signal.
    'none'
       The text is written directly to the console.


IPythonWidget.style_sheet : Unicode
    Default: `u''`

    
    A CSS stylesheet. The stylesheet can contain classes for:
        1. Qt: QPlainTextEdit, QFrame, QWidget, etc
        2. Pygments: .c, .k, .o, etc. (see PygmentsHighlighter)
        3. IPython: .error, .in-prompt, .out-prompt, etc


IPythonWidget.syntax_style : Unicode
    Default: `u''`

    
    If not empty, use this Pygments style for syntax highlighting.
    Otherwise, the style sheet is queried for Pygments style
    information.


IPythonWidget.width : Integer
    Default: `81`

    The width of the console at start time in number
    of characters (will double with `hsplit` paging)


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
