
Changelog
---------

0.10 (2014-01-19)
~~~~~~~~~~~~~~~~~

- Sort adress variants by lastname, firstname. #38.
  [href]

- Remove memberships and commission_memberships from the addresses variant.
  [href]

0.9 (2014-12-22)
~~~~~~~~~~~~~~~~

- Adds two Kantonsrat address variants for all addresses and for adress labels.
  [href]

- The JSON export now contains links to ALL organizations (even if they are
  private). See #30.
  [href]

- Adds the ability to print the comissions report for single commissions.
  [href]

- Adds a PDF icon to the commission report link.
  [href]

- Fix removal of memberships if a replacment_for relationship is broken.
  [href]

- Fix display of organizations if a membership relationship is broken.
  [href]

0.8 (2014-05-08)
~~~~~~~~~~~~~~~~

- The json export now contains all members and organizations, independent of
  their workflow state. Fixes #25.
  [href]

0.7 (2014-04-22)
~~~~~~~~~~~~~~~~

- Fixes exception being trigger if a private person is used in a published 
  membership. The membership is hidden now in this case. Fixes #17.
  [href]

- Show dates on organization view. Fixes #5.
  [href]

- Print numbers instead of stars for references in the report. Fixes #9.
  [href]

- Make email private. Fixes #10.
  [href]

- Remove reports from all organizations except the ones with the 'kommissionen'
  id. Fixes #11.
  [href]

- Fixes unicode decode error when editing memberships in organizations with
  titles outside the ASCII range. Closes #8.
  [href]

0.6 (2014-03-31)
~~~~~~~~~~~~~~~~

- Fixes critical error caused by a typo in the trigger-state view.
  [href]

0.5 (2014-03-31)
~~~~~~~~~~~~~~~~

- Adds start/end to Kantonsrat which hides them from the list of the people.
  [href]

- Adds the ability to define past, present and future memberships in 
  organizations.
  [href]

- Adds the ability to show external motions defined in
  https://github.com/4teamwork/geschaeftsverzeichnis.
  [href]

- Adds the ability to select a replacement for existing memberships.
  [href]

- Adds the ability to activate/deactivate organisations using a start/end date.
  Inactive organisations are not shown in the list and in the navigation. 
  They are still available through the url.

  This needs a cronjob run every night calling
  https://example.org/plone/trigger-state as administrator.
  [href]

- Adds the ability to directly edit the role and the note of a membership.
  Fixes #4.
  [href]

- Adds notes display to organization memberships.
  [href]

- Adds saner dateranges for birthday/entry date.
  [href]

- Adds a number of private fields for members.
  [href]

0.4 (2013-12-31)
~~~~~~~~~~~~~~~~

- Fixes more spelling errors. I can haz spell check?
  [href]

0.3 (2013-12-31)
~~~~~~~~~~~~~~~~

- Fixes really wrong spelling in German.
  [href]

0.2 (2013-12-31)
~~~~~~~~~~~~~~~~

- Adds parties, committees and factions. Fixes #1.
  [href]

0.1
~~~

- Initial release.
  [href]
