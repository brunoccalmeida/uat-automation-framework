Feature: Shopping Cart
  As a Sauce Demo customer
  I want to manage my shopping cart
  So that I can purchase products

  Background:
    Given I am logged in as "standard_user"
    And I am on the products page

  Scenario: Add single product to cart
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show "1"
    And the product button should change to "Remove"

  Scenario: Add multiple products to cart
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    Then the cart badge should show "2"

  Scenario: View cart with added products
    Given I have added "Sauce Labs Backpack" to the cart
    When I click the shopping cart icon
    Then I should be on the cart page
    And I should see "Sauce Labs Backpack" in the cart
    And the cart should have 1 item

  Scenario: Remove product from cart
    Given I have added "Sauce Labs Backpack" to the cart
    When I click the shopping cart icon
    And I remove "Sauce Labs Backpack" from the cart
    Then the cart should be empty
    And the cart badge should not be visible

  Scenario: Continue shopping from cart
    Given I have added "Sauce Labs Backpack" to the cart
    And I am on the cart page
    When I click "Continue Shopping"
    Then I should be on the products page

  Scenario: Cart persists across pages
    Given I have added "Sauce Labs Backpack" to the cart
    When I navigate to different pages
    Then the cart badge should still show "1"
