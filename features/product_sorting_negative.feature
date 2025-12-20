@e2e @negative @edgecase @sorting
Feature: Product Sorting - Edge Cases
  As a QA engineer
  I want to test edge cases in product sorting
  So that I can ensure the sorting logic handles unusual scenarios correctly

  Background:
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page

  Scenario: Sort option selected is visually distinct
    When I select sort option "za"
    Then the sort dropdown should show "za" as selected
    And I verify the sort dropdown has the correct option selected

  Scenario: Multiple rapid sort changes
    When I select sort option "za"
    And I select sort option "lohi"
    And I select sort option "hilo"
    And I select sort option "az"
    Then products should be sorted by name A to Z
    And the sort dropdown should show "az" as selected

  Scenario: Sort after navigation to cart and back
    When I select sort option "hilo"
    And I click the shopping cart icon
    And I click the continue shopping button
    Then products should be sorted by name A to Z
    And the sort dropdown should show "az" as selected

  Scenario: Sort persists after adding product
    When I select sort option "za"
    Then products should be sorted by name Z to A
    When I add "Test.allTheThings() T-Shirt (Red)" to the cart
    Then products should be sorted by name Z to A
    And the sort dropdown should show "za" as selected

  Scenario: Verify all sort options are available
    Then I should see all sort options in the dropdown
    And the sort dropdown should contain "Name (A to Z)"
    And the sort dropdown should contain "Name (Z to A)"
    And the sort dropdown should contain "Price (low to high)"
    And the sort dropdown should contain "Price (high to low)"
