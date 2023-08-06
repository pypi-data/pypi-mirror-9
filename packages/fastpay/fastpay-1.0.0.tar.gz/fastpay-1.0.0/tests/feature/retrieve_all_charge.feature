Feature: retrieve charges
    Scenario: retrieve all charges
       Given can create the fastpay client
        When retrieve all charges
        Then get the all charges

    Scenario: retrieve 2 charges
       Given can create the fastpay client
        When retrieve 2 charges
        Then get the charges of first
         And get the charges of second
