Feature: User Login
  As a Sauce Demo customer
  I want to log into my account
  So that I can shop for products

  Background:
    Given I am on the Sauce Demo login page

  Scenario: Successful login with standard user
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be logged in successfully
    And I should see the products page
    And the page title should be "Products"

  Scenario: Failed login with invalid credentials
    When I login with username "invalid_user" and password "wrong_password"
    Then I should see login error message
    And I should remain on the login page

  Scenario: Failed login with locked out user
    When I login with username "locked_out_user" and password "secret_sauce"
    Then I should see login error message
    And the error should mention "locked out"

  Scenario: Successful logout after login
    Given I am logged in as "standard_user"
    When I click the menu button
    And I click logout
    Then I should be redirected to the login page
