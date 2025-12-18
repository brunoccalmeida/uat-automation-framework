@e2e @cart @negative
Feature: Shopping Cart - Negative and Edge Cases
  As a Sauce Demo customer
  I want to see appropriate handling of cart edge cases
  So that I have a smooth shopping experience even in unexpected situations

  Background:
    Given I am logged in as "standard_user"
    And I am on the products page

  Scenario: Remove product from empty cart
    When I click the shopping cart icon
    Then I should be on the cart page
    And the cart should be empty
    And the cart badge should not be visible

  Scenario: Continue shopping from empty cart
    When I click the shopping cart icon
    And I click "Continue Shopping"
    Then I should be on the products page

  Scenario: Remove all items then add again
    Given I have added "Sauce Labs Backpack" to the cart
    When I click the shopping cart icon
    And I remove "Sauce Labs Backpack" from the cart
    Then the cart should be empty
    When I click "Continue Shopping"
    And I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show "1"

  Scenario: Add product shows Remove button (preventing duplicates)
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show "1"
    And the product button should change to "Remove"

  Scenario: Navigate to checkout with empty cart
    When I click the shopping cart icon
    And I click "Checkout"
    Then I should be on the checkout information page
