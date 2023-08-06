Introduction to basical usage
=============================

Welcome to the guide of the usage of redturtle.custommenu.factories.
We need to setup something before this file can became a real and working browser test for Plone.
    
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> portal_url = self.portal.absolute_url()
    >>> self.portal.error_log._ignored_exceptions = ('NotFound', 'Redirect', 'Unauthorized')
    >>> from Products.PloneTestCase.setup import portal_owner, default_password

Ok, now we are ready to load the Plone site where this product is installed.

    >>> browser.open(portal_url)

Our first test is to see that the "Customize menu..." element of the factories menu can't be used
by "normal" users.

    >>> browser.getLink('Log in').click()
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = 'secret'
    >>> browser.getControl(name='submit').click()
    >>> "You are now logged in" in browser.contents
    True

So the link to access the customization can't be in the current page. A Contributor can add a new content
type (like a "News Item") but can't see the new command.

    >>> browser.getLink('News Item').text.endswith('News Item')
    True
    >>> "Customize menu" in browser.contents
    False

Again, the contributor user can't go directly to the customization form if he know the URL.

    >>> browser.open(portal_url + "/@@customize-factoriesmenu")
    Traceback (most recent call last):
    ...
    Unauthorized: You are not authorized to access this resource.

Only Manager (or role that behave the "*Customize menu: factories*" permission) can access the customization
form.

    >>> browser.open(portal_url+'/logout')
    >>> browser.open(portal_url+'/login_form') # silly, but needed for Plone 4 tests
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl('Log in').click()
    >>> "You are now logged in" in browser.contents
    True

Now the "Customize menu" link must be available when on homepage.

    >>> browser.open(portal_url)
    >>> "Customize menu" in browser.contents
    True
    >>> browser.getLink('Customize menu').click()

Now test if we are arrived in a form needed to explicitly enable customization per-context.

    >>> "Factories menu management activation" in browser.contents
    True

Before being able to add or customize menu elements, we need to activate the feature here, in the site
root.

    >>> browser.getControl(name='enable-command').click()

Now we are again the the customization form, but the form is changed. We can test to be at the same URL,
but now with a nice activation message.

    >>> browser.url == portal_url+'/@@customize-factoriesmenu'
    True
    >>> 'Enabled local customizations' in browser.contents    
    True

From this new form we can of course disable the customization. Be aware that this will also delete all
customizations added to the context (we will see in a moment how to add customizations).

    >>> browser.getControl(name='disable-command').click()
    >>> browser.url == portal_url
    True
    >>> 'Local customizations disabled' in browser.contents    
    True

Ok, so now we're going back to the customization form, enable it for the site root and going over.

    >>> browser.open(portal_url+'/@@customize-factoriesmenu')
    >>> browser.getControl(name='enable-command').click()

The customization view now is empty (no customization are there).

Adding a new element
--------------------

The simplest thing we can do is to add an alias for another existing content type. Often the "File"
entity can be unfriendly (not all users see a PDF as a "file"), we can create a new entry named
"PDF Document".

The idea is to keep inner Plone feature to handle PDF files (so still we will use the File content type)
but we change the UI for final users.

Let's fill the form.

    >>> browser.getControl(name='element-id').value = 'pdf-file'
    >>> browser.getControl(name='element-name').value = 'PDF Document'
    >>> browser.getControl(name='element-descr').value = 'A file content to be filled with a PDF document'
    >>> browser.getControl(name='icon-tales').value = 'string:$portal_url/pdf_icon.gif'
    >>> browser.getControl(name='element-tales').value = 'string:${container/absolute_url}/createObject?type_name=File'

We skipped the optional *condition-tales* that can be used to control when the customized entry must
appear in the UI (see advanced section below).

Now we can submit the form and see the result.

    >>> browser.getControl(name='add-command').click()
    >>> 'New entry added' in browser.contents
    True

First of all we are still in the customization form.

    >>> browser.url == portal_url+'/@@customize-factoriesmenu'
    True

The entry we just added is now available for being updated or deleted, in another part of the same page.

    >>> browser.getControl(name='element-name:list').value
    'PDF Document'

Now it's time to test what new feature we added to the site. Going back to the site root we can now rely
on our new entry in the factories menu.

    >>> browser.open(portal_url)
    >>> browser.getLink('PDF Document').text
    '[IMG] PDF Document'

Also, all other given attributes has been used.

    >>> browser.getLink('PDF Document').attrs['title']
    'A file content to be filled with a PDF document'
    >>> browser.getLink('PDF Document').attrs['id']
    'pdf-file'
    
But for the user, the real interesting thing is the "new" content type. Click on the new link in the menu
will lead us to add a normal Plone File content.

    >>> browser.getLink('PDF Document').click()
    >>> browser.url.startswith(portal_url + '/portal_factory/File/file.')
    True

When adding new element, some entry data (name and TALES expression for the URL) are required. We are forced
to provide both of them.

    >>> browser.open(portal_url+'/@@customize-factoriesmenu')
    >>> browser.getControl(name='element-id').value = 'fake'
    >>> browser.getControl(name='element-descr').value = 'fake'
    >>> browser.getControl(name='icon-tales').value = 'fake'
    >>> browser.getControl(name='add-command').click()
    >>> 'Please, provide all required data' in browser.contents
    True
    >>> browser.getControl(name='element-id').value = 'fake'
    >>> browser.getControl(name='element-name').value = 'fake'
    >>> browser.getControl(name='element-descr').value = 'fake'
    >>> browser.getControl(name='icon-tales').value = 'fake'
    >>> browser.getControl(name='add-command').click()
    >>> 'Please, provide all required data' in browser.contents
    True
    >>> browser.getControl(name='element-id').value = 'fake'
    >>> browser.getControl(name='element-descr').value = 'fake'
    >>> browser.getControl(name='icon-tales').value = 'fake'
    >>> browser.getControl(name='element-tales').value = 'fake'
    >>> browser.getControl(name='add-command').click()
    >>> 'Please, provide all required data' in browser.contents
    True
    >>> browser.getControl(name='element-id').value = 'fake'
    >>> browser.getControl(name='element-name').value = 'fake'
    >>> browser.getControl(name='element-descr').value = 'fake'
    >>> browser.getControl(name='icon-tales').value = 'fake'
    >>> browser.getControl(name='element-tales').value = 'fake'
    >>> browser.getControl(name='add-command').click()
    >>> 'Please, provide all required data' in browser.contents
    False
    >>> 'New entry added' in browser.contents
    True

In the last example above we added a completely non-sense new element. But the menu customization feature
heavily rely on the TALES expression for the URL. In the given data can't be transformed in a valid TALES
expression, the whole entry is ignored.

In a similar way, if errors are put inside other optional TALES expressions, they will be ignored
(**not** evaluated to False).

So, going back to the site root we don't see any "*fake*" link available, even if the "*PDF Document*"
ones is still there.

    >>> browser.open(portal_url)
    >>> 'fake' in browser.contents
    False
    >>> 'PDF Document' in browser.contents
    True

Removing entries
----------------

Just for keep things clean, but obviously also for giving to users a way to remove added customization,
the form provide the feature to remove stored entries.

First of all, be sure that our "*fake*" element is in the form.

    >>> browser.open(portal_url+'/@@customize-factoriesmenu')
    >>> browser.getControl(name='element-name:list', index=1).value
    'fake'

Also the first (and good) entry is there.

    >>> browser.open(portal_url+'/@@customize-factoriesmenu')
    >>> browser.getControl(name='element-name:list', index=0).value
    'PDF Document'

To delete one or more entries we must use the "*Delete selected*" button. First we must select one or
more entries. Click on the button without select an entry will return an error to the user, and no
real action will be performed.

    >>> browser.getControl(name='delete-command').click()
    >>> 'Please, select at least one entry to be deleted' in browser.contents
    True
    >>> browser.url == portal_url+'/@@customize-factoriesmenu'
    True

Ok, now we remove the garbage of the "*fake*" element.

    >>> browser.getControl('Delete?', index=1).click()
    >>> browser.getControl(name='delete-command').click()
    >>> 'Customizations removed' in browser.contents
    True

Now we don't see anymore the "*fake*" entry in the form.

    >>> 'fake' not in browser.contents
    True


Modify and update existing entries
----------------------------------

The next and last "simple" task is to modify existing entry for local menu customization.
In the next example we keep all the data for our "*PDF Document*" but we wanna change the mandatory
description.

    >>> browser.getControl('Element description', index=0).value
    'A file content to be filled with a PDF document'
    >>> browser.getControl('Element description',
    ...                    index=0).value = 'A PDF document (ok, this is again a File content)'

We must now click on the "*Save changes*" button.

    >>> browser.getControl('Save changes').click()
    >>> 'Customizations updated' in browser.contents
    True
    >>> browser.getControl('Element description', index=0).value
    'A PDF document (ok, this is again a File content)'

We are still in the form, so we can continue to change again our entry. Like for adding new ones, required
data must be provided.

    >>> browser.getControl('Element name', index=0).value = ''
    >>> browser.getControl('Save changes').click()
    >>> 'Please, provide all required data' in browser.contents
    True

To make a real test of the changes, let's go back to the site root and see if the link title has been
changed.

    >>> browser.open(portal_url)
    >>> browser.getLink('PDF Document').attrs['title']
    'A PDF document (ok, this is again a File content)'


Advanced use
============

The customization can give us more power and new features thanks to:

 `Condition for entry`
     We can provide a condition TALES expression that will be evaluated to make an element appear or not
 `Multiple contexts`
     We can customize different entries in different context all around the site. As seen before the site
     root is a context, but a very special ones.
 `Inheritance`
     The "*Inherit*" check will give us the power to enable/disable acquisition of customization defined
     in the site root to lower contexts.
 `Override and obfuscate`
     Using the *id* we can override inherit customization but also original menu elements.
     We can also hide elements using a *False* condition.

Before going on with examples, let's prepare a new context to work on. We now create a new Folder content
inside our Plone site.

    >>> browser.getLink('Folder').click()
    >>> browser.getControl('Title').value = 'New area'
    >>> browser.getControl('Description').value = 'Welcome to a new area of the site'
    >>> browser.getControl('Save').click()

Next, we go again to the customization form.

    >>> browser.getLink('Customize menu\xe2\x80\xa6').click()
    >>> browser.url == portal_url+'/new-area/@@customize-factoriesmenu'
    True

Use TALES conditions
--------------------

Let's introduce power of condition with an example. Let's say that in our "*New area*" we want to handle
a special kind on Event content type. But this event must be addable to our new area if and only if a
special marker keyword is used on the area itself.

First of all, this is a new context, so we need to enable local customization there.

    >>> browser.getControl('Enable').click()
    >>> 'Enabled local customizations' in browser.contents
    True

Now we can add our new entry.

    >>> browser.getControl(name='element-name').value = 'Special Event'
    >>> browser.getControl(name='condition-tales').value = "python:'Special' in container.Subject()"
    >>> browser.getControl(name='element-tales').value = 'string:${container/absolute_url}/createObject?type_name=Event'
    >>> browser.getControl('Add this').click()
    >>> 'New entry added' in browser.contents
    True

Now we can return to the folder view.

    >>> browser.getLink('Return').click()
    >>> browser.url == portal_url + '/new-area'
    True

As the condition we used check for a keyword we don't provided yet, no new entry is visible inside the
factories menu.

To see our new element, we need to add the tag "*Special*" to the folder.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='subject_keywords:lines').value = 'Special'
    >>> browser.getControl('Save').click()
    >>> 'Special' in browser.contents
    True

We supplied the right keyword, so our new element must be in the factories menu.

    >>> 'Special Event' in browser.contents
    True

Before going on, we must talk a little more on variable used in the condition. As we used *container*
instead of context we are sure that always, inside the "New area" folder, the new entry is available
(of course, when the condition pass).

Use *context* here can leave to unexpected and unwanted result when the folder use a contained document as
default view. In this case when we are on the folder the real context is the document inside.

Use *container* is the best choice, so our trick continue to work even if a document is used as default
view for the folder.

    >>> browser.getLink('Page').click()
    >>> browser.getControl('Title').value = 'The index page'
    >>> browser.getControl('Body Text').value = '<p>Welcome to a secret area</p>'    
    >>> browser.getControl('Save').click()
    >>> browser.getLink('New area').click()
    >>> browser.getLink('Select a content item as default view').click()
    >>> browser.getControl('The index page').click()
    >>> browser.getControl('Save').click()

Now we can see that going onto the "New area" folder we see the new start page created above, but the
factories link is still in the menu.

    >>> browser.open(portal_url + '/new-area')
    >>> 'Special Event' in browser.contents
    True


Multiple contexts
-----------------

Right now we worked on two different section of the site where we defined customization of the
factories menu:

* the site root
* the "*New area*" folder

Going to the site root we see only the customization defined there. If we go to the Folder defined in
examples above, we see both customizations!

    >>> browser.open(portal_url + '/new-area')
    >>> 'Special Event' in browser.contents
    True
    >>> 'PDF Document' in browser.contents
    True

This because "*New area*" is a Folder inside the Plone root. But (right now) this will only happen for
the Plone root and other containers inside it.
This inheritance will not be repeated for a Folder (with local customization) and a subfolder inside it.

Let's create a subfolder inside the current area.

    >>> browser.getLink('Folder').click()
    >>> browser.getControl('Title').value = 'Subsection'
    >>> browser.getControl('Save').click()
    >>> browser.url == portal_url + '/new-area/subsection/'
    True

There we only see the customization defined in the site root (again: because the site root is right now
the only context that can spread its customization to all other contexts).

    >>> 'Special Event' in browser.contents
    False
    >>> 'PDF Document' in browser.contents
    True


Use inherit checks
------------------

This part is strictly related to the multiple context section above. Right now we always ignored a checkbox
available in every customization form: the "*Inherit*" check, that is selected by default.

This check take 2 very different meaning in Plone root and in other contexts (this will underline once again
that site root is special for us).

In the site root this check will say us that customization defined there *can* be inherited in lower levels
of the site.

Disabling this doesn't change nothing in the site root context, but make all customization not available in
all other contexts.

Let's go back to root's customization form.

    >>> browser.open(portal_url)
    >>> browser.getLink('Customize menu').click()

Now try to uncheck the inherit command, save and return to the site view.

    >>> browser.getControl('Inherit').click()
    >>> browser.getControl('Save changes').click()
    >>> browser.getLink('Return').click()

Nothing is changed here. The "*PDF Document*" menu entry is still there.

    >>> 'PDF Document' in browser.contents
    True

But if we move now to the "*New area*" folder, we'll see a big difference.

    >>> browser.getLink('New area').click()

There we still see the local customization, but we don't see anymore the one defined in the site root.

    >>> 'Special Event' in browser.contents
    True
    >>> 'PDF Document' in browser.contents
    False

This feature is given for all usecases where the customization of the menu is needed only in the site root,
just because only there we need some additional menu elements.

The inherit check in all other contexts has a different meaning. Like said before the check in the Plone
root tell that customizations *can* be inherited but the check in the other contexts tell us if root's
customizations *must* be inherited.

To test this we need to enable again the check in the site root.

    >>> browser.open(portal_url)
    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Inherit').click()
    >>> browser.getControl('Save changes').click()
    >>> browser.getLink('Return').click()

Ok, now we will change the inherit check on the "*New area*" folder.

    >>> browser.getLink('New area').click()
    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Inherit').click()
    >>> browser.getControl('Save changes').click()
    >>> browser.getLink('Return').click()
    >>> browser.url == portal_url + '/new-area'
    True

The result is the same as before.

    >>> 'Special Event' in browser.contents
    True
    >>> 'PDF Document' in browser.contents
    False

But there is a big difference: now is the current context that say "I don't wanna see root's
customizations".

No, go to the subsection.

    >>> browser.getLink('Subsection').click()

There the inheritance block of the upper folder has no effect. We still see there the customization
defined in the site root.

    >>> 'PDF Document' in browser.contents
    True


Using id for override
---------------------

In all examples above we used or skipped the "*Element id*" data for customization without giving it
too much consideration.

It's primary task is to render and HTML id attribute to the link in the menu.

    >>> browser.open(portal_url)
    >>> browser.getLink('PDF Document').attrs['id'] == 'pdf-file'
    True

Default entries have also ids.

    >>> browser.getLink('Image').attrs['id'] == 'image'
    True

Then came the magic! As we like valid XHTML we don't want to have duplicate id in the same page, so the
customized menu will not show you two entries with the same id: only ones will be shown.

We use this also to reach another feature because the customized id wins on inherit ones, this is true
for standard or already customized (and inherited from the site root) elements.

In the last example we seen that the link for creating a new Image has an id. Let's go back to our
subsection folder.

    >>> browser.open(portal_url+'/new-area/subsection')

The link for creating Image is there as in Plone normal behaviour.

    >>> browser.getLink('Image').attrs['id'] == 'image'
    True

Now we add local customization in this folder. Since is the first time we customize this folder, we need
to enable local customizations.

    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Enable').click()

Now we are free to add a new customization there. For this example we will repeat what we did for the
PDF document, and add a new "*Photo*" entry.

    >>> browser.getControl(name='element-name').value = 'Photo'
    >>> browser.getControl(name='icon-tales').value = 'string:$portal_url/image_icon.gif'
    >>> browser.getControl(name='element-tales').value = 'string:${container/absolute_url}/createObject?type_name=Image'
    >>> browser.getControl("Add this").click()

Now we can go back to the folder view and see the result.

    >>> browser.getLink('Return').click()

Nothing new right now.
Now let's say that in this folder we don't want to add Image content type but only Photo (we know that
they are the same, but think as a final user).

We can reach this in 3 ways:

* Use basic Plone features, and access the "Restrictions..." option inside the factories menu, to disable
  Image there.
* Give to our Photo entry the same id that Image has.
* Create an additional customization entry for Image, keeping the same id of Image with an always false
  condition.

The third choice is silly (but possible). However we want to focus on the second choice.
Giving to Photo the same id used by Image will automatically make Image entry invisible in this context
(because Image is inherited from root).

    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Element id', index=0).value = 'image'
    >>> browser.getControl("Save changes").click()
    >>> browser.getLink('Return').click()

So, now we have no "*Image*" option available, but "*Photo*" is still there.

    >>> browser.getLink('Image')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> 'Photo' in browser.contents
    True

Right now we always defined new fake entries, to give users the feeling that new content type are present
in the factories menu. But we can also replace an entry with the same content type.

    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Element name', index=0).value = 'Image'
    >>> browser.getControl("Save changes").click()
    >>> browser.getLink('Return').click()

Now the Image is back in the menu, and Photo disappeared.

    >>> bool(browser.getLink('Image'))
    True
    >>> browser.getLink('Photo')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

This is obviously a stupid example for now, but this can show some possibility, like a way to change
some less important data of the menu element (you can, for example, change only image icon for an entry
in a context).

Another *big feature* is to give us the power to conditionally give or not a content type to users
(default or customized ones).

For example: now we are replacing the base Plone Image content type with a new one (that give the same
features) but we want to make this content addable in that folder only when it is *published*.

*Note: this is only an example... playing with review state of objects is a task for workflow*.

    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('TALES condition',
    ...                    index=0).value = "python:container.portal_workflow.getInfoFor(container, 'review_state')=='published'"
    >>> browser.getControl("Save changes").click()
    >>> browser.getLink('Return').click()

Now, as far as the condition is False, we don't see any Image in the menu (in this context).

    >>> browser.getLink('Image')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, even if the condition is False, the customization is still done. The local defined Image keep
precedence onto the Plone ones.

Now we need to test if the customized Image will be shown when condition because True. We only need to
publish the folder.

    >>> browser.getLink('Publish').click()
    >>> bool(browser.getLink('Image'))
    True

Last example: show that we can customize also non standards entries, like our "*PDF Document*". For this
example we will define a new PDF option in the "*Subsection*" area.
The "new" version of the PDF entry have only a different description.

    >>> browser.getLink('Customize menu').click()
    >>> browser.getControl('Element id', index=1).value = 'pdf-file'
    >>> browser.getControl('Element name', index=1).value = 'PDF Document'
    >>> browser.getControl('Element description', index=1).value = 'Another boring PDF version'
    >>> browser.getControl('TALES icon', index=1).value = 'string:$portal_url/pdf_icon.gif'
    >>> browser.getControl('TALES expression for URL',
    ...                     index=1).value = 'string:${container/absolute_url}/createObject?type_name=File'
    >>> browser.getControl("Add this").click()
    >>> browser.getLink('Return').click()

Now we need to test if we have only the new version of our PDF in the folder factories menu

    >>> 'Another boring PDF version' in browser.contents
    True
    >>> 'A PDF document (ok, this is again a File content)' in browser.contents
    False


Very advanced features
======================

How the product handle customization for contents is given by *adapters*. For example we have two standard
adapters, one for general folderish contents and another for Plone sites.
Those adapters provide the *ICustomFactoryMenuProvider*.

Those different adapters are the actor that make the inheritance working in a different way in site root or
everywhere else.

Feature described here are targeted on developers.

We can write code that provide an additional adapter for "special" contexts. Providing a totally new adapter
give us *a lot* of freedom for the way we can change customized menu.

The most part of this example is setup outside of this document. See the test setup in
*redturtle.custommenu.factories.tests.adapters*.
In this file we create a new interface (subclass of the interface normally used for standard folder adapter)
and the adapter itself.

Our new adapter does nothing special. It ignore the customization form elements and instead always return
a single "*Hello!*" entry.

To see this in action we create a new folder where to work on.

    >>> browser.open(portal_url)
    >>> browser.getLink('Folder').click()
    >>> browser.getControl('Title').value = "Mad folder"
    >>> browser.getControl('Save').click()

Now for testing purpose we manually make this new folder to provide our interface. Thanks to the adapter
mechanism of Plone, our interface is seen much specific of the standard ones for folders, so our example
adapter will take precedence.

    >>> self.loginAsPortalOwner()
    >>> from redturtle.custommenu.factories.tests.adapters import ISpecialFolder
    >>> from zope.interface import alsoProvides
    >>> mad_folder = self.portal.restrictedTraverse('mad-folder')
    >>> alsoProvides(mad_folder, ISpecialFolder)

Now we must go to our folder view just to see that no factories link available, except for our "*Hello!*".

    >>> browser.getLink('Mad folder').click() # for some reason browser.reload() here breakes Plone 4 tests
    >>> bool(browser.getLink('Hello!'))
    True
    >>> browser.getLink('Folder')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.getLink('PDF Document')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

This example must show that is possible to handle in special way different content type that implements
some interfaces, or single contents that provides other interface.

This will give us a lot of way to customize this product's behaviours.
