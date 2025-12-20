@e2e @smoke
Feature: Application Smoke Tests
  As a QA engineer
  I want to verify basic application functionality
  So that I can ensure the system is operational

  Scenario: Homepage loads successfully
    When I navigate to the Sauce Demo homepage
    Then the login page should be displayed
    And the page title should contain "Swag Labs"

  Scenario: Login form elements are present
    Given I am on the Sauce Demo homepage
    Then the username field should be visible
    And the password field should be visible
    And the login button should be visible

  Scenario: Application accepts valid login
    Given I am on the Sauce Demo homepage
    When I enter valid credentials
    Then I should be redirected to the inventory page

  Scenario: Application rejects invalid login
    Given I am on the Sauce Demo homepage
    When I enter invalid credentials
    Then I should see an error message
    And I should remain on the login page
