# django-sparkle-external

Django-sparkle-external is a spin-off version of django-sparkle-1.5 to provide Sparkle updates with external file sources.

I serve my app site with [Heroku](https://www.heroku.com), on which it is absolutely painful to enable media file uploads for Django. I changed the file source to a `URLField` so that I can serve my updates with [GitHub](https://github.com) Downloads instead. Some other hooks provided by django-sparkle-1.5 had also been removed since they won’t work on Heroku.

I also used [Django Ghostdown](https://github.com/uranusjr/django-ghostdown) to provide a better text field for release notes. One benefit (?) of this is that this project does not depend on `Markdown` anymore, but you can use any Markdown rendering library as you wish. See description of Django Ghostdown for more information on the setup.

The original README of django-sparkle-1.5 follows.



# django-sparkle-1.5

Django-sparkle-1.5 is a Django application to make it easy to publish updates for your mac application using [sparkle](http://sparkle.andymatuschak.org/).

In addition to publishing updates via the appcast feed, Django-sparkle can also collect system profile information if sparkle is configured to report it.

This version of django-sparkle is intended for use with Django 1.5 and has some added features. If you're looking for the base version of django-sparkle, please visit [https://github.com/Mobelux/django-sparkle](https://github.com/Mobelux/django-sparkle)

# Requirements

* Django >= 1.5
* Markdown > 2.1 (for release notes)
* django-absolute (for absolute URLs in the link field of the appcast)

## optional requirements

* OpenSSL (if you want to have releases signed)
This must be available on the command line as the `openssl` command.



# Setup

1. `easy_install django-sparkle-1.5` or `pip install django-sparkle-1.5`
2. Make sure that `django-absolute` is correctly installed (this needs some additional settings).
3. Add `sparkle` to your installed apps
4. In `urls.py` include the sparkle URLs by adding something like `(r'^sparkle/', include('sparkle.urls'))`.
5. Ensure `MEDIA_URL` is correctly set
6. `python manage.py syncdb` to create the tables needed for sparkle.
7. Optional: In `settings.py` add `SPARKLE_PRIVATE_KEY_PATH` which is the path to your private DSA key for signing your releases.
8. Optional: Add `SPARKLE_UPLOAD_PREFIX` to your settings (default is `sparkle/`). This component will be added to the media URL for your uploaded versions.

# Usage

Create an application and optionally add some versions.

The application's appcast feed will be available at `/whatever_you/configured_in/your_urls_py/(?P<application_slug>\d+)/appcast.xml`.

Your uploaded versions will be available at `{{ MEDIA_URL }}/SPARKLE_UPLOAD_PREFIX/application_slug/version_number.extension`. You can get the URL for an latest version of an Application by calling `instance.latest().update.url`.

Set the `SUFeedURL` key in your Info.plist to point to the sparkle application's appcast URL. `http://example.com/sparkle/app/appcast.xml` for example.

If you want to enable system profiling, be sure to set the `SUEnableSystemProfiling` key in your Info.plist to `YES`.

# Settings

* `SPARKLE_PRIVATE_KEY_PATH`
   The path to your DSA private key for signing releases.  Defaults to `None`.  If not provided, releases will not be automatically signed when uploaded.
* `SPARKLE_UPLOAD_PREFIX`
The path prefix that will be added to your uploaded files. Defaults to `sparkle/`. Use this to configure the upload directory in which your release files will end. Note that this prefix will become part of the download URL. Remember to end this with a `/` if you want a directory.


# To Do

* Tests of course!

# License

This software is licensed under the terms of the BSD license:

Copyright (c) 2011, Jason Emerick
Copyright (c) 2013, Johannes Spielmann
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
