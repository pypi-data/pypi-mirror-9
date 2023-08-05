import os, sys

def default_editor():
    """If no editors are specified in .edi.yml, somehow figure out what constitutes a default editor."""

    # Standard UNIX environment variables to set the editor.
    visual_env_var = os.environ.get("VISUAL")
    if visual_env_var:
        return visual_env_var + " {0}"

    editor_var = os.environ.get("EDITOR")
    if editor_var:
        return editor + " {0}"

    # TODO: Need to use something like this to get default Mac OS text editor:
    # defaults write com.apple.LaunchServices LSHandlers -array-add '{LSHandlerContentType=public.plain-text;LSHandlerRoleAll=com.sublimetext.3;}'

    # Ubuntu defaults for if X windows is enabled or if only terminal is available
    if os.environ.get("DISPLAY"):
        if os.path.exists("/usr/bin/gnome-text-editor"):
            return "gnome-text-editor {0}"
    else:
        if os.path.exists("/usr/bin/editor"):
            return "editor {0}"

    # Last resort
    return "vi {0}"
