Feature: Retrieve Elasticity Rule
  As a user
  I want to get a specific elasticity rule
  In order to manage my rules

  @basic
  Scenario Outline: Retrieve a created rule

    Given a created rule in the in the "<server_id>"
    When I retrieve the rule in "<server_id>"
    Then I obtain the Rule data

    Examples:

    | server_id   |
    | qatestserver|
    | qaserver    |

  Scenario Outline: Retrieve a non existent rule

    Given a created rule in the in the "<server_id>"
    When I retrieve "<another_rule_id>"
    Then I obtain an "<Error_code>" and the "<FaultElement>"

    Examples:

    | server_id   |  another_rule_id | Error_code  | FaultElement  |
    | qatestserver|  testing         | 404         | itemNotFound  |
    | qatestserver|  qa              | 404         | itemNotFound  |

  Scenario Outline: Retrieve a existent rule in other server

    Given a created rule in the in the "<server_id>"
    When I retrieve the rule in "<another_server_id>"
    Then I obtain an "<Error_code>" and the "<FaultElement>"

    Examples:

    | server_id   | another_server_id | Error_code  | FaultElement  |
    | qatestserver| testingserver     | 404         | itemNotFound  |
    | qatestserver| qaserver          | 404         | itemNotFound  |

  @security
  Scenario Outline: Retrieve a rule with incorrect token

    Given a created rule in the in the "<server_id>"
    And incorrect "<token>"
    When I retrieve the rule in "<server_id>"
    Then I obtain an "<Error_code>" and the "<FaultElement>"

    Examples:

      | Error_code  | FaultElement  | token     | server_id   |
      | 401         | unauthorized  | 1a2b3c    | qatestserver|
      | 401         | unauthorized  | old_token | qatestserver|
      | 401         | unauthorized  |           | qatestserver|
      | 401         | unauthorized  | null      | qatestserver|
