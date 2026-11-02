@e2e @edgecase @error_user
Feature: Error User Known Defects
  As a QA engineer
  I want to validate the known defects of the error user
  So that the framework proves it detects broken flows, not only working ones

  # Note: "error_user" has intentional defects. These scenarios assert them,
  # so a scenario fails if Sauce Demo changes the defect.

  Background:
    Given I am logged in as "error_user"

  Scenario: Sorting raises an error alert and keeps the default order
    When I select sort option "za"
    Then I should see an alert saying "Sorting is broken! This error has been reported to Backtrace."
    And the sort dropdown should show "az" as selected
    And products should be sorted by name A to Z

  Scenario Outline: Some products cannot be added to the cart
    When I add "<product>" to the cart
    Then the cart badge should still show "0"

    Examples:
      | product                           |
      | Sauce Labs Bolt T-Shirt           |
      | Sauce Labs Fleece Jacket          |
      | Test.allTheThings() T-Shirt (Red) |

  Scenario: Products cannot be removed from the products page
    Given I have added "Sauce Labs Backpack" to the cart
    When I remove "Sauce Labs Backpack" from the products page
    Then the cart badge should still show "1"

  Scenario: Checkout ignores the last name and still continues
    Given I have added "Sauce Labs Backpack" to the cart
    And I am on the cart page
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value |
      | First Name | Ada   |
      | Last Name  | Byron |
      | Zip Code   | 12345 |
    Then the last name field should be empty
    When I click continue
    Then I should be on the checkout overview page

  Scenario: Finishing the order fails and keeps the item in the cart
    Given I have added "Sauce Labs Backpack" to the cart
    And I am on the cart page
    When I click the checkout button
    And I fill in the checkout information:
      | field      | value |
      | First Name | Ada   |
      | Zip Code   | 12345 |
    And I click continue
    And I try to finish the order
    Then I should still be on the checkout overview page
    And the cart badge should still show "1"
