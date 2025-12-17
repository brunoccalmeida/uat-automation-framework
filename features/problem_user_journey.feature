@e2e @user_journey @problem_user
Feature: Problem User Journey
  As a QA engineer
  I want to validate the experience of a problem user
  So that I can detect visual glitches and unexpected behaviors

  Scenario: Problem user logs in and navigates to inventory
    Given I am on the Sauce Demo login page
    When I login with username "problem_user" and password "secret_sauce"
    Then I should be on the inventory page
    And the product images should be broken
    And the product names should be visible
