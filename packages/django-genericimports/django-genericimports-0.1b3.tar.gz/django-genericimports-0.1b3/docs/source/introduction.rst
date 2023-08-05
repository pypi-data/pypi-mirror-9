Introduction
============

django-genericimports was born out of the need to create an import mechanism
that worked no matter what, allowing third parties to upload imports into the
database and being as blind as possible to all the human mistakes that can
happen.

Why
---

Mainly because i was tired of doing import scripts for all the projects that
I worked on, the second reason is that it doesn't seem to be any open source
truly generic importer that does the job right, so I felt it was necessary to
do it. Of course there are really cool import applications out there, and maybe
they suit you better than this one.

I know it's not the best approach, an it is slow as hell, but that is why I
opensourced it, so everyone could improve  it. By the way I'm quite a fan of
commenting the code, so you will find tons of comments in it, even some
comments that are obviously obvious, but hey, not only 10+ y/exp programmers
will be looking at this.

Disclaimer
----------

Please note that this application was made to cover all use cases and it sanitizes the data. It's not meant to be fast, at least at this stage of development. Feel free to send your optimization patches.

