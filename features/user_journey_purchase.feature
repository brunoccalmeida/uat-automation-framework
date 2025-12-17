Feature: Complete Purchase Journey
  As a budget-conscious customer
  I want to find and purchase the cheapest product
  So that I can stay within my budget

  @e2e @user_journey
  Scenario: Customer finds and buys cheapest product successfully
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page
    When I sort products by price low to high
    And I add the first product to cart
    And I click the shopping cart
    Then I should be on the cart page
    And the cart should have 1 item
    When I proceed to checkout
    Then I should be on the checkout information page
    When I enter checkout information:
      | field      | value      |
      | first_name | John       |
      | last_name  | Doe        |
      | zip_code   | 12345      |
    And I click continue to review order
    Then I should be on the checkout overview page
    When I click finish to complete order
    Then I should see the order confirmation
    And the confirmation message should be "Thank you for your order!"
    When I click back to products
    Then I should be on the inventory page
