@e2e @functional @product_details
Feature: Product Details
  As a Sauce Demo customer
  I want to see the details of a product
  So that I can decide whether to buy it

  Background:
    Given I am logged in as "standard_user"

  Scenario Outline: Details match the product card
    When I open the details of "<product>"
    Then the details should match the product card

    Examples:
      | product                           |
      | Sauce Labs Backpack               |
      | Sauce Labs Bike Light             |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Fleece Jacket          |
      | Sauce Labs Onesie                 |
      | Test.allTheThings() T-Shirt (Red) |

  Scenario: Add product to cart from its details
    Given I am on the details of "Sauce Labs Backpack"
    When I add the product to the cart from its details
    Then the cart badge should show "1"
    And the details button should show "Remove"

  Scenario: Remove product from cart on its details
    Given I am on the details of "Sauce Labs Backpack"
    And I have added the product to the cart from its details
    When I remove the product from the cart on its details
    Then the cart badge should show "0"
    And the details button should show "Add to cart"

  Scenario: Back to products keeps the cart
    Given I am on the details of "Sauce Labs Backpack"
    And I have added the product to the cart from its details
    When I go back to the products page
    Then I should be on the products page
    And the cart badge should show "1"
