*** Settings ***
Documentation     Tests for avoiding properties and handling descriptors.
Suite Setup       Run Tests    ${EMPTY}    test_libraries/avoid_properties_when_creating_libraries.robot
Resource          atest_resource.robot

*** Test Cases ***
Property
    Check Test Case    ${TESTNAME}
    Adding keyword failed    normal_property

Classmethod property
    Check Test Case    ${TESTNAME}
    Adding keyword failed    classmethod_property

Cached property
    Check Test Case    ${TESTNAME}
    Adding keyword failed    cached_property

Non-data descriptor
    Check Test Case    ${TESTNAME}
    Adding keyword failed    non_data_descriptor

Classmethod non-data descriptor
    Check Test Case    ${TESTNAME}
    Adding keyword failed    classmethod_non_data_descriptor    error=True

Data descriptor
    Check Test Case    ${TESTNAME}
    Adding keyword failed    data_descriptor

Classmethod data descriptor
    Check Test Case    ${TESTNAME}
    Adding keyword failed    classmethod_data_descriptor

Failing non-data descriptor
    Adding keyword failed    failing_non_data_descriptor    Getting handler method failed: ZeroDivisionError:

Failing classmethod non-data descriptor
    Adding keyword failed    failing_classmethod_non_data_descriptor    Getting handler method failed: ZeroDivisionError:    error=True

Failing data descriptor
    Adding keyword failed    failing_data_descriptor

Failing classmethod data descriptor
    Adding keyword failed    failing_classmethod_data_descriptor

*** Keywords ***
Adding keyword failed
    [Arguments]    ${name}    ${message}=Not a method or function.    ${error}=False
    IF    ${error} and not (3, 9) <= ${INTERPRETER.version_info} < (3, 13)
        Syslog Should Contain    | ERROR | Error in library 'AvoidProperties': Adding keyword '${name}' failed:
    ELSE
        Syslog Should Contain    | INFO \ | In library 'AvoidProperties': Adding keyword '${name}' failed: ${message}
    END
