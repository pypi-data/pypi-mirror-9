robotframework-httpd
====================

Robot Framework keyword library for HTTPD Simulator.

This module allows easy to create http server and test request that http server is received



Installation
------------

``pip install robotframework-httpd``

Usage
-----
`HTTPDLibrary keyword
documentation <http://mbbn.github.io/robotframework-httpd//>`__

.. code:: robotframework

    *** Settings ***
    Library     HTTPDLibrary    port=5060
    Library     RequestsLibrary
    Library     Collections

    *** Test Cases ***
    Test HttpdLibrary GET
        Get Request  /test?param1=p1
        Run Httpd

        Create Session  Httpd   http://localhost:5060
        ${resp}=    Get    Httpd    /test?param1=p1

        wait to get request

    Test HttpdLibrary Post
        Post Request  this is body
        Run Httpd

        Create Session  Httpd   http://localhost:5060
        ${resp}=    Post    Httpd    /      data=this is body

        wait to get request

    *** Keywords ***
    Get Request
        [Arguments]  ${path}
        ${request}=     create dictionary   method  GET     path    ${path}
        set wished request  ${request}

    Post Request
        [Arguments]  ${post_body}
        ${request}=     create dictionary   method  POST     post_body    ${post_body}
        set wished request  ${request}

Contribute
----------

If you like this module, please contribute! I welcome patches,
documentation, issues, ideas, and so on.