# Multi User Blog

3rd Project in Udacity's Full Stack Web Developer Nanodegree.

### Running the project

* Need Google Cloud SDK to deploy and run app, or to test in development
environment. Installation instructions can be found [here][1].
* After installation and the `PATH` environment is configured correctly, the
project can be tested in local environment by running `dev_appserver.py path`,
where _path_ is the location of this project and it can be specified relatively
or absolutley.
* To run application in Google App Engine, follow the instructions [here][2].

### Miscellaneous Notes

* Blog layout inspired by [Jake Archibalds blog][3].
* There are many places where app can be improved, e.g.:
  * Use SSL/TLS.
  * Improved error handling
    * For AJAX requests, make sure body is not empty.
    * If possible, provide error messages.
  * Login redirection. Example: when users try to like a blog post without being
  signed in, they are redirected to sign in, however, they are not redirected
  back to where they were before the first redirection.
  * Make comment and blog forms full blown editors so that users have more
  freedom of expression, and to make it easier to tag the content of the blog
  or comment with HTML, e.g., bullet points, font styles, font color, pictures,
  etc.

[1]: https://cloud.google.com/sdk/downloads
[2]: https://cloud.google.com/appengine/docs/python/console/
[3]: https://jakearchibald.com/
