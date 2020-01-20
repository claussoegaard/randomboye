# Todos
* Try changing randomboye to Thread and only use Process for stuff I want to be able to kill -- maybe that is something I want to be able to kill?
* Consider expanding on the Lock mechanism. One lock for printing, one lock for enabling/disabling buttons maybe?
* Cleanup logger.debug statements
* If getting collection from Discogs fails, add fallback to get non-updated from file
* Add back blinking on shutdown function
* See about making logging async by using QueueHandler and QueueListener. The raspberry pi is slow and with particularly long record artists/title strings, setting up the framebuffers calls certain helper functions and as such logger.debug() as well, which slows down things noticably. 