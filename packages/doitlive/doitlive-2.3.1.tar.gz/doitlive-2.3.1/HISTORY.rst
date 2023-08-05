Changelog
---------

2.3.1 (2015-02-08)
******************

- Fix bug that showed the incorrect prompt on the last slide if the theme was set using the ``#doitlive prompt:`` directive.

2.3.0 (2014-11-16)
******************

- Add support for displaying Mercurial VCS info (current branch, bookmark)
- Add ``commentecho`` CLI option and magic comment.
- Add ``--quiet`` CLI option for suppressing the startup message.

2.2.1 (2014-08-02)
******************

- Fix display of git branches on Python 3 (don't show ``b`` prefix).

2.2.0 (2014-07-13)
******************

- Add ``{TTY}`` prompt variable that contains named constants for ANSI escape sequences.
- Add "giddie" theme.
- Add ``help/H`` command to the recorder console.

2.1.0 (2014-06-25)
******************

- Python mode: Fenced code blocks can be played back in a fake Python console.
- Added ability to preview and undo commands during a recorder session.
- Current datetime (``{now}``) can be included in prompt.
- Added 'pws' theme.
- Added ``--envvar`` and ``--alias`` options to ``record`` command.
- Added ``unalias`` and ``unset`` comment directives.


2.0 (2014-06-21)
****************

- Added session recorder (``doitlive record``).
- Improved interface.
- Sessions are played with ``doitlive play <session_file>``.
- Deprecated ``doitlive-demo``. Run ``doitlive demo`` instead.
- Deprecated ``doitlive --themes`` and ``doitlive --themes-preview``. Run ``doitlive themes`` and ``doitlive themes --preview`` instead.
- Fix bug that raised an error when cd'ing into a non-existent directory.
- Remove extra spacing in prompt when not in a git directory.
- Added 'robbyrussell' theme.


1.0 (2014-06-18)
****************

- Added themes!
- Prompt variables can have ANSI colors and styles.
- ``{hostname}`` can be included in prompt.
- ``{git_branch}`` can be included in prompt.
- Prompt variable ``{full_cwd}`` renamed to ``{cwd}``.
- Prompt variable ``{cwd}`` renamed to ``{dir}``.
- Short option for ``--speed`` is now ``-s``.
- Short option for ``--shell`` is now ``-S``.
- Changed default prompt.
- ``run`` and ``magictype`` receive prompt_template instead of a prompt function.
- Remove unnecessary ``PromptState`` class.

0.2.0 (2014-06-16)
******************

- Add "speed" config option.
- Fix short option for "--shell".
- Custom prompts are colored.
- Remove unnecessary --check-output option, which was only used for testing.
- Fix bug where cwd would not update in custom prompts.

0.1.0 (2014-06-15)
******************

- Initial release.
