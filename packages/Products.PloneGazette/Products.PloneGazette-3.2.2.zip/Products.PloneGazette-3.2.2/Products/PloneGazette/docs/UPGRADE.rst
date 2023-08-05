Upgrade
-------

  Upgrade to 3.1.1

    o Subscriber's workflow has been changed from one_state_workflow to
      subscriber_workflow. This requires running of GS upgrade step. If you
      are upgrading to 3.1.1 please do these steps:

          - visit portal_quickinstaller and reinstall PloneGazette to 3.1.1

          - go to ZMI/portal_setup, click Upgrades tab

          - select Products.PloneGazette from the dropdown and click at Choose
            Profile button

          - if there is "No upgrade avaialble", press "Show" button

          - tick Upgrade PloneGazette (3.1.0 - 3.1.1) checkbox
          
          - press Upgrade button

      This upgrade operation may take some time if there is a lot of
      subscribers. There is no progress indication, but messages in the event 
      log:

      - INFO PloneGazette.migration Remapping Subscriber workflow
      - INFO PloneGazette.migration Subscriber workflow remapped


  Upgrade from PloneGazette 2.x to PloneGazette 3.0
  
    o BACKUP YOUR SITE! Backup at least Data.fs (zope database)

    o I personally tried ZEXP export NewsletterTheme object from Zope
      2.9/Plone 2.5 and import it to Zope2.10.4/Plone 3.0.3 and it worked. You
      can use other migration process, for example copy old Data.fs to new
      instance etc. Migration of Plone is described on
      http://plone.org/upgrade

    o Go to portal_quickinstaller, locate PloneGazette, check the checkbox
      and reinstall product. All newsletter themes, newsletters and
      subscribers in your site will be migrated.

    o After migration, all newsletters and newsletter themes may be in default
      workflow initial state (private, by default). To be users able to browse
      newsletter archives and sign in to newsletters, you must publish all
      NewsletterTheme objects and Newsletters. Please check if your
      newsletters are accessible for your anoynmous users.

    o Please be sure Subscribers folder (that one where your subscribers are
      stored) is NOT accessible by anonymous users. You can easily ensure it
      bu moving Subscribers folder to private state.

    o Test your newsletters, test they are accessible for users, test sending
      of some newsletter to your test address (using the Test tab).
