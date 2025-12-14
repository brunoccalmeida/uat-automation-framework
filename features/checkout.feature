Feature: Checkout
  As a Sauce Demo customer
  I want to complete the checkout process
  So that I can purchase my selected products

  Background:
    Given I am logged in as "standard_user"
    And I have added "Sauce Labs Backpack" to the cart
    And I am on the cart page

  Scenario: Complete checkout with valid information
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value    |
      | First Name | Marcus   |
      | Last Name  | Chen     |
      | Zip Code   | 12345    |
    And I click continue
    Then I should be on the checkout overview page
    And I should see "Sauce Labs Backpack" in the order summary
    And I should see the payment information
    And I should see the shipping information
    When I click finish
    Then I should see the order confirmation
    And the confirmation message should say "Thank you for your order!"

  Scenario: Cannot proceed without required information
    When I click the checkout button
    And I click continue
    Then the checkout error should mention "First Name is required"

  Scenario: Cannot proceed with incomplete information
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value |
      | First Name | Sofia |
    And I click continue
    Then the checkout error should mention "Last Name is required"

  Scenario: Verify order summary displays correct information
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value    |
      | First Name | Elena    |
      | Last Name  | Rodriguez|
      | Zip Code   | 54321    |
    And I click continue
    Then I should be on the checkout overview page
    And the item total should be displayed
    And the tax should be displayed
    And the total should be displayed

  Scenario: Cancel checkout and return to cart
    When I click the checkout button
    And I click cancel
    Then I should be on the cart page

  Scenario: Return to products from confirmation page
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value    |
      | First Name | Akira    |
      | Last Name  | Tanaka   |
      | Zip Code   | 99999    |
    And I click continue
    And I click finish
    And I click back home
    Then I should be on the products page
    And the cart should be empty
