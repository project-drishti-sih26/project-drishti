"""
Project Drishti — ML Engine package.

CONSOLE ENCODING GUARD — DO NOT REMOVE
--------------------------------------
This cost us a working demo once, so it is worth writing down.

On Windows, `sys.stdout` defaults to the cp1252 code page. A `print()` containing
'Rs.' as the rupee sign (U+20B9) or an em-dash therefore raises
UnicodeEncodeError. When the ML engine was imported in-process by the FastAPI
backend, that exception propagated out of the *logging* statement, aborted
inference, and the trigger service fell through to its heuristic fallback — which
served RANDOM distances. The dashboard rendered them at full confidence with no
indication anything had failed.

So: a diagnostic print must never be able to break a prediction. We reconfigure
the streams to UTF-8 with errors="replace", which makes encoding failure
impossible — at worst a character renders as '?'. The hot-path prints are also
kept ASCII-only as defence in depth, but this guard is what makes the class of
bug unreachable rather than merely unlikely.
"""

import sys as _sys


def _make_stream_encoding_safe() -> None:
    for _name in ("stdout", "stderr"):
        _stream = getattr(_sys, _name, None)
        if _stream is None:
            continue
        try:
            # Python 3.7+: swap the stream's codec in place.
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            # Streams that don't support reconfigure (pytest capture, some
            # WSGI/ASGI wrappers) are left alone rather than replaced — losing
            # the host's capture would be worse than a mangled character.
            pass


_make_stream_encoding_safe()
