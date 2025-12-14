Feature: User Login
  As a Parabank user
  I want to log into my account
  So that I can access banking features

  Background:
    Given the user is on the Parabank homepage

  Scenario: Successful login with valid credentials
    Given the user registers a new account
    And the user logs out
    When the user logs in with the registered credentials
    Then the user should be logged in successfully
    And the user should see the account services menu

  Scenario: Failed login with invalid credentials
    When the user enters username "invaliduser"
    And the user enters password "wrongpassword"
    And the user clicks the login button
    Then the user should see an error message
    And the user should remain on the login page
