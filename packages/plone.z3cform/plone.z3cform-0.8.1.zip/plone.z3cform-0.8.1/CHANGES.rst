Changelog
=========

0.8.1 (2015-01-22)
------------------

- Feature: take group class from parent-form if given. If not given it uses
  the default class.
  [jensens]

- Added Ukrainian translation
  [kroman0]

- Added Italian translation
  [giacomos]


0.8.0 (2012-08-30)
------------------

* Remove backwards-compatibility code for Zope < 2.12
  [davisagli]

* Use plone.testing for functional test layer support.
  [hannosch]

* Use ViewPageTemplateFile from zope.browserpage.
  [hannosch]

* Use form action URL as given by the view, instead of implementing it
  in the template as a call to the ``getURL`` method of the request.
  [malthe]

* Use plone.batching for batches instead of z3c.batching
  [tom_gross]

0.7.8 - 2011-09-24
------------------

* Do not display h1 element if there is no label on view.
  [thomasdesvenain]

* Add Chinese translation.
  [jianaijun]

0.7.7 - 2011-06-30
------------------

* Avoid rendering a wrapped form if a redirect has already occurred after
  updating it.
  [davisagli]

* Remove <a name=""/> elements from inside the CRUD table TBODY element
  they were otherwise unused (and illegal in that location of the HTML content
  model).
  [mj]

0.7.6 - 2011-05-17
------------------

* Add ability to find widgets with non-integer names in lists. This shouldn't
  generally be something that happens, and ideally should be removed if
  DataGridField looses it's 'AA' and 'TT' rows.
  [lentinj]

0.7.5 - 2011-05-03
------------------

* Fix traversal tests on Zope 2.10 to handle TraversalError instead of
  LocationError.
  [elro]

* Fix traversal.py syntax to be python2.4 compatible.

* Revert [120798] as it breaks on Zope2.10 / Plone 3.3. We can deal with Zope
  2.14 in 0.8.x.
  [elro]

0.7.4 - 2011-05-03
------------------

* Define 'hidden' within field macro.
  [elro]

* Ignore "form.widgets." if ++widget++ path begins with it.
  [lentinj]

* Rework traverser to handle lists and subforms
  [lentinj]

* Only search a group's widgets if they exist. collective.z3cform.wizard doesn't
  create widgets for pages/groups other than the current one
  [lentinj, elro]

* Deal with forward compatibility with Zope 2.14.

* Adds Brazilian Portuguese translation.
  [davilima6]

0.7.3 - 2011-03-02
------------------

* Handle wrong fieldnames more cleanly in the ++widget++ traverser.
  [elro]

0.7.2 - 2011-02-17
------------------

* Make sure the CRUD add form doesn't use a standalone template.
  [davisagli]

0.7.1 - 2011-01-18
---------------------

* Add zope.app.testing to test dependencies so that it continues to work under
  Zope 2.13.
  [esteele]

0.7.0 - 2010-08-04
------------------

* Add a marker interface which can be used by widgets to defer any security
  checks they may be doing when they are set up during traversal with the
  ++widgets++ namespace
  [dukebody]

* Fix re-ordering of fields not in the default fieldset. Thanks to Thomas
  Buchberger for the patch.
  [optilude]

* Added Norwegian translation.
  [regebro]

0.6.0 - 2010-04-20
------------------

* In the CRUD table, fix odd/even labels, which were reversed.
  [limi]

* Added slots to the ``titlelessform`` macro. See ``README.txt`` for details.
  [optilude, davisagli]

* Remove the distinction between wrapped and unwrapped subforms. A subform is
  always wrapped by the form that contains it, and can use a Zope 3 page
  template.
  [davisagli]

* Fixed tests in Plone 3.
  [davisagli]

* Fixed tests in Plone 4
  [optilude]

* Made it possible to distinguish wrapped and unwrapped forms via the
  IWrappedForm marker interface.
  [optilude]

* Made it possible to use z3c.form forms without a FormWrapper in Plone 4.
  [optilude]

0.5.10 - 2010-02-01
-------------------

* A z3c.form.form.AddForm do a redirect in its render method.
  So we have to render the form to see if we have a redirection.
  In the case of redirection, we don't render the layout at all.
  This version remove the contents method on FormWrapper,
  it's now an attribute set during the FormWrapper.update.
  This change fixes status message not shown because it was consumed by
  the never shown rendered form.
  [vincentfretin]

0.5.9 - 2010-01-08
------------------

* Fix security problem with the ++widget++ namespace
  [optilude]

0.5.8 - 2009-11-24
------------------

* Don't do the rendering if there is a redirection, use the update/render
  pattern for that.
  See http://dev.plone.org/plone/ticket/10022 for an example how
  to adapt your code, in particular if you used FormWrapper with ViewletBase.
  [vincentfretin]

0.5.7 - 2009-11-17
------------------

* Fix silly doctests so that they don't break in Python 2.6 / Zope 2.12
  [optilude]

0.5.6 - 2009-09-25
------------------

* Added title_required msgid in macros.pt to be the same as plone.app.z3cform
  because macros.pt from plone.app.z3cform uses plone.z3cform translations.
  Added French translation and fixed German and Dutch translations
  for label_required and title_required messages.
  [vincentfretin]

0.5.5 - 2009-07-26
------------------

* Removed explicit <includeOverrides /> call from configure.zcml. This causes
  race condition type errors in ZCML loading when overrides are included
  later.
  [optilude]

0.5.4 - 2009-04-17
------------------

* Added monkey patch to fix a bug in z3c.form's ChoiceTerms on z3c.form 1.9.0.
  [optilude]

* Fix obvious bugs and dodgy naming in SingleCheckBoxWidget.
  [optilude]

* Use chameleon-based page templates from five.pt if available.
  [davisagli]

* Copied the basic textlines widget from z3c.form trunk for use until
  it is released.
  [davisagli]

0.5.3 - 2008-12-09
------------------

* Add translation marker for batch, update translation files.
  [thefunny42]

* Handle changed signature for widget extract method in z3c.form > 1.9.0
  [davisagli]

* Added wildcard support to the 'before' and 'after' parameters of the
  fieldset 'move' utility function.
  [davisagli]

* Fixes for Zope 2.12 compatibility.
  [davisagli]

* Don't display an 'Apply changes' button if you don't define an
  update_schema.
  [thefunny42]

* Declare xmlnamespace into 'layout.pt' and 'subform.pt' templates

* Added support for an editsubform_factory for an EditForm so you can
  override the default behavior for a sub form now.

* Changed css in crud-table.pt for a table to "listing" so that tables
  now look like plone tables.

* Copy translation files to an english folder, so if your browser
  negociate to ``en,nl``, you will get english translations instead of
  dutch ones (like expected).
  [thefunny42]

* Send an event IAfterWidgetUpdateEvent after updating display widgets
  manually in a CRUD form.
  [thefunny42]

0.5.2 - 2008-08-28
------------------

* Add a namespace traversal adapter that allows traversal to widgets. This
  is useful for AJAX calls, for example.

0.5.1 - 2008-08-21
------------------

* Add batching to ``plone.z3cform.crud`` CrudForm.

* Look up the layout template as an IPageTemplate adapter. This means that
  it is possible for Plone to provide a "Ploneish" default template for forms
  that don't opt into this, without those forms having a direct Plone
  dependency.

* Default to the titleless form template, since the layout template will
  provide a title anyway.

* In ``plone.z3cform.layout``, allow labels to be defined per form
  instance, and not only per form class.

0.5.0 - 2008-07-30
------------------

* No longer depend on <3.5 of zope.component.

0.4 - 2008-07-25
----------------

* Depend on zope.component<3.5 to avoid ``TypeError("Missing
  'provides' attribute")`` error.

* Allow ICrudForm.add to raise ValidationError, which allows for
  displaying a user-friendly error message.

* Make the default layout template CMFDefault- compatible.

0.3 - 2008-07-24
----------------

* Moved Plone layout wrapper to ``plone.app.z3cform.layout``.  If you
  were using ``plone.z3cform.base.FormWrapper`` to get the Plone
  layout before, you'll have to use
  ``plone.app.z3cform.layout.FormWrapper`` instead now.  (Also, make
  sure you include plone.app.z3cform's ZCML in this case.)

* Move out Plone-specific subpackages to ``plone.app.z3cform``.  These
  are:

  - wysywig: Kupu/Plone integration

  - queryselect: use z3c.formwidget.query with Archetypes

  Clean up testing code and development ``buildout.cfg`` to not pull
  in Plone anymore.
  [nouri]

* Relicensed under the ZPL 2.1 and moved into the Zope repository.
  [nouri]

* Add German translation.
  [saily]

0.2 - 2008-06-20
----------------

* Fix usage of NumberDataConverter with zope.i18n >= 3.4 as the
  previous test setup was partial and did not register all adapters
  from z3c.form (some of them depends on zope >= 3.4)
  [gotcha, jfroche]

* More tests
  [gotcha, jfroche]

0.1 - 2008-05-21
----------------

* Provide and *register* default form and subform templates.  These
  allow forms to be used with the style provided in this package
  without having to declare ``form = ViewPageTemplateFile('form.pt')``.

  This does not hinder you from overriding with your own ``form``
  attribute like usual.  You can also still register a more
  specialized IPageTemplate for your form.

* Add custom FileUploadDataConverter that converts a Zope 2 FileUpload
  object to a Zope 3 one before handing it to the original
  implementation.  Also add support for different enctypes.
  [skatja, nouri]

* Added Archetypes reference selection widget (queryselect)
  [malthe]

* Moved generic Zope 2 compatibility code for z3c.form and a few
  goodies from Singing & Dancing into this new package.
  [nouri]
