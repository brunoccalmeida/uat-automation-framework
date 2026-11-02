@e2e @edgecase @product_details
Feature: Product Details Known Defects
  As a QA engineer
  I want to validate the known defects of the product details page
  So that the framework proves it detects broken flows, not only working ones

  # Note: "problem_user" and "error_user" have intentional defects. These
  # scenarios assert them, so a scenario fails if Sauce Demo changes the defect.

  @problem_user
  Scenario: The problem user opens the next product's details
    Given I am logged in as "problem_user"
    When I open the details of "Sauce Labs Backpack"
    Then the details should show "Sauce Labs Fleece Jacket"

  @error_user
  Scenario: The error user sees no product description
    Given I am logged in as "error_user"
    When I open the details of "Sauce Labs Backpack"
    Then the details should show "Sauce Labs Backpack"
    And the details should have no description
