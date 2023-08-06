About TGApp-turbopress
-------------------------

.. image:: https://drone.io/bitbucket.org/axant/tgapp-turbopress/status.png
    :target: https://drone.io/bitbucket.org/axant/tgapp-turbopress

turbopress is a Pluggable Minimalistic Blog for TurboGears2.
It implements articles with Attachments and Tags support.
Uses CKEditor for content editing.
It support both sqla and ming orm.

Installing
-------------------------------

tgapp-turbopress can be installed both from pypi or from bitbucket::

    pip install tgapp-turbopress

should just work for most of the users

Plugging turbopress
----------------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with turbopress::

    plug(base_config, 'turbopress')

Run **gearbox setup-app development.ini** again to create
the tables related to turbopress and start the application.
You will be able to access the blog section at
*http://localhost:8080/press*. Management gui
will be available when logged with an user that
has the the *turbopress* Permission.

Multiple Blogs Support
---------------------------

By default turbopress will work with only one blog, but it supports
a preliminary multiple blogs implementation. Search and TagCloud will
be shared by all the blogs, but it is possible to filter the articles
of only one blog and manage only its articles.

To create a blog access */press/blogs* and create a new one,
you will then be able to access the subblog and manage it by accessing
*/press/blogname*

Exposed Partials
----------------------

turbopress exposed a bunch of partials which can be used
to render pieces of the blogging system anywhere in your
application:

    * **turbopress.partials:articles** -> Renders the list of articles

    * **turbopress.partials:article_preview** -> Renders the preview of an article

    * **turbopress.partials:tagcloud** -> Renders the blog tagcloud section

    * **turbopress.partials:search** -> Renders the blog search section

    * **turbopress.partials.excerpts** -> Renders excerpts of a list of articles

    * **turbopress.partials.excerpt** -> Renders the excerpt of an article

Available Hooks
----------------------

turbopress exposes some hooks and options to configure its
aspects.

Options that can be passed to the **plug** call:

    * **form** -> Full python path of the form class to use for the Article form. By default *turbopress.lib.forms.ArticleForm* is used.

The hooks that can be used with TurboGears2 *register_hook* are:

    * **turbopress.before_create_article(article, values)** -> Runs before the creation of an article

    * **turbopress.after_create_article(article, values)** -> Runs after the creation of an article, makes possible to set additional data for newly created articles

    * **turbopress.before_edit_article(article, values)** -> Runs before displaying the edit article form, makes possible to load additional form values

    * **turbopress.before_save_article(article, values)** -> Runs before saving the article after it got edited, makes possible to update additional data for the article.
