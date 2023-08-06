======
README
======

This package provides an enhanced z3c.form implementation supporting twitter
bootstrap 3 layouts, other enhancements and jsonrpc support given from
j01.jsonrpc.

We use this j01.demo package for develop and explain the different concepts we
use in our projects. One important part is the ability to test jsonrpc ajax form
and buttons. We will use the p01.testbrowser and j01.jsonrpc.testing components
for show how we test our projects. See the package j01.demo for more information.


setup
-----

  >>> import p01.testbrowser.testing

  >>> siteURL = 'http://127.0.0.1:8080'

Let's start with some simple tests:

  >>> import j01.form.layer

  >>> j01.form.layer.IFormLayer
  <InterfaceClass j01.form.layer.IFormLayer>
