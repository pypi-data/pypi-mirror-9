.. contents::

Introduction
============

This product will add to Plone a new content rules, someway similar to the default "*Send an email*" ones.
The difference is that the email recipient is taken dinamically from a site content, not from a
static list of values.

In this way the same rule, applied in different places in the site, can send the message to different users.

How to use
==========

The rules can be enabled globally and locally like every one else, as default Plone feature.
In the rule configuration panel you need to fill a set of information:

``Subject``
    The e-mail subject. You can place inside this text some markers (see below).
``Sender email``
    The sender of the e-mail. You can leave this empty and automatically use the one from the
    general mail settings.
``Source field``
    You must put there the name of the attribute from which you want to retrieve the recipient
    e-mail. See next section.
``Target element``
    You need to select if the recipient's e-mail must be taken from:
    
    * the container where the rules is activated on
    * the content who notified the event that started the rule execution
    * the parent of that content 
    
    See below for details.
``Mail message``
    The body text of the e-mail that will be sent. The text is the same for all section where
    the rule is activated on.
    
    You can place inside this text some markers (see below).

How it take the email data
--------------------------

First of all you must choose the *Target element*.

If you choose to keep default "*From rule's container*" option address will be read from the section you have
activated the rule on.

*Example*: if you activated the rule on folder ``/site/section`` and the rule will raise event when
working on a document ``/site/section/folder/foo`` the email address will be taken
from the folder.

Changing to "*From content that triggered the event*" will change the behavior, trying to get email data
from the content that raised the event.

*Example*: if you activated the rule on a folder ``/site/section`` and the rule  will raise event when
working on a document ``/site/section/folder/foo`` the email address will be taken
from the ``foo`` document.

Finally, if you choose "*From content's parent*", adresses will the taken from the container of the content
that triggered the event.

*Example*: if you activated the rule on a folder ``/site/section`` and the rule  will raise event when
working on a document ``/site/section/folder/foo`` the email address will be taken
from ``folder``.

What it try to read
-------------------

The rule try to get from the object:

* an attribute of the given name
* a callable method from the given name
* an Archetypes field with given id
* a ZMI property with given id

The rule try to read, one after one, all this data. The first match found will be the one used;
if not one give results, no e-mail is sent at all.

Message interpolation
---------------------

Marker labels that follow can be used in the message text and subject.

``${title}``
    The title of the content that triggered the event (``foo`` title in our example)
``${url}``
    The URL of the content that triggered the event (``foo`` URL in our example)
``${section_name}``
    The title of the folder where the rule is activated on (``section`` title in our example)
``${section_url}``
    The URL of the folder where the rule is activated on (``section`` URL in our example)

A real Plone use case
---------------------

A Plone site use `Signup Sheet`__ for manage internal training session. The form fieldset is
customized as normal, but one of the field is ``director_email``.

__ http://plone.org/products/signupsheet

We want that this e-mail address is notified when a user subscribe and the user
itself put there the e-mail address of the proper director.

To reach this we need to:

* create a new rule triggered on "*Object added to this container*"
* add a filter condition based on content type *Registrant*
* add an action using the "*Send email to address taken from the content*"
* specify in the action the SignupSheet field with the director email
* specify in the action that we want to take the email from the target content
  (the Registrant itself)

TODO
====

* why don't support also looking in annotations?
* right now the rules check all mail source until one is found with a defined order;
  maybe is better to leave this choice to the configuration
* Dexterity support (probably already there, but needs to be tested)

Requirements
============

This product has been tested on:

* Plone 4.2
* Plone 4.3

Credits
=======

Developed with the support of `S. Anna Hospital, Ferrara`__; S. Anna Hospital supports the
`PloneGov initiative`__.

.. image:: http://www.ospfe.it/ospfe-logo.jpg
   :alt: OspFE logo

__ http://www.ospfe.it/
__ http://www.plonegov.it/

This product was largely developed looking at the source of `collective.contentrules.mailtogroup`__.

__ http://plone.org/products/collective.contentrules.mailtogroup

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

