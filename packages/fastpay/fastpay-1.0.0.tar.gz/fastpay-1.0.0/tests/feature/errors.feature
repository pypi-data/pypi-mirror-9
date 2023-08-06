Feature: errors
    Scenario: card error
       Given can create the fastpay client
        When create charge use invalid card
        Then raise "CardError"

    Scenario: api error
       Given can create the fastpay client
        When create charge but internal server error
        Then raise "ApiError"

    Scenario: invalid request error
       Given can create the fastpay client
        When create charge use invalid request
        Then raise "InvalidRequestError"

    Scenario: fastpay error
       Given can create the fastpay client
        When create charge but return unknown error
        Then raise "FastPayError"
