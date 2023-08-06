r2pipe for Python
=================

Interact with radare2 using the #!pipe command or in standalone scripts
that communicate with local or remoate r2 via pipe, tcp or http.

Usage example:

	$ python
	> import r2pipe
	> r2 = r2pipe.open("/bin/ls")
	> print(r2.cmd("pd 10"))

*Author*: pancake <pancake@nopcode.org>
*Project*: http://www.radare.org/
