# Todos

* Finesse print functions, maybe take learnings from my attempt of queueing.
    * Make it so it doesn't reset between each framebuffer but just keeps doing full frames, so it doesn't blink between Loading screens
    * Maybe abstract it so only the write_framebuffer function does any actual time.sleep(), based on the step inputs it gets from the calling functions
* Once prints are improved, see about good messaging for when refreshing discogs collection
    * Make it acquire new collection on bootup
* Maybe replace the smiley face rasp screen with some basic collection info like record count?