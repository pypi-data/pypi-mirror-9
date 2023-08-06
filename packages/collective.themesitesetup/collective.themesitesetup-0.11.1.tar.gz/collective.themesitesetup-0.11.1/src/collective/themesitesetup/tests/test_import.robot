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

An imported theme
    Go to  ${PLONE_URL}/@@theming-controlpanel

    Page should contain  Upload Zip file
    Click button  Upload Zip file

    Wait until page contains element  name=import
    Choose file  themeArchive  ${CURDIR}/my-theme.zip

    Click button  Import

    Wait until page contains  Modify theme
    Page should contain  My Theme

I open the import form
    Go to  ${PLONE_URL}/++theme++my-theme/@@import-site-setup
    Page should contain  Import site setup

I submit the import form
    Page should contain  Import site setup

    Set window size   768  576
    Capture and crop page screenshot  import-site-setup.png  content

    Click button  Import
    Wait until page contains  Done

I see a page imported from theme
    Page should contain  Hello World

*** Test cases ***

Site setup can be imported from theme
    Given a site administrator
      And an imported theme
     When I open the import form
      And I submit the import form
     Then I see a page imported from theme
