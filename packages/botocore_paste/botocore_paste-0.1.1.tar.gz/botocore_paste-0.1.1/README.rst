.. -*- coding: utf-8 -*-

==============
botocore_paste
==============

Utility for ``botocore.session.get_session()``


Install
=======

from PyPI::

  pip install botocore_paste

from source::

  $ pip install -e .


How to use
==========

If you use ``pyramid``::

  import botocore_paste

  def main(global_config, **settings):
      boto_session = botocore_paste.session_from_config(settings)
      config = Configurator(settings=settings)

      # Some your configuration

      return config.make_wsgi_app()


Configuration Keys
==================

See ``botocore.session.Session``'s Documents.

Example ini-file::

  botocore.profile =
  botocore.credentials_file = ~/.aws/credentials
  botocore.config_file = ~/.aws/config
  botocore.metadata_service_num_attempts = 1
  botocore.provider = aws
  botocore.region =
  botocore.data_path =
  botocore.metadata_service_timeout = 1


All keys are not mandatory.
If you don't write any keys, ``botocore.session.Session`` instances are
created by ``default``.
