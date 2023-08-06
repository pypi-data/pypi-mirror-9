FastPay SDK for Python
======================

FastPayをPythonで簡単に利用するためのSDKです。

インストール
------------

pipコマンドでインストールを行います

.. code-block:: bash

    $ pip install fastpay


使い方
------

FastPayではクレジットカード情報は直接扱わず、FastPay側でトークン化したものを使って安全に決済を行います。
トークン化など全体的な流れについては、 `FastPayのドキュメント[支払いフロー] <https://fastpay.yahoo.co.jp/docs/flow>`_ をご覧ください。

課金
~~~~

詳細についてはFastPayのドキュメント `新規決済の作成 <https://fastpay.yahoo.co.jp/docs/pay/new>`_ をご覧ください。

.. code-block:: python

    import fastpay

    # fastpay.jsで取得します。"fastpayToken"というパラメータでhiddenのinputにて送信されます。
    token = "CARD_TOKEN"

    client = fastpay.FastPay("シークレット")

    try:
        charge = client.charge.create(
            amount=100,  # 金額
            card=token,  # fastpay.jsで取得したトークン
            description="fastpay@example.com",  # 詳細情報。フリーフォームです
            capture=False  # 確定を行わない場合False。同時確定の場合は省略またはTrueを指定する
        )
        # 例外が上がらなかった場合、課金成功
        print("注文完了 ID: %s" % charge.id)  # -> 注文ID表示
    except fastpay.CardError as e:
        # カード与信エラー。必要に応じて再度画面を表示など行う
        if e.code == FastPayError.CARD_DECLINED:
            print("カード決済に失敗しました。（オーソリ時のエラー）")
        elif e.code == FastPayError.INCORRECT_CVC:
            print("セキュリティコードが正しくありません。（オーソリ時のエラー）")
        # 他のコードは https://fastpay.yahoo.co.jp/docs/error を参照
    except fastpay.FastPayError as e:
        print("システムエラー %s" % str(e))

確定
~~~~

詳細についてはFastPayのドキュメント `決済の確定 <https://fastpay.yahoo.co.jp/docs/pay/fixed>`_ をご覧ください。

.. code-block:: python

    import fastpay

    client = fastpay.FastPay("シークレット")

    try:
        charge = client.charge.retrieve("対象のcharge_id")
        # 確定を行う
        charge.capture()
        # 例外が上がらなかった場合、確定成功
        print("確定成功")
    except fastpay.FastPayError as e:
        print("システムエラー %s" % str(e))

返金
~~~~

詳細についてはFastPayのドキュメント `払い戻し処理 <https://fastpay.yahoo.co.jp/docs/pay/rtnpay>`_ をご覧ください。

.. code-block:: python

    import fastpay

    client = fastpay.FastPay("シークレット")

    try:
        charge = client.charge.retrieve("対象のcharge_id")
        # 確定を行う。引数を与えることで部分返金も可能
        charge.refund()
        # 例外が上がらなかった場合、払い戻し成功
        print("払い戻し成功")
    except fastpay.FastPayError as e:
        print("システムエラー %s" % str(e))

継続課金の開始
~~~~~~~~~~~~~~

継続課金についてはまずはFastPayのドキュメント `継続課金とは <https://fastpay.yahoo.co.jp/docs/guide_subscription>`_ をごらんください。

.. code-block:: python

    import fastpay

    client = fastpay.FastPay("シークレット")

    try:
        subscription = client.subscription.activate("対象のsubscription_id")
        print("継続課金開始成功")
    except fastpay.FastPayError as e:
        print("システムエラー %s" % str(e))

継続課金の停止
~~~~~~~~~~~~~~

継続停止についてもFastPayのドキュメント `継続課金とは <https://fastpay.yahoo.co.jp/docs/guide_subscription>`_ をごらんください。

.. code-block:: python

    import fastpay

    client = fastpay.FastPay("シークレット")

    try:
        subscription = client.subscription.cancel("対象のsubscription_id")
        print("継続課金停止成功")
    except fastpay.FastPayError as e:
        print("システムエラー %s" % str(e))

License
-------

MITライセンスにて提供しています。詳しくはLICENSEをご覧ください。
