Terminal IPython options
========================

InteractiveShellApp.code_to_run : Unicode
    Default: `''`

    Execute the given command string.

InteractiveShellApp.exec_PYTHONSTARTUP : Bool
    Default: `True`

    Run the file referenced by the PYTHONSTARTUP environment
    variable at IPython startup.

InteractiveShellApp.exec_files : List
    Default: `[]`

    List of files to run at IPython startup.

InteractiveShellApp.exec_lines : List
    Default: `[]`

    lines of code to run at IPython startup.

InteractiveShellApp.extensions : List
    Default: `[]`

    A list of dotted module names of IPython extensions to load.

InteractiveShellApp.extra_extension : Unicode
    Default: `''`

    dotted module name of an IPython extension to load.

InteractiveShellApp.file_to_run : Unicode
    Default: `''`

    A file to be run

InteractiveShellApp.gui : 'glut'|'gtk'|'gtk3'|'osx'|'pyglet'|'qt'|'qt5'|'tk'|'wx'
    Enable GUI event loop integration with any of ('glut', 'gtk', 'gtk3', 'osx', 'pyglet', 'qt', 'qt5', 'tk', 'wx').

InteractiveShellApp.hide_initial_ns : Bool
    Default: `True`

    Should variables loaded at startup (by startup files, exec_lines, etc.)
    be hidden from tools like %who?

InteractiveShellApp.matplotlib : 'auto'|'gtk'|'gtk3'|'inline'|'nbagg'|'notebook'|'osx'|'qt'|'qt4'|'qt5'|'tk'|'wx'
    Configure matplotlib for interactive use with
    the default matplotlib backend.

InteractiveShellApp.module_to_run : Unicode
    Default: `''`

    Run the module as a script.

InteractiveShellApp.pylab : 'auto'|'gtk'|'gtk3'|'inline'|'nbagg'|'notebook'|'osx'|'qt'|'qt4'|'qt5'|'tk'|'wx'
    Pre-load matplotlib and numpy for interactive use,
    selecting a particular matplotlib backend and loop integration.


InteractiveShellApp.pylab_import_all : Bool
    Default: `True`

    If true, IPython will populate the user namespace with numpy, pylab, etc.
    and an ``import *`` is done from numpy and pylab, when using pylab mode.
    
    When False, pylab mode should not import any names into the user namespace.


InteractiveShellApp.reraise_ipython_extension_failures : Bool
    Default: `False`

    Reraise exceptions encountered loading IPython extensions?

TerminalIPythonApp.code_to_run : Unicode
    Default: `''`

    Execute the given command string.

TerminalIPythonApp.copy_config_files : Bool
    Default: `False`

    Whether to install the default config files into the profile dir.
    If a new profile is being created, and IPython contains config files for that
    profile, then they will be staged into the new directory.  Otherwise,
    default config files will be automatically generated.


TerminalIPythonApp.display_banner : Bool
    Default: `True`

    Whether to display a banner upon starting IPython.

TerminalIPythonApp.exec_PYTHONSTARTUP : Bool
    Default: `True`

    Run the file referenced by the PYTHONSTARTUP environment
    variable at IPython startup.

TerminalIPythonApp.exec_files : List
    Default: `[]`

    List of files to run at IPython startup.

TerminalIPythonApp.exec_lines : List
    Default: `[]`

    lines of code to run at IPython startup.

TerminalIPythonApp.extensions : List
    Default: `[]`

    A list of dotted module names of IPython extensions to load.

TerminalIPythonApp.extra_config_file : Unicode
    Default: `u''`

    Path to an extra config file to load.
    
    If specified, load this config file in addition to any other IPython config.


TerminalIPythonApp.extra_extension : Unicode
    Default: `''`

    dotted module name of an IPython extension to load.

TerminalIPythonApp.file_to_run : Unicode
    Default: `''`

    A file to be run

TerminalIPythonApp.force_interact : Bool
    Default: `False`

    If a command or file is given via the command-line,
    e.g. 'ipython foo.py', start an interactive shell after executing the
    file or command.

TerminalIPythonApp.gui : 'glut'|'gtk'|'gtk3'|'osx'|'pyglet'|'qt'|'qt5'|'tk'|'wx'
    Enable GUI event loop integration with any of ('glut', 'gtk', 'gtk3', 'osx', 'pyglet', 'qt', 'qt5', 'tk', 'wx').

TerminalIPythonApp.hide_initial_ns : Bool
    Default: `True`

    Should variables loaded at startup (by startup files, exec_lines, etc.)
    be hidden from tools like %who?

TerminalIPythonApp.ignore_old_config : Bool
    Default: `False`

    Suppress warning messages about legacy config files

TerminalIPythonApp.ipython_dir : Unicode
    Default: `u''`

    
    The name of the IPython directory. This directory is used for logging
    configuration (through profiles), history storage, etc. The default
    is usually $HOME/.ipython. This option can also be specified through
    the environment variable IPYTHONDIR.


TerminalIPythonApp.log_datefmt : Unicode
    Default: `'%Y-%m-%d %H:%M:%S'`

    The date format used by logging formatters for %(asctime)s

TerminalIPythonApp.log_format : Unicode
    Default: `'[%(name)s]%(highlevel)s %(message)s'`

    The Logging format template

TerminalIPythonApp.log_level : 0|10|20|30|40|50|'DEBUG'|'INFO'|'WARN'|'ERROR'|'CRITICAL'
    Default: `30`

    Set the log level by value or name.

TerminalIPythonApp.matplotlib : 'auto'|'gtk'|'gtk3'|'inline'|'nbagg'|'notebook'|'osx'|'qt'|'qt4'|'qt5'|'tk'|'wx'
    Configure matplotlib for interactive use with
    the default matplotlib backend.

TerminalIPythonApp.module_to_run : Unicode
    Default: `''`

    Run the module as a script.

TerminalIPythonApp.overwrite : Bool
    Default: `False`

    Whether to overwrite existing config files when copying

TerminalIPythonApp.profile : Unicode
    Default: `u'default'`

    The IPython profile to use.

TerminalIPythonApp.pylab : 'auto'|'gtk'|'gtk3'|'inline'|'nbagg'|'notebook'|'osx'|'qt'|'qt4'|'qt5'|'tk'|'wx'
    Pre-load matplotlib and numpy for interactive use,
    selecting a particular matplotlib backend and loop integration.


TerminalIPythonApp.pylab_import_all : Bool
    Default: `True`

    If true, IPython will populate the user namespace with numpy, pylab, etc.
    and an ``import *`` is done from numpy and pylab, when using pylab mode.
    
    When False, pylab mode should not import any names into the user namespace.


TerminalIPythonApp.quick : Bool
    Default: `False`

    Start IPython quickly by skipping the loading of config files.

TerminalIPythonApp.reraise_ipython_extension_failures : Bool
    Default: `False`

    Reraise exceptions encountered loading IPython extensions?

TerminalIPythonApp.verbose_crash : Bool
    Default: `False`

    Create a massive crash report when IPython encounters what may be an
    internal error.  The default is to append a short message to the
    usual traceback

TerminalInteractiveShell.ast_node_interactivity : 'all'|'last'|'last_expr'|'none'
    Default: `'last_expr'`

    
    'all', 'last', 'last_expr' or 'none', specifying which nodes should be
    run interactively (displaying output from expressions).

TerminalInteractiveShell.ast_transformers : List
    Default: `[]`

    
    A list of ast.NodeTransformer subclass instances, which will be applied
    to user input before code is run.


TerminalInteractiveShell.autocall : 0|1|2
    Default: `0`

    
    Make IPython automatically call any callable object even if you didn't
    type explicit parentheses. For example, 'str 43' becomes 'str(43)'
    automatically. The value can be '0' to disable the feature, '1' for
    'smart' autocall, where it is not applied if there are no more
    arguments on the line, and '2' for 'full' autocall, where all callable
    objects are automatically called (even if no arguments are present).


TerminalInteractiveShell.autoedit_syntax : CBool
    Default: `False`

    auto editing of files with syntax errors.

TerminalInteractiveShell.autoindent : CBool
    Default: `True`

    
    Autoindent IPython code entered interactively.


TerminalInteractiveShell.automagic : CBool
    Default: `True`

    
    Enable magic commands to be called without the leading %.


TerminalInteractiveShell.banner1 : Unicode
    Default: `'Python 2.7.9 |Continuum Analytics, Inc.| (default, Dec 15 20...`

    The part of the banner to be printed before the profile

TerminalInteractiveShell.banner2 : Unicode
    Default: `''`

    The part of the banner to be printed after the profile

TerminalInteractiveShell.cache_size : Integer
    Default: `1000`

    
    Set the size of the output cache.  The default is 1000, you can
    change it permanently in your config file.  Setting it to 0 completely
    disables the caching system, and the minimum value accepted is 20 (if
    you provide a value less than 20, it is reset to 0 and a warning is
    issued).  This limit is defined because otherwise you'll spend more
    time re-flushing a too small cache than working


TerminalInteractiveShell.color_info : CBool
    Default: `True`

    
    Use colors for displaying information about objects. Because this
    information is passed through a pager (like 'less'), and some pagers
    get confused with color codes, this capability can be turned off.


TerminalInteractiveShell.colors : 'NoColor'|'LightBG'|'Linux'
    Default: `'LightBG'`

    Set the color scheme (NoColor, Linux, or LightBG).

TerminalInteractiveShell.confirm_exit : CBool
    Default: `True`

    
    Set to confirm when you try to exit IPython with an EOF (Control-D
    in Unix, Control-Z/Enter in Windows). By typing 'exit' or 'quit',
    you can force a direct exit without any confirmation.

TerminalInteractiveShell.debug : CBool
    Default: `False`

    No description

TerminalInteractiveShell.deep_reload : CBool
    Default: `False`

    
    Enable deep (recursive) reloading by default. IPython can use the
    deep_reload module which reloads changes in modules recursively (it
    replaces the reload() function, so you don't need to change anything to
    use it). deep_reload() forces a full reload of modules whose code may
    have changed, which the default reload() function does not.  When
    deep_reload is off, IPython will use the normal reload(), but
    deep_reload will still be available as dreload().


TerminalInteractiveShell.disable_failing_post_execute : CBool
    Default: `False`

    Don't call post-execute functions that have failed in the past.

TerminalInteractiveShell.display_page : Bool
    Default: `False`

    If True, anything that would be passed to the pager
    will be displayed as regular output instead.

TerminalInteractiveShell.editor : Unicode
    Default: `u'mate -w'`

    Set the editor used by IPython (default to $EDITOR/vi/notepad).

TerminalInteractiveShell.history_length : Integer
    Default: `10000`

    No description

TerminalInteractiveShell.ipython_dir : Unicode
    Default: `''`

    No description

TerminalInteractiveShell.logappend : Unicode
    Default: `''`

    
    Start logging to the given file in append mode.
    Use `logfile` to specify a log file to **overwrite** logs to.


TerminalInteractiveShell.logfile : Unicode
    Default: `''`

    
    The name of the logfile to use.


TerminalInteractiveShell.logstart : CBool
    Default: `False`

    
    Start logging to the default log file in overwrite mode.
    Use `logappend` to specify a log file to **append** logs to.


TerminalInteractiveShell.multiline_history : CBool
    Default: `True`

    Save multi-line entries as one entry in readline history

TerminalInteractiveShell.object_info_string_level : 0|1|2
    Default: `0`

    No description

TerminalInteractiveShell.pager : Unicode
    Default: `'less'`

    The shell program to be used for paging.

TerminalInteractiveShell.pdb : CBool
    Default: `False`

    
    Automatically call the pdb debugger after every exception.


TerminalInteractiveShell.prompt_in1 : Unicode
    Default: `'In [\\#]: '`

    Deprecated, use PromptManager.in_template

TerminalInteractiveShell.prompt_in2 : Unicode
    Default: `'   .\\D.: '`

    Deprecated, use PromptManager.in2_template

TerminalInteractiveShell.prompt_out : Unicode
    Default: `'Out[\\#]: '`

    Deprecated, use PromptManager.out_template

TerminalInteractiveShell.prompts_pad_left : CBool
    Default: `True`

    Deprecated, use PromptManager.justify

TerminalInteractiveShell.quiet : CBool
    Default: `False`

    No description

TerminalInteractiveShell.readline_parse_and_bind : List
    Default: `['tab: complete', '"\\C-l": clear-screen', 'set show-all-if-a...`

    No description

TerminalInteractiveShell.readline_remove_delims : Unicode
    Default: `'-/~'`

    No description

TerminalInteractiveShell.readline_use : CBool
    Default: `True`

    No description

TerminalInteractiveShell.screen_length : Integer
    Default: `0`

    Number of lines of your screen, used to control printing of very
    long strings.  Strings longer than this number of lines will be sent
    through a pager instead of directly printed.  The default value for
    this is 0, which means IPython will auto-detect your screen size every
    time it needs to print certain potentially long strings (this doesn't
    change the behavior of the 'print' keyword, it's only triggered
    internally). If for some reason this isn't working well (it needs
    curses support), specify it yourself. Otherwise don't change the
    default.

TerminalInteractiveShell.separate_in : SeparateUnicode
    Default: `'\\n'`

    No description

TerminalInteractiveShell.separate_out : SeparateUnicode
    Default: `''`

    No description

TerminalInteractiveShell.separate_out2 : SeparateUnicode
    Default: `''`

    No description

TerminalInteractiveShell.show_rewritten_input : CBool
    Default: `True`

    Show rewritten input, e.g. for autocall.

TerminalInteractiveShell.term_title : CBool
    Default: `False`

    Enable auto setting the terminal title.

TerminalInteractiveShell.wildcards_case_sensitive : CBool
    Default: `True`

    No description

TerminalInteractiveShell.xmode : 'Context'|'Plain'|'Verbose'
    Default: `'Context'`

    No description

PromptManager.color_scheme : Unicode
    Default: `'Linux'`

    No description

PromptManager.in2_template : Unicode
    Default: `'   .\\D.: '`

    Continuation prompt.

PromptManager.in_template : Unicode
    Default: `'In [\\#]: '`

    Input prompt.  '\#' will be transformed to the prompt number

PromptManager.justify : Bool
    Default: `True`

    
    If True (default), each prompt will be right-aligned with the
    preceding one.


PromptManager.out_template : Unicode
    Default: `'Out[\\#]: '`

    Output prompt. '\#' will be transformed to the prompt number

HistoryManager.connection_options : Dict
    Default: `{}`

    Options for configuring the SQLite connection
    
    These options are passed as keyword args to sqlite3.connect
    when establishing database conenctions.


HistoryManager.db_cache_size : Integer
    Default: `0`

    Write to database every x commands (higher values save disk access & power).
    Values of 1 or less effectively disable caching.

HistoryManager.db_log_output : Bool
    Default: `False`

    Should the history database include output? (default: no)

HistoryManager.enabled : Bool
    Default: `True`

    enable the SQLite history
    
    set enabled=False to disable the SQLite history,
    in which case there will be no stored history, no SQLite connection,
    and no background saving thread.  This may be necessary in some
    threaded environments where IPython is embedded.


HistoryManager.hist_file : Unicode
    Default: `u''`

    Path to file to use for SQLite history database.
    
    By default, IPython will put the history database in the IPython
    profile directory.  If you would rather share one history among
    profiles, you can set this value in each, so that they are consistent.
    
    Due to an issue with fcntl, SQLite is known to misbehave on some NFS
    mounts.  If you see IPython hanging, try setting this to something on a
    local disk, e.g::
    
        ipython --HistoryManager.hist_file=/tmp/ipython_hist.sqlite
    


ProfileDir.location : Unicode
    Default: `u''`

    Set the profile location directly. This overrides the logic used by the
    `profile` option.

PlainTextFormatter.deferred_printers : Dict
    Default: `{}`

    No description

PlainTextFormatter.float_precision : CUnicode
    Default: `''`

    No description

PlainTextFormatter.max_seq_length : Integer
    Default: `1000`

    Truncate large collections (lists, dicts, tuples, sets) to this size.
    
    Set to 0 to disable truncation.


PlainTextFormatter.max_width : Integer
    Default: `79`

    No description

PlainTextFormatter.newline : Unicode
    Default: `'\\n'`

    No description

PlainTextFormatter.pprint : Bool
    Default: `True`

    No description

PlainTextFormatter.singleton_printers : Dict
    Default: `{}`

    No description

PlainTextFormatter.type_printers : Dict
    Default: `{}`

    No description

PlainTextFormatter.verbose : Bool
    Default: `False`

    No description

IPCompleter.greedy : CBool
    Default: `False`

    Activate greedy completion
    
    This will enable completion on elements of lists, results of function calls, etc.,
    but can be unsafe because the code is actually evaluated on TAB.


IPCompleter.limit_to__all__ : CBool
    Default: `False`

    Instruct the completer to use __all__ for the completion
    
    Specifically, when completing on ``object.<tab>``.
    
    When True: only those names in obj.__all__ will be included.
    
    When False [default]: the __all__ attribute is ignored 


IPCompleter.merge_completions : CBool
    Default: `True`

    Whether to merge completion results into a single list
    
    If False, only the completion results from the first non-empty
    completer will be returned.


IPCompleter.omit__names : 0|1|2
    Default: `2`

    Instruct the completer to omit private method names
    
    Specifically, when completing on ``object.<tab>``.
    
    When 2 [default]: all names that start with '_' will be excluded.
    
    When 1: all 'magic' names (``__foo__``) will be excluded.
    
    When 0: nothing will be excluded.


ScriptMagics.script_magics : List
    Default: `[]`

    Extra script cell magics to define
    
    This generates simple wrappers of `%%script foo` as `%%foo`.
    
    If you want to add script magics that aren't on your path,
    specify them in script_paths


ScriptMagics.script_paths : Dict
    Default: `{}`

    Dict mapping short 'ruby' names to full paths, such as '/opt/secret/bin/ruby'
    
    Only necessary for items in script_magics where the default path will not
    find the right interpreter.


StoreMagics.autorestore : Bool
    Default: `False`

    If True, any %store-d variables will be automatically restored
    when IPython starts.

