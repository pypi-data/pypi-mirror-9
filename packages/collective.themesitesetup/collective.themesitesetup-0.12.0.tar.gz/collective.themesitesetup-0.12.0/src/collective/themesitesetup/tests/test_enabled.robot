*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Keywords ***

A site administrator
    Enable autologin as  Manager

An imported theme
    Go to  ${PLONE_URL}/@@theming-controlpanel

    Page should contain  Upload Zip file
    Click button  Upload Zip file

    Wait until page contains element  name=import
    Choose file  themeArchive  ${CURDIR}/my-theme.zip

    Click button  Import

    Wait until page contains  Modify theme
    Page should contain  My Theme

    Wait until page contains  install
    Click link  install
    Wait until page contains  structure
    Click link  structure
    Wait until page contains  objects.dotfile
    Click link  objects.dotfile

    Set window size   768  576
    Capture page screenshot  edit-site-setup.png

I activate the imported theme
    Go to  ${PLONE_URL}/@@theming-controlpanel
    Page should contain  My Theme

    Click button  Activate

    Page should contain  Theme enabled

I see a page imported from theme
    Page should contain  Hello World

*** Test cases ***

Theme activation imports site structure
    Given a site administrator
      And an imported theme
     When I activate the imported theme
     Then I see a page imported from theme
