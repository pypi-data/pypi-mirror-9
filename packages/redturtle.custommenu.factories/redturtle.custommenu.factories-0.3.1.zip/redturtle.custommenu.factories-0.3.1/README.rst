.. contents::

Summary
=======

This product make possible the customization of the Plone "*Add new...*" menu, commonly filled
from the Plone available content types.

This is designed for avoiding useless content types but, at the same time, help UI experience of
non-technical users.

You can use this to add new non-standard stuff to the menu (like JavaScript links). See below.

Idea behind this
================

The case is related to developed content types that gets added to Plone only for *usability* enhancements.

One example: have you ever used Plone4ArtistsVideo, or `collective.flowplayer`__?
In those products users that want to add new video to a site must use the "*Add new...*" menu and select
the *File* content.

__ http://pypi.python.org/pypi/collective.flowplayer

So the editor (that is *never* a developer in real life... you must accept it) must know that when he add
a new file, it magically became a video... This is not so simple to understand; also is impossible to
understand it without a training or by past experience.
Can't be better if the user could read "*Add new video*" in the menu instead?

Right now the best usability choice is to add a new content type to the menu, or develop a new helper portlet
that show some links like "*add a new video here*".

In the first case, just copy/paste the original used content if enough (copy/paste the *File* content type and
rename it in something like "Video").
But you know... we don't really need those new content types.

In the second case all is ok, but what Plone users know is to look at the right menu to search for addable
types, not to look in a menu and *also* in another place.

So:

* user know that for adding new content types, they must use the "*Add new...*"
* users often ignores the magic behind Plone (like the File that became a Video)
* developer don't like to add new silly content types only to help end users (no, the are not bad guys).

The problem above is related to the not-customizable state of the "Add new..." menu: the editor and the
developer will be both happy if a new, fake entry could be added to this menu.
Going back to the video example:

* the classic *File* entry (that point to *http://myhost/mysite/createObject?type_name=File*)
* a new "Video" entry (again pointing to *http://myhost/mysite/createObject?type_name=File*)

This products is designed only for this or similar usability issues, however can help you to customize
existing elements of the menu on context (for example: the action of adding a new "News Item" content in
a folder can be customized to be an alias for another content type, but only for this special folder,
or you can disable with a falsy espression a content type in a folder, ...).

How to use
==========

Installation
------------

Simply add the egg to your buildout, and re-run it.

::

    [instance]
    ...
    eggs =
        ...
        redturtle.custommenu.factories
    ...

Remember to add also the ZCML slug and overrides if you are testing this on Plone 3.2 or lesser.

After this, install the new product in Plone.

Customize the menu
------------------

In your "Add new..." menu you'll find a new "*Customize menu...*" entry. This will lead you to a
form where you must enable customization feature on the current context.
After this you can use the a customization form where you can manage local menu changes.

.. figure:: http://keul.it/images/plone/redturtle.customizemenu.factories1.png
   :align: left

For every new entry you can/must fill this informations:

`id`
    Enter here a string to be used to add an HTML id attribute to the new element. You can not provide
    it, but if you use an already existing ids, the new one will override the old.
    In this way you can *replace* one of the native (or inherited) menu entry with a new ones.
`name`
    Required.
    Provide the string to be used for displaying the new element.
`description`
    The description is used to provide a tooltips hovering the element.
`icon`
    A TALES expression that can be used to give an icon to the new element (very common).
`condition`
    A TALES condition expression. If not provided, the new element is added to the menu. In provided
    it is evaluated as True or False, so the element is displayed or not.
`URL`
    Required.
    A TALES expression used to render the HREF attribute on the link in the element. You have total freedom
    here: you can also render a string as "*javascript:...*" to provide some Javascript features.

Also you can inherit the customization done in the site root everywhere in the site, adding this to all
other customizations. You can also locally block the inherit of root customization but you can also make
new menu elements defined in the root available only in the root itself.

Also, you can give a right *id* to new entries not only to override menu element from Plone normal
behaviour, but also for change a customization done in the site root.

.. figure:: http://keul.it/images/plone/redturtle.customizemenu.factories2.png
   :align: left

TALES expressions
-----------------

In the TALES expression above, you can use those variables:

 `context`
     The current context, as Plone normal meaning
 `container`
     The container of the current context, or the context itself if the context is a container. This is
     useful when writing expression that keep in mind the default document in a folder.
 `portal_url`
     The *portal_url* tool, taken from the Plone site.

Generic setup support
---------------------

Juan. [nueces] provided Generic Setup support for this package:

.. code:: xml

    <?xml version="1.0"?>
    <object>
      <property name="inherit">True</property>
      <custommenu>
        <property name="element-id">pdf-file</property>
        <property name="element-name">PDF Document</property>
        <property name="element-descr">A file content to be filled with a PDF document</property>
        <property name="icon-tales">string:$portal_url/pdf_icon.gif</property>
        <property name="condition-tales"></property>
        <property name="element-tales">string:${container/absolute_url}/createObject?type_name=File</property>
      </custommenu>
      <custommenu>
          ...
      </custommenu>
      <object name="documents">
        <property name="inherit">True</property>
        <custommenu>
            ...
        </custommenu>
        <object name="ebooks">
           <property name="inherit">True</property>
           <custommenu>
                ...
           </custommenu>
           ...
        </object>
        ...
      </object>
      ...
    <object>

For a complete code check `collective.examples.custommenufactories`__.

__ http://svn.plone.org/svn/collective/collective.examples.custommenufactories/trunk/

Dependencies
============

All Plone versions from 3.3 to 4.3 has been tested.

TODO
====

* JavaScript features for managing entries
* code needs refactoring
* think about inherit customizations not only from portal root
* subsites testing needed

