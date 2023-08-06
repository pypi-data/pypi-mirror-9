*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Resource  Selenium2Screenshots/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Keywords ***

A site administrator
    Enable autologin as  Manager

A new theme
    Go to  ${PLONE_URL}/@@theming-controlpanel
    Page should contain  New theme
    Click button  New theme

    Wait until page contains element  name=create

    Input text  title  My Theme
    Click button  Create

    Wait until page contains  Modify theme
    Page should contain  My Theme

I open the export form
    Go to  ${PLONE_URL}/++theme++my-theme/@@export-site-setup
    Page should contain  Export site setup

I submit the export form
    Page should contain  Export site setup

    Set window size   768  576
    Capture and crop page screenshot  export-site-setup.png  content

    Click button  Export
    Wait until page contains  Done

The theme should contain the export
    Go to  ${PLONE_URL}/++theme++my-theme/@@theming-controlpanel-mapper

*** Test cases ***

Site setup can be exported into theme
    Given a site administrator
      And a new theme
     When I open the export form
      And I submit the export form
     Then the theme should contain the export
