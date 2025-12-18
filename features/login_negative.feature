@e2e @login @negative
Feature: Login - Negative and Edge Cases
  As a user
  I want to see clear feedback when login fails or is misused
  So that I can understand and correct my mistakes

  Background:
    Given I am on the Sauce Demo login page

  Scenario: Login with empty username and password
    When I click the login button
    Then I should see login error message
    And the error should mention "Username is required"

  Scenario: Login with empty password
    When I enter username "standard_user"
    And I click the login button
    Then I should see login error message
    And the error should mention "Password is required"

  Scenario: Login with special characters
    When I login with username "!@#$%" and password "^&*()"
    Then I should see login error message
    And I should remain on the login page

  Scenario: Multiple failed login attempts
    When I login with username "invalid_user" and password "wrong_password"
    And I login with username "invalid_user" and password "wrong_password"
    And I login with username "invalid_user" and password "wrong_password"
    Then I should see login error message
    And the error should mention "do not match"
    And I should remain on the login page

  Scenario: Login with SQL injection attempt
    When I login with username "' OR 1=1 --" and password "password"
    Then I should see login error message
    And I should remain on the login page
