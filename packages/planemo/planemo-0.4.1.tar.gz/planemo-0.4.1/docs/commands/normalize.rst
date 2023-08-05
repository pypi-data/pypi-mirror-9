
``normalize`` command
===============================

This section is auto-generated from the help text for the planemo command
``normalize``. This help message can be generated with ``planemo normalize
--help``.

**Usage**::

    planemo normalize [OPTIONS] TOOL_PATH

**Help**

Generate normalized tool XML from input.

The top-level blocks will be reordered and whitespace fixed according to
the tool development best practices outlined on the Galaxy wiki.

See also https://wiki.galaxyproject.org/Tools/BestPractices.

::

    % # Print normalized version of tool.
    % planemo normalize tool.xml
    <tool>
    ...
    % # Print a variant of tool with all macros expanded out, useful for
    % # debugging complex macros.
    % planemo normalize --expand_macros tool.xml
    <tool>
    ...

**Options**::


      --expand_macros  Expand macros while normalizing tool XML - useful to see
                       how macros are evaluated.
      --skip_reorder   Planemo will reorder top-level tool blocks according to
                       tool development best practices as part of this command,
                       this flag will disable that behavior.
      --skip_reindent  Planemo will reindent the XML according to tool development
                       best practices as part of this command, this flag will
                       disable that behavior.
      --help           Show this message and exit.
    
