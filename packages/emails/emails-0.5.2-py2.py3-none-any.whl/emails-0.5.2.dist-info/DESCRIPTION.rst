   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
Description: python-emails
        ~~~~~~~~~~~~~
        
        Modern python library for email.
        
        Build message:
        
        .. code-block:: python
        
           >>> import emails
           >>> message = emails.html(html="<p>Hi!<br>Here is your receipt...",
                                  subject="Your receipt No. 567098123",
                                  mail_from=('Some Store', 'store@somestore.com'))
           >>> message.attach(data=open('bill.pdf'), filename='bill.pdf')
        
        send message and get response from smtp server:
        
        .. code-block:: python
        
           >>> r = message.send(to='s@lavr.me', smtp={'host': 'aspmx.l.google.com', 'timeout': 5})
           >>> assert r.status_code == 250
        
        and more:
        
        * DKIM signature
        * Render body from template
        * Flask extension and Django integration
        * Message body transformation methods
        * Load message from url or from file
        
        |
        
        Documentation: `python-emails.readthedocs.org <http://python-emails.readthedocs.org/>`_
        
        Flask extension: `flask-emails <https://github.com/lavr/flask-emails>`_
        
        |
        |
        
        .. image:: https://travis-ci.org/lavr/python-emails.png?branch=master
           :target: https://travis-ci.org/lavr/python-emails
        
        .. image:: https://img.shields.io/pypi/v/emails.svg
           :target: https://pypi.python.org/pypi/emails
        
        .. image:: http://allmychanges.com/p/python/emails/badge/
           :target: http://allmychanges.com/p/python/emails/?utm_source=badge
        
        .. image:: https://coveralls.io/repos/lavr/python-emails/badge.svg?branch=master
           :target: https://coveralls.io/r/lavr/python-emails?branch=master
        
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Intended Audience :: Developers
Classifier: Natural Language :: English
Classifier: License :: OSI Approved :: BSD License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Topic :: Communications
Classifier: Topic :: Internet :: WWW/HTTP
Classifier: Topic :: Other/Nonlisted Topic
Classifier: Topic :: Software Development :: Libraries :: Python Modules
