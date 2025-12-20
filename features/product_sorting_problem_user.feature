@e2e @edgecase @sorting @problem_user
Feature: Product Sorting - Problem User
  As a QA
  I want to validate known bugs and edge cases for the problem_user
  So that I can ensure the system handles problematic users as expected

  # Note: "problem_user" has intentional sorting bug (sorting does not work)
  Scenario: Sorting does not work for problem_user
    Given I am on the Sauce Demo login page
    When I login with username "problem_user" and password "secret_sauce"
    Then I should be on the inventory page
    And I select sort option "za"
    Then products should NOT be sorted by name Z to A
    Then the sort dropdown should show "az" as selected
