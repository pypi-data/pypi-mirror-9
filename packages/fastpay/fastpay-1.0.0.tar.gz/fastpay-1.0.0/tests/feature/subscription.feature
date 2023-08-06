Feature: subscription
    Scenario: activate subscription
       Given can create the fastpay client
        When activate subscription
        Then subscription status is "active"

    Scenario: cancel subscription
       Given can create the fastpay client
        When cancel subscription
        Then subscription status is "cancelled"
