@e2e @functional
Feature: Product Sorting
  As a customer
  I want to sort products by different criteria
  So that I can find products more easily

  Background:
    Given I am on the Sauce Demo login page
    When I login with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page

  Scenario: Sorting resets to default after page refresh
    When I select sort option "za"
    And I refresh the page
    Then products should be sorted by name A to Z
    And the sort dropdown should show "az" as selected

  Scenario: Default sorting is A to Z
    Then products should be sorted by name A to Z
    And the sort dropdown should show "az" as selected

  Scenario: Sort products by name Z to A
    When I select sort option "za"
    Then products should be sorted by name Z to A

  Scenario: Sort products by price low to high
    When I select sort option "lohi"
    Then products should be sorted by price low to high

  Scenario: Sort products by price high to low
    When I select sort option "hilo"
    Then products should be sorted by price high to low

  Scenario: Change sorting multiple times
    When I select sort option "za"
    And I select sort option "lohi"
    Then products should be sorted by price low to high
    And the sort dropdown should show "lohi" as selected

  Scenario: Sorting persists product count
    When I select sort option "hilo"
    Then I should see 6 products on the page

  Scenario: Sorting after adding and removing products from cart
    When I add "Sauce Labs Backpack" to the cart
    And I remove "Sauce Labs Backpack" from the cart
    And I select sort option "za"
    Then products should be sorted by name Z to A
    Then the sort dropdown should show "za" as selected
