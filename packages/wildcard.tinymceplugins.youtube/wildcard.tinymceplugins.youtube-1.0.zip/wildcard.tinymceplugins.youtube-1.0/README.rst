Introduction
============

This package provides a tinymce plugin for easily adding youtube videos.

Only tested with latest Products.TinyMCE.

Warning
^^^^^^^

You'll likely need to allow iframe as a custom tag via html filtering for
this plugin to work.


Another warning
^^^^^^^^^^^^^^^

Due to the way most modern browsers help protect against XSS attacks, after
you save a form where you added a video with tinymce, you'll likely see the
rendering of the video is blocked initially. Just reload the browser once more
to see the video added.

See http://glicksoftware.com/blog/disable-html-filtering for tips on getting
around this annoyance.
