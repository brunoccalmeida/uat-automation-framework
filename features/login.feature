Feature: User Login
  As a Parabank user
  I want to log into my account
  So that I can access banking features

  Background:
    Given the user is on the Parabank homepage

  Scenario: Successful login with valid credentials
    Given the user has a registered account with username "testuser" and password "testpass123"
    When the user enters username "testuser"
    And the user enters password "testpass123"
    And the user clicks the login button
    Then the user should be logged in successfully
    And the user should see the account overview page

  Scenario: Failed login with invalid credentials
    When the user enters username "invaliduser"
    And the user enters password "wrongpassword"
    And the user clicks the login button
    Then the user should see an error message
    And the user should remain on the login page
