Pretending python is a shell
============================

We all like python for scripting, because it's so much more powerful than a
shell. But sometimes we really need to call a shell command because it's so
much easier than writing yet another library in python or adding a dependency::

  from whelk import shell
  shell.zgrep("-r", "downloads", "/var/log/httpd")
  # Here goes code to process the log

You can even pipe commands together::

  from whelk import pipe
  pipe(pipe.getent("group") | pipe.grep(":1...:"))

Much more usage info can de found at http://seveas.github.io/whelk/

Installing
----------

Installing the latest released version is as simple as::

  pip install whelk

If you want to tinker with the source, you can install the latest source from
github::

  git clone https://github.com/seveas/whelk.git

And finally, Ubuntu users can install whelk from my ppa::

  sudo apt-add-repository ppa:dennis/python
  sudo apt-get update
  sudo apt-get install python-whelk python3-whelk

License
-------

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
version 3, as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
