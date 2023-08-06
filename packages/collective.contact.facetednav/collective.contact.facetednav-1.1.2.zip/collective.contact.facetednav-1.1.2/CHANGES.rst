Changelog
=========


1.1.2 (2015-04-03)
------------------

- Force no caching in ajax requests (fix bug with Internet Explorer).
  [cedricmessiant]

- Trigger events when selecting/unselecting all.
  [cedricmessiant]

- Use a 'rendercheckboxes' namespace when registering
  Faceted.Events.AJAX_QUERY_SUCCESS callback, so we can unbind it from an other
  module.
  [vincentfretin]


1.1.1 (2014-09-15)
------------------

- Fix conditional viewlet manager to really check that viewlets are available.
  [cedricmessiant]

- We can create a held_position from the faceted navigation view.
  [thomasdesvenain]

- Added 'multiple_selection' option on batch action : the action is available
  when more than one content is selected.
  [thomasdesvenain]

- Works with collective.excelexport 1.1.
  [thomasdesvenain]


1.1 (2014-06-16)
----------------

- WARNING: remove auto-include.
  [thomasdesvenain]

- Display a link to create a new person or organization.
  Name is pre-filled with text search.
  [thomasdesvenain]

- Add an optional and pluggable system
  to provide actions and batch actions on contacts faceted navigation.
  with two examples of batch actions : delete and export (when collective.excelexport installed)
  and two actions: delete and edit.
  [thomasdesvenain]

- Display for held positions.
  [thomasdesvenain]


1.0 (2014-03-11)
----------------

- Do not declare navigable behavior - depends on eea.facetednavigation >= 5.8.
  [thomasdesvenain]

- Manage case users have uploaded non-image formats for logo or photo.
  [thomasdesvenain]

- In faceted search results for person, display held positions phones and emails
  if the person doesn't have phone and email (if person content type doesn't have
  IContactDetails behavior, held_position should).
  [cedricmessiant]

- Add alphabetic criterion to faceted config example.
  [cedricmessiant]

- Add some style to faceted navigation results.
  [cedricmessiant]

- Add macros to customize faceted navigation results.
  [cedricmessiant]

- Fix bug with held position phone and email in preview-* templates.
  [cedricmessiant]


0.10 (2013-11-04)
-----------------

- Works when contact doesn't have contact details and when held position does.


0.9 (2013-09-25)
----------------

- Initial release.
  [thomasdesvenain]
