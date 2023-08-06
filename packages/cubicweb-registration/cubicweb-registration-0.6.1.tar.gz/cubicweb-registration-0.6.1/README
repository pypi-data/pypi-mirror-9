This CubicWeb component provides a public registration feature (users
can register and create an account without the need for admin
intervention).

To activate the user registration feature in your CubicWeb
application, just add this cube in your instance ; either depend on it
in your cube's __pkginfo__ or run the ``add_cude`` command in a
CubicWeb shell::

  $ cubicwebctl shell youapp
  entering the migration python shell
  just type migration commands or arbitrary python code and type ENTER to execute it
  type "exit" or Ctrl-D to quit the shell and resume operation
  >>> add_cube('registration')
  >>> ^D


Then add or modify the ``registration-cypher-seed`` configuration
option in your application's ``all-in-one.conf`` file:

  [REGISTRATION]

  # seed used to cypher registration data in confirmation email link
  registration-cypher-seed=<change me>


