from behave import given, when, then
from mock import patch
from os.path import dirname

from fastpay import FastPay

import requests
import json


def get_content_from_mock(filename):
    filepath = dirname(dirname(__file__)) + '/mock/' + filename
    with open(filepath) as f:
        content = json.load(f)

    return json.dumps(content).encode('utf-8')


@given('can create the fastpay client')
def step_impl_1(context):  # noqa
    try:
        context.fastpay = FastPay('SECRET_STRING')
    except NameError:
        assert context.failed


@when('create charge')
@patch('requests.post')
def step_impl_2(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge.txt')
    m.return_value = response

    context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa


@when('create charge no capture')
@patch('requests.post')
def step_impl_3(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_no_capture.txt')
    m.return_value = response

    context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa


@when('retrieve a charge')
@patch('requests.get')
def step_impl_4(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge.txt')
    m.return_value = response

    charge_id = 'ch_99a0699911fda5cb68ee1bbd3815300d8149f691'
    context.charge = context.fastpay.charge.retrieve(charge_id)


@when('retrieve a charge that is not captured yet')
@patch('requests.get')
def step_impl_5(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_no_capture.txt')
    m.return_value = response

    charge_id = 'ch_99a0699911fda5cb68ee1bbd3815300d8149f691'
    context.charge = context.fastpay.charge.retrieve(charge_id)


@when('retrieve all charges')
@patch('requests.get')
def step_impl_6(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_list.txt')
    m.return_value = response

    context.charges = context.fastpay.charge.all()


@when('retrieve {count:d} charges')
@patch('requests.get')
def step_impl_7(context, m, count):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_list_' + str(count) + '.txt')
    m.return_value = response

    context.charges = context.fastpay.charge.all(count)


@when('do capture of charge')
@patch('requests.post')
def step_impl_8(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge.txt')
    m.return_value = response

    context.charge.capture()


@when('do refund of charge')
@patch('requests.post')
def step_impl_9(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_refund.txt')
    m.return_value = response

    context.charge.refund()


@when('do partial refund of charge')
@patch('requests.post')
def step_impl_23(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_partial_refund.txt')
    m.return_value = response

    context.charge.refund(100)


@when('do partial refund of charge twice')
@patch('requests.post')
def step_impl_27(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_partial_refund_2.txt')
    m.return_value = response

    context.charge.refund(100)
    context.charge.refund(100)


@when('do partial refund of charge complete')
@patch('requests.post')
def step_impl_28(context, m):  # noqa
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('charge_partial_refund_all.txt')
    m.return_value = response

    context.charge.refund(100)
    context.charge.refund(100)
    context.charge.refund(200)


@when('create charge use invalid card')
@patch('requests.post')
def step_impl_10(context, m):  # noqa
    response = requests.Response()
    response.status_code = 402
    response._content = get_content_from_mock('card_error.txt')
    m.return_value = response

    try:
        context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa
    except Exception as ext:
        context.exception = ext


@when('create charge use invalid request')
@patch('requests.post')
def step_impl_11(context, m):  # noqa
    response = requests.Response()
    response.status_code = 400
    response._content = get_content_from_mock('invalid_request_error.txt')
    m.return_value = response

    try:
        context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa
    except Exception as ext:
        context.exception = ext


@when('create charge but internal server error')
@patch('requests.post')
def step_impl_12(context, m):  # noqa
    response = requests.Response()
    response.status_code = 500
    response._content = get_content_from_mock('api_error.txt')
    m.return_value = response

    try:
        context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa
    except Exception as ext:
        context.exception = ext


@when('create charge but return unknown error')
@patch('requests.post')
def step_impl_13(context, m):  # noqa
    response = requests.Response()
    response.status_code = 500
    response._content = get_content_from_mock('unknown_error.txt')
    m.return_value = response

    try:
        context.charge = context.fastpay.charge.create(amount=300, card="ch_t3qsFu3hf4FDFUyF02V8ra0Z", description="test fastpay description", capture=True)  # noqa
    except Exception as ext:
        context.exception = ext


@then('get a charge')
def step_impl_14(context):  # noqa
    assert 'ch_99a0699911fda5cb68ee1bbd3815300d8149f691' == context.charge.id


@then('get a charge that is not capture')
def step_impl_15(context):  # noqa
    assert 'ch_99a0699911fda5cb68ee1bbd3815300d8149f691' == context.charge.id
    assert context.charge.captured is False


@then('get a charge that was captured')
def step_impl_16(context):  # noqa
    assert context.charge.captured is True
    assert context.charge.refunded is False


@then('get a charge that was refunded')
def step_impl_17(context):
    assert context.charge.refunded is True
    for refund in context.charge.refunds:
        assert refund.__class__.__name__ == 'Refund'


@then('get a charge that was partial refunded')
def step_impl_24(context):
    assert context.charge.refunded is False
    for refund in context.charge.refunds:
        assert refund.__class__.__name__ == 'Refund'
        assert int(refund.amount) == context.charge.amount_refunded


@then('get a charge that was partial refunded twice')
def step_impl_25(context):
    amount_refunded = 0
    assert context.charge.refunded is False
    for refund in context.charge.refunds:
        assert refund.__class__.__name__ == 'Refund'
        amount_refunded += int(refund.amount)

    assert amount_refunded == context.charge.amount_refunded


@then('get a charge that was partial refunded complete')
def step_impl_26(context):
    amount_refunded = 0
    for refund in context.charge.refunds:
        assert refund.__class__.__name__ == 'Refund'
        amount_refunded += int(refund.amount)

    assert amount_refunded == context.charge.amount_refunded
    assert context.charge.amount_refunded == context.charge.amount
    assert context.charge.refunded is True


@then('get a retrieve charge')
def step_impl_18(context):
    assert 'ch_99a0699911fda5cb68ee1bbd3815300d8149f691' == context.charge.id


@then('get the all charges')
def step_impl_19(context):
    assert len(context.charges) == 3
    assert context.charges[0].id == "ch_Cfam8ouZ6UW9ElHAP3SCoyZf"
    assert context.charges[1].id == "ch_Cfam9ouZ6UW9ElHAP3SCoyZf"
    assert context.charges[2].id == "ch_Cfmb9ou9El6ZUWHAP3SCoyZf"


@then('get the charges of first')
def step_impl_20(context):
    assert context.charges[0].id == "ch_Cfam8ouZ6UW9ElHAP3SCoyZf"


@then('get the charges of second')
def step_impl_21(context):
    assert context.charges[1].id == "ch_Cfam9ouZ6UW9ElHAP3SCoyZf"


@then('raise "{text}"')
def step_impl_22(context, text):
    assert text == context.exception.__class__.__name__


@when('activate subscription')
@patch('requests.post')
def step_impl_29(context, m):
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('subscription_activate.txt')
    m.return_value = response

    context.subscription = context.fastpay.subscription.activate("subs_FMvoWYnanQKiH6fRw9NIYVHg")


@then('subscription status is "{status}"')
def step_impl_30(context, status):
    assert context.subscription.status == status
    assert context.subscription.plan.__class__.__name__ == 'Plan'


@when('cancel subscription')
@patch('requests.post')
def step_impl_31(context, m):
    response = requests.Response()
    response.status_code = 200
    response._content = get_content_from_mock('subscription_cancel.txt')
    m.return_value = response

    context.subscription = context.fastpay.subscription.cancel("subs_FMvoWYnanQKiH6fRw9NIYVHg")
