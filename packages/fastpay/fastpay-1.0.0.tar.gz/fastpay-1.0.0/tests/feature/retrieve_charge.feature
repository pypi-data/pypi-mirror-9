Feature: retrieve a charge
    Scenario: retrieve
       Given can create the fastpay client
        When retrieve a charge
        Then get a retrieve charge

    Scenario: retrieve and capture
       Given can create the fastpay client
        When retrieve a charge that is not captured yet
         AND do capture of charge
        Then get a charge that was captured

    Scenario: retrieve and refund
       Given can create the fastpay client
        When retrieve a charge that is not captured yet
         AND do refund of charge
        Then get a charge that was refunded
