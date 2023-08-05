===========
acme.dchat
===========

What API ?
==========
`NTT docomo <https://www.nttdocomo.co.jp/>`_ has `a chatting API <https://dev.smt.docomo.ne.jp/?p=docs.api.page&api_docs_id=17>`_.

This software provides a client for the api.

How to use?
===========
1. Get API KEY.
2. Call client.

   .. code-block:: python

      >>> from acme.dchat import DocomoChatClient
      >>> c = DocomoChatClient('some api key')
      >>> c.talk('hello, world.')
      'Helloを聞くようです'
