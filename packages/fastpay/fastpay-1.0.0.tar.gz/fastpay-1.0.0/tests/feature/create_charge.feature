Feature: create charge
    Scenario: create charge
       Given can create the fastpay client
        When create charge
        Then get a charge

    Scenario: create charge no capture
       Given can create the fastpay client
        When create charge no capture
        Then get a charge that is not capture

    Scenario: create charge and capture
       Given can create the fastpay client
        When create charge no capture
         AND do capture of charge
        Then get a charge that was captured
