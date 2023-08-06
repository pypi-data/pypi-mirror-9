Feature: refund charge
    Scenario: create charge and refund
       Given can create the fastpay client
        When create charge no capture
         AND do refund of charge
        Then get a charge that was refunded

    Scenario: create charge and partial refund
       Given can create the fastpay client
        When create charge
         And do partial refund of charge
        Then get a charge that was partial refunded

    Scenario: create charge and partial refund twice
       Given can create the fastpay client
        When create charge
         And do partial refund of charge twice
        Then get a charge that was partial refunded twice

    Scenario: create charge and partial refund complete
       Given can create the fastpay client
        When create charge
         And do partial refund of charge complete
        Then get a charge that was partial refunded complete
