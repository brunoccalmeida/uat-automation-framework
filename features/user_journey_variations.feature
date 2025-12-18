@e2e @user_journey @critical
Feature: Complete Purchase - Multiple User Journeys
  As a Sauce Demo customer
  I want to complete purchases in different ways
  So that I can validate various shopping patterns

  @e2e @user_journey @multiple_items
  Scenario: Customer buys multiple products
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    And I add "Sauce Labs Bolt T-Shirt" to the cart
    Then the cart badge should show "3"
    When I click the shopping cart icon
    Then I should be on the cart page
    And the cart should have 3 items
    When I click "Checkout"
    Then I should be on the checkout information page
    When I enter checkout information:
      | field      | value      |
      | first_name | Jane       |
      | last_name  | Smith      |
      | zip_code   | 90210      |
    And I click continue to review order
    Then I should be on the checkout overview page
    And I should see "Sauce Labs Backpack" in the order summary
    And I should see "Sauce Labs Bike Light" in the order summary
    And I should see "Sauce Labs Bolt T-Shirt" in the order summary
    When I click finish to complete order
    Then I should see the order confirmation
    And the confirmation message should be "Thank you for your order!"

  @e2e @user_journey @price_conscious
  Scenario: Price-conscious shopper compares before buying
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page
    When I sort products by price low to high
    And I add the first product to cart
    When I sort products by price high to low
    Then the cart badge should still show "1"
    When I click the shopping cart icon
    Then the cart should have 1 item
    When I click "Checkout"
    And I enter checkout information:
      | field      | value      |
      | first_name | Budget     |
      | last_name  | Shopper    |
      | zip_code   | 10001      |
    And I click continue to review order
    And I click finish to complete order
    Then I should see the order confirmation

  @e2e @user_journey @cart_management
  Scenario: Customer adds multiple items then removes some
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page
    When I add "Sauce Labs Backpack" to the cart
    And I add "Sauce Labs Bike Light" to the cart
    And I add "Sauce Labs Bolt T-Shirt" to the cart
    And I add "Sauce Labs Fleece Jacket" to the cart
    Then the cart badge should show "4"
    When I click the shopping cart icon
    Then the cart should have 4 items
    When I remove "Sauce Labs Bolt T-Shirt" from the cart
    And I remove "Sauce Labs Fleece Jacket" from the cart
    Then the cart should have 2 items
    When I click "Checkout"
    And I enter checkout information:
      | field      | value      |
      | first_name | Decisive   |
      | last_name  | Customer   |
      | zip_code   | 33101      |
    And I click continue to review order
    Then I should see "Sauce Labs Backpack" in the order summary
    And I should see "Sauce Labs Bike Light" in the order summary
    When I click finish to complete order
    Then I should see the order confirmation
