Release History
===============

0.1.2 (2015-02-07)
------------------

*Minor Changes*

- We now remove the ``Connection`` header if it's given to us, as that header
  is not valid in HTTP/2.

*Bugfixes*

- Adds workaround for HTTPie to make our responses look more like urllib3
  responses.

0.1.1 (2015-02-06)
------------------

*Minor Changes*

- Support for HTTP/2 draft 15, and 16. No drop of support for draft 14.
- Updated bundled certificate file.

*Bugfixes *

- Fixed ``AttributeError`` being raised when a PING frame was received, thanks
  to @t2y. (`Issue #79`_)
- Fixed bug where large frames could be incorrectly truncated by the buffered
  socket implementation, thanks to @t2y. (`Issue #80`_)

.. _Issue #79: https://github.com/Lukasa/hyper/issues/79
.. _Issue #80: https://github.com/Lukasa/hyper/issues/80

0.1.0 (2014-08-16)
------------------

*Regressions and Known Bugs*

- Support for Python 3.3 has been temporarily dropped due to features missing
  from the Python 3.3 ``ssl`` module. PyOpenSSL has been identified as a
  replacement, but until NPN support is merged it cannot be used. Python 3.3
  support *will* be re-added when a suitable release of PyOpenSSL is shipped.
- Technically this release also includes support for PyPy and Python 2.7. That
  support is also blocked behind a suitable PyOpenSSL release.

For more information on these regressions, please see `Issue #37`_.

*Major Changes*

- Support for HPACK draft 9.
- Support for HTTP/2 draft 14.
- Support for Sever Push, thanks to @alekstorm. (`Issue #40`_)
- Use a buffered socket to avoid unnecessary syscalls. (`Issue #56`_)
- If `nghttp2`_ is present, use its HPACK encoder for improved speed and
  compression efficiency. (`Issue #60`_)
- Add ``HTTP20Response.gettrailer()`` and ``HTTP20Response.gettrailers()``,
  supporting downloading and examining HTTP trailers. (Discussed in part in
  `Issue #71`_.)

*Bugfixes*

- ``HTTP20Response`` objects are context managers. (`Issue #24`_)
- Pluggable window managers are now correctly informed about the document size.
  (`Issue #26`_)
- Header blocks can no longer be corrupted if read in a different order to the
  one in which they were sent. (`Issue #39`_)
- Default window manager is now smarter about sending WINDOWUPDATE frames.
  (`Issue #41`_ and `Issue #52`_)
- Fixed inverted window sizes. (`Issue #27`_)
- Correct reply to PING frames. (`Issue #48`_)
- Made the wheel universal, befitting a pure-Python package. (`Issue #46`_)
- HPACK encoder correctly encodes header sets with duplicate headers.
  (`Issue #50`_)

.. _Issue #24: https://github.com/Lukasa/hyper/issues/24
.. _Issue #26: https://github.com/Lukasa/hyper/issues/26
.. _Issue #27: https://github.com/Lukasa/hyper/issues/27
.. _Issue #33: https://github.com/Lukasa/hyper/issues/33
.. _Issue #37: https://github.com/Lukasa/hyper/issues/37
.. _Issue #39: https://github.com/Lukasa/hyper/issues/39
.. _Issue #40: https://github.com/Lukasa/hyper/issues/40
.. _Issue #41: https://github.com/Lukasa/hyper/issues/41
.. _Issue #46: https://github.com/Lukasa/hyper/issues/46
.. _Issue #48: https://github.com/Lukasa/hyper/issues/48
.. _Issue #50: https://github.com/Lukasa/hyper/issues/50
.. _Issue #52: https://github.com/Lukasa/hyper/issues/52
.. _Issue #56: https://github.com/Lukasa/hyper/issues/56
.. _Issue #60: https://github.com/Lukasa/hyper/issues/60
.. _Issue #71: https://github.com/Lukasa/hyper/issues/71
.. _nghttp2: https://nghttp2.org/

0.0.4 (2014-03-08)
------------------

- Add logic for pluggable objects to manage the flow-control window for both
  connections and streams.
- Raise new ``HPACKDecodingError`` when we're unable to validly map a
  Huffman-encoded string.
- Correctly respect the HPACK EOS character.

0.0.3 (2014-02-26)
------------------

- Use bundled SSL certificates in addition to the OS ones, which have limited
  platform availability. (`Issue #9`_)
- Connection objects reset to their basic state when they're closed, enabling
  them to be reused. Note that they may not be reused if exceptions are thrown
  when they're in use: you must open a new connection in that situation.
- Connection objects are now context managers. (`Issue #13`_)
- The ``HTTP20Adapter`` correctly reuses connections.
- Stop sending WINDOWUPDATE frames with a zero-size window increment.
- Provide basic functionality for gracelessly closing streams.
- Exhausted streams are now disposed of. (`Issue #14`_)

.. _Issue #9: https://github.com/Lukasa/hyper/issues/9
.. _Issue #13: https://github.com/Lukasa/hyper/issues/13
.. _Issue #14: https://github.com/Lukasa/hyper/issues/14

0.0.2 (2014-02-20)
------------------

- Implemented logging. (`Issue #12`_)
- Stopped HTTP/2.0 special headers appearing in the response headers.
  (`Issue #16`_)
- `HTTP20Connection` objects are now context managers. (`Issue #13`_)
- Response bodies are automatically decompressed. (`Issue #20`_)
- Provide a requests transport adapter. (`Issue #19`_)
- Fix the build status indicator. (`Issue #22`_)


.. _Issue #12: https://github.com/Lukasa/hyper/issues/12
.. _Issue #16: https://github.com/Lukasa/hyper/issues/16
.. _Issue #13: https://github.com/Lukasa/hyper/issues/13
.. _Issue #20: https://github.com/Lukasa/hyper/issues/20
.. _Issue #19: https://github.com/Lukasa/hyper/issues/19
.. _Issue #22: https://github.com/Lukasa/hyper/issues/22

0.0.1 (2014-02-11)
------------------

- Initial Release
- Support for HTTP/2.0 draft 09.
- Support for HPACK draft 05.
- Support for HTTP/2.0 flow control.
- Verifies TLS certificates.
- Support for streaming uploads.
- Support for streaming downloads.
