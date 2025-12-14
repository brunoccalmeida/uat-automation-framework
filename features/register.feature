Feature: User Registration
  As a new Parabank user
  I want to register a new account
  So that I can access banking features

  Background:
    Given the user is on the Parabank homepage

  Scenario: Successful user registration
    When the user navigates to the registration page
    And the user fills in the registration form with unique username
      | field      | value                 |
      | first_name | Bruno                 |
      | last_name  | Almeida               |
      | address    | 742 Evergreen Terrace |
      | city       | Curitiba              |
      | state      | PR                    |
      | zip_code   | 80420                 |
      | phone      | 41-98765-4321         |
      | ssn        | 987-65-4321           |
    And the user submits the registration form
    Then the user should see a success message
    And the user should be logged in automatically
