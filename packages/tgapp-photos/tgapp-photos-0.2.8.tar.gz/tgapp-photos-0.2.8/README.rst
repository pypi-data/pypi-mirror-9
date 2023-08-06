About TGApp-Photos
-------------------------

Photos is a Pluggable photos application for TurboGears2.
It has born as an example on how to use tgext.crud.EasyCrudRestController
inside a pluggable application, but can be used to quickly implement
photo galleries inside any TurboGears application.

Installing
-------------------------------

tgapp-photos can be installed both from pypi or from bitbucket::

    easy_install tgapp-photos

should just work for most of the users

Plugging Photos
----------------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with photos::

    plug(base_config, 'photos')

You will be able to access the photos process at
*http://localhost:8080/photos*.

Exposed Partials
----------------------

Photos exposes a bunch of partials which can be used
to render pieces of the photo galleries anywhere in your
application:

    * **photos.partials:gallery** -> Renders a photo gallery, if none specified renders the first available

    * **photos.partials:albums** -> Renders preview of galleries, if none specified renders all the galleries

Exposed Templates
--------------------

The templates used by photos and that can be replaced with
*tgext.pluggable.replace_template* are:

    * photos.templates.index

    * photos.templates.gallery

    * photos.templates.gallery_partial

    * photos.templates.albums_partial
