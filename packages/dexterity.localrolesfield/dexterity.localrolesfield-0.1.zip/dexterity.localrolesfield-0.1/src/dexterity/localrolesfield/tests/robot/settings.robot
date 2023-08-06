*** Settings ***
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  plone.app.robotframework.keywords.Debugging

Test Setup  Test Setup
Test Teardown  Close all browsers

*** Variables ***
${global_first_row_xpath} =    xpath=//div[@class="documentContent"]/form[1]/div[1]/div/div/table/tbody/tr[1]
${global_state_xpath} =        ${global_first_row_xpath}/td[1]/select
${global_value_xpath} =        ${global_first_row_xpath}/td[2]/input
${global_contributor_xpath} =  ${global_first_row_xpath}/td[3]/span/span[1]/input

${localrolefield_first_row_xpath} =  xpath=//div[@class="documentContent"]/form[1]/div[2]/div/div/table/tbody/tr[1]
${localrolefield_state_xpath} =      ${localrolefield_first_row_xpath}/td[1]/select
${localrolefield_value_xpath} =      ${localrolefield_first_row_xpath}/td[2]/input
${localrolefield_editor_xpath} =     ${localrolefield_first_row_xpath}/td[3]/span/span[2]/input

*** Test Cases ***

Test global config dexterity form
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    # check form is empty
    List selection should be  ${global_state_xpath}  pending
    Element should contain  ${global_value_xpath}  ${EMPTY}
    Checkbox should not be selected  ${global_contributor_xpath}

    # fill form
    Select from list by value  ${global_state_xpath}  private
    Input text  ${global_value_xpath}  kate
    Select checkbox  ${global_contributor_xpath}
    Click button  id=form-buttons-apply

    # Redirected
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    List selection should be  ${global_state_xpath}  private
    TextField value should be  ${global_value_xpath}  kate
    Checkbox should be selected  ${global_contributor_xpath}

Test field config dexterity form
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    # check form is empty
    List selection should be  ${localrolefield_state_xpath}  pending
    Element should contain  ${localrolefield_value_xpath}  ${EMPTY}
    Checkbox should not be selected  ${localrolefield_editor_xpath}

    # fill form
    Select from list by value  ${localrolefield_state_xpath}  published
    Input text  ${localrolefield_value_xpath}  editor
    Select checkbox  ${localrolefield_editor_xpath}
    Click button  id=form-buttons-apply

    # Redirected
    Go to  ${PLONE_URL}/dexterity-types/testingtype/@@localroles
    List selection should be  ${localrolefield_state_xpath}  published
    TextField value should be  ${localrolefield_value_xpath}  editor
    Checkbox should be selected  ${localrolefield_editor_xpath}


*** Keywords ***
Test Setup
    Open SauceLabs test browser
    Go to  ${PLONE_URL}
    Enable autologin as  Manager
