@e2e @checkout @negative
Feature: Checkout - Negative and Edge Cases
  As a Sauce Demo customer
  I want appropriate validation during checkout
  So that I can correct errors and complete my purchase successfully

  Background:
    Given I am logged in as "standard_user"
    And I have added "Sauce Labs Backpack" to the cart
    And I am on the cart page
    When I click the checkout button

  Scenario: ZIP code with invalid format (letters)
    When I fill in the checkout information:
      | field      | value    |
      | First Name | John     |
      | Last Name  | Doe      |
      | Zip Code   | ABCDE    |
    And I click continue
    Then I should be on the checkout overview page

  Scenario: First name with special characters
    When I fill in the checkout information:
      | field      | value    |
      | First Name | @#$%     |
      | Last Name  | Smith    |
      | Zip Code   | 12345    |
    And I click continue
    Then I should be on the checkout overview page

  Scenario: Last name with numbers
    When I fill in the checkout information:
      | field      | value    |
      | First Name | Jane     |
      | Last Name  | 12345    |
      | Zip Code   | 54321    |
    And I click continue
    Then I should be on the checkout overview page

  Scenario: Very long input values
    When I fill in the checkout information:
      | field      | value                                        |
      | First Name | ThisIsAVeryLongFirstNameWithMoreThanFiftyChars |
      | Last Name  | ThisIsAVeryLongLastNameWithMoreThanFiftyChars  |
      | Zip Code   | 123456789012345                              |
    And I click continue
    Then I should be on the checkout overview page

  Scenario: Cancel checkout from overview page
    When I fill in the checkout information:
      | field      | value    |
      | First Name | Cancel   |
      | Last Name  | User     |
      | Zip Code   | 11111    |
    And I click continue
    And I click cancel
    Then I should be on the products page

  Scenario: Only spaces in required fields
    When I fill in the checkout information:
      | field      | value |
      | First Name |       |
      | Last Name  |       |
      | Zip Code   |       |
    And I click continue
    Then the checkout error should mention "First Name is required"
