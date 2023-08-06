
.. _settings-section:

########
Settings
########

These settings are defined, and can be overridden in your project settings

* ``DJANGO_FRONT_PERMISSION``: a callable that gets passed a user object, and returns a boolean specifying whether or not the user is allowed to do front-end editing. Defaults to ``lambda u: u and u.is_staff``
* ``DJANGO_FRONT_EDIT_MODE``: specifies whether the editor should be opened in a lightbox (default) or inline (over the edited element). Valid values are ``'inline'`` and ``'lightbox'``.
* ``DJANGO_FRONT_EDITOR_OPTIONS``: allows for options to be passed on to the editors (works with WYMeditor, Redactor, EpicEditor, CKEditor). This dictionary will be serialized as JSON and merged with the editor's base options. Defaults to ``{}``. Example, to handle `image uploads in Redactor <http://imperavi.com/redactor/docs/images/>`_::

    DJANGO_FRONT_EDITOR_OPTIONS = {
        'imageUpload': '/path/to/image/handling/view/'
    }

* ``DJANGO_FRONT_ALLOWED_EDITORS``: list of allowed editor plugins. Add to this list if you plan on adding a new editor type. Defaults to ``['ace', 'ace-local', 'wymeditor', 'redactor', 'epiceditor', 'ckeditor', 'default']``
