Asheesh's Django Optimizer
--------------------------


About this package
==================

This package is a total dummy package. Don't use it in any real apps.
It exists for the purpose of demonstrating what a vulnerable/malicious
dependency could be like.

During the web security tutorial, pretend this is a real package and you
actually need it for the web app in question.


Purpose of this package
=======================

Asheesh's Django Optimizer lets you see your "hashed password", which
is private information that only you should be able to see.

Luckily, this package is secure -- it only shows it if you're logged in
as the user you're looking up.

To see your hashed password, visit:

`/optimizer/optimize_user/:username`

assuming that you have mapped in the `urls.py` from this app at
`/optimizer/` in your site.

This is an optimization because visiting this URL *warm the database
cache* for your data! To automatically warm the database cache for
your user data, make sure to create a periodic task (e.g., cron job)
that accesses this URL.


Also about this package
=======================

Version history:

* 1.0: Does nothing, successfully.
* 1.2: Actually implement cache warming functionality.
