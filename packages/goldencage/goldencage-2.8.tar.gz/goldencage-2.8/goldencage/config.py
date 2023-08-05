# encoding=utf-8


APPWALLLOG_MAPPING = {
    'waps': {'identity': ('adv_id', 'key'),
             'cost': 'points',
             'user_id': 'key',
             'product_id': 'adv_id',
             'product_name': 'ad_name'
             },
    'youmi_ios': {'identity': 'order',
                  'cost': 'points',
                  'user_id': 'user',
                  'product_id': 'adid',
                  'product_name': 'ad'
                  },
    'youmi_adr': {'identity': 'order',
                  'cost': 'points',
                  'user_id': 'user',
                  'product_id': 'ad',
                  'product_name': 'ad',
                  },
    'dianjoy_adr': {'identity': ('device_id', 'pack_name',
                                 'trade_type', 'task_id'),
                    'cost': 'currency',
                    'user_id': 'snuid',
                    'product_id': 'pack_name',
                    'product_name': 'ad_name',
                    },
    'qumi': {'identity': 'order',
             'cost': 'points',
             'user_id': 'user',
             'product_id': 'ad',
             'product_name': 'ad',
        },
}

PAYMENT_MAPPING = {
    'alipay': {'account': 'buyer_id',
               'email': 'buyer_email',
               'value': 'total_fee',
               'transaction_id': 'trade_no',
               'order_id': 'out_trade_no',
               'status': 'trade_status'
               },
    'wechatpay': {'account': 'OpenId',
                  'email': 'OpenId',
                  'value': 'total_fee',
                  'transaction_id': 'transaction_id',
                  'order_id': 'out_trade_no',
                  'status': 'trade_state'
                  }
}
PAYMENT_FINISH = {
    'alipay': 'TRADE_FINISHED',
    'wechatpay': '0',
}

PAYMENT_SCALE = {
    'alipay': 100,
    'wechatpay': 1,
}

EXCHANGE_RATE = 25  # 一RMB对应金币数

ALIPAY_PUBLIC_KEY = (
    '-----BEGIN PUBLIC KEY-----\n'
    'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnxj/9qwVfgoUh/y2W89L6BkRA'
    'FljhNhgPdyPuBV64bfQNN1PjbCzkIM6qRdKBoLPXmKKMiFYnkd6rAoprih3/PrQE'
    'B/VsW8OoM8fxn67UDYuyBTqA23MML9q1+ilIZwBC2AQ2UBVOrFXfFl75p6/B5Ksi'
    'NG9zpgmLCUYuLkxpLQIDAQAB'
    '\n-----END PUBLIC KEY-----'
)
