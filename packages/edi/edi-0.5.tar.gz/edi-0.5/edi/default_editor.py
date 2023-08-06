import os, sys

def default_editor():
    """If no editors are specified in .edi.yml, somehow figure out what constitutes a default editor."""

    # Standard UNIX environment variables to set the editor. These should be used first.
    visual_env_var = os.environ.get("VISUAL")
    if visual_env_var:
        return visual_env_var + " {0}"

    editor_var = os.environ.get("EDITOR")
    if editor_var:
        return editor + " {0}"

    # Windows-based system.
    windows = 'win32' in str(sys.platform).lower()
    
    # OS based system
    osx = 'darwin' in str(sys.platform).lower()
    
    # Various over unices
    linux = 'linux' in str(sys.platform).lower()
    hpux = 'hpux' in str(sys.platform).lower()
    solaris = 'sunos' in str(sys.platform).lower()
    cygwin = 'cygwin' in str(sys.platform).lower()
    
    if osx:
        return "open {0}"
    elif linux or cygwin or solaris or hpux:
        # Ubuntu defaults for if X windows is enabled or if only terminal is available
        if os.path.exists("/usr/bin/gnome-text-editor"):
            return "gnome-text-editor {0}"
        elif os.path.exists("/usr/bin/editor"):
            return "editor {0}"
        else:
            return "vi {0}"
    else:
        # Last resort
        return "vi {0}"
