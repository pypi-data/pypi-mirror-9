Feature: Email steps

    @email
    Scenario: Receive email
        When I send an email to "foo@bar.com" with subject "Hello world" and body "Greetings from a BDD world!"
        Then I should receive an email at "foo@bar.com"
        And I should receive an email at "foo@bar.com" with subject "Hello world"
        And I should receive an email at "foo@bar.com" containing "BDD"

    @email
    Scenario: Receive email with attachment
        When I send an email to "foo@bar.com" with subject "Hello world" and body "Greetings from a BDD world!" and attachment "test.txt"
        Then I should receive an email at "foo@bar.com" with attachment "test.txt"

    @email
    @web
    Scenario: Click link in an email
        Given a browser
        When I send an email to "foo@bar.com" with subject "Hello world" and body "Go to http://www.crypho.com"
        And I click the link in the email I received at "foo@bar.com"
        Then the browser's URL should be "http://www.crypho.com/"

