#!/opt/anaconda/bin/python
from __future__ import print_function

import time

import pandas as pd
import gate_api
from gate_api.exceptions import ApiException, GateApiException
import os
import datetime
import numpy as np
import logging
# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.
# Configure APIv4 key authorization
### 查询k线信息，并保存数据到
class Gate_Api():
    def __init__(self, key: str, secret: str, host='https://api.gateio.ws/api/v4'):
        self.configuration = gate_api.Configuration(
            host=host,
            key=key,
            secret=secret
        )
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=format, filename ='log.txt')
        logging.getLogger('gate')

        self.api_client =gate_api.ApiClient(self.configuration)
        self.create_order_record = []  # 下单信息记录
        self.get_order_record = []  # 订单状态查询记录
        self.holing_record = []  # 持仓情况
        self.list_order = []  # 显示所有订
        self.list_trigger_order = []  # 显示所有限价订单
        self.price_record = []  # 记录所有订单
        self.account = [] #记录所有当前是账户信息
        self.future_price_record = [] # 记录查询的期货k线信息
        self.future_orders = [] # 记录
        self.create_futures_trigger_order =[] # 记录期货下单信息
        self.orders_record =[] #record the orders info
        self.get_order_record = []  # record the orders info
        self.contracts =[] # record every futures contract traded
    ## 查询K线数据
    def candelsticks(self, Type: str, currency_pair: str,interval: str, limit=1, _from=None, to=None, settle='usdt', contract='BTC_USDT'):
        api_client = gate_api.ApiClient(self.configuration)
        if (_from!= None) and (to !=None):

            if Type == 'Spot':
                api_instance = gate_api.SpotApi(api_client)
                currency_pair = currency_pair
                interval = interval
                ls = locals()  #
                try:
                    # Market candlesticks

                    interval_scale_set = {'d': 24 * 60 * 60, 'h': 60 * 60, 'm': 60, 's': 1}
                    interval_time = int(interval[0])
                    interval_scale = interval[1]
                    time_amount = interval_time * interval_scale_set[interval_scale]
                    time_range = to - _from

                    loop_time = int(time_range / (time_amount)/1000) + 1
                    price = []
                    if loop_time <= 1:
                        print('a')
                        api_response = api_instance.list_candlesticks(currency_pair, limit=limit, interval=interval,
                                                                      _from=_from, to=to)
                        for i in api_response:
                            pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                                  'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                                  'LowPrice': float(i[4]), 'Open': float(i[5])}
                            price.append(pp)
                    else:
                        time_seq = [_from, ]
                        for k in range(0, loop_time-1 ):
                            next_to = time_seq[k] +999 * time_amount
                            time_seq.append(next_to)
                        time_seq.append(to)
                        price = []
                        price_slice = []

                        for k in range(0, loop_time ):
                            print('b')

                            api_response = api_instance.list_candlesticks(currency_pair, interval=interval,
                                                                          _from=time_seq[k], to=time_seq[k + 1])
                            for i in api_response:

                                pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                                      'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                                      'LowPrice': float(i[4]), 'Open': float(i[5])}
                                price_slice.append(pp)
                        price.extend(price_slice)
                    price = pd.DataFrame(price)
                    price = price.drop_duplicates()

                    self.price_record.append(price)
                except GateApiException as ex:
                    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                    price = None
                except ApiException as e:
                    print("Exception when calling SpotApi->list_candlesticks: %s\n" % e)
                    price = None
                return price
            if Type == 'Futures':
                api_client = gate_api.ApiClient(self.configuration)
                # Create an instance of the API class
                api_instance = gate_api.FuturesApi(api_client)  # FuturesApi
                interval = interval
                ls = locals()  #
                try:
                    # Market candlesticks
                    interval_scale_set = {'d': 24 * 60 * 60, 'h': 60 * 60, 'm': 60, 's': 1}
                    interval_time = int(interval[0])
                    interval_scale = interval[1]
                    time_amount = interval_time * interval_scale_set[interval_scale]
                    time_range = to - _from

                    loop_time = int(time_range / (time_amount * 100)) + 1
                    price = []
                    if loop_time <= 100:
                        api_response = api_instance.list_futures_candlesticks(settle=settle, contract=contract,
                                                                              limit=limit, interval=interval,
                                                                              _from=_from, to=to)
                        for i in api_response:
                            pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                                  'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                                  'LowPrice': float(i[4]), 'Open': float(i[5])}
                            price.append(pp)
                    else:
                        time_seq = [_from, ]
                        for k in range(0, loop_time - 1):
                            next_to = time_seq[k] + 100 * time_amount
                            time_seq.append(next_to)
                        time_seq.append(to)
                        price = []
                        for k in range(0, loop_time - 1):
                            api_response = api_instance.list_futures_candlesticks(currency_pair, limit=100, interval=interval,
                                                                          _from=time_seq[k], to=time_seq[k + 1])
                            price_slice = []
                            for i in api_response:
                                pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                                      'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                                      'LowPrice': float(i[4]), 'Open': float(i[5])}
                                price_slice.append(pp)
                        price.extend(price_slice)
                    price = pd.DataFrame(price)
                    price = price.drop_duplicates()
                    self.future_price_record.append(price)
                except GateApiException as ex:
                    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                    price = None
                except ApiException as e:
                    print("Exception when calling FuturesApi->list_candlesticks: %s\n" % e)
                    price = None
                return price
        else:
            api_instance = gate_api.SpotApi(api_client)
            if Type =='Spot':
                try:
                    api_reponse = api_instance.list_candlesticks(currency_pair=currency_pair, limit=limit,
                                                                 interval=interval, _from=_from, to=to)
                    price = []
                    for i in api_reponse:
                        pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                              'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                              'LowPrice': float(i[4]), 'Open': float(i[5])}

                    price.append(pp)
                except GateApiException as ex:
                    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                    price = None
                except ApiException as e:
                    print("Exception when calling SpotApi->list_candlesticks: %s\n" % e)
                    price = None
                price = pd.DataFrame(price)
                return price
            if Type =='Futures':
                # Create an instance of the API class
                api_instance = gate_api.FuturesApi(api_client)  # FuturesApi
                try:
                    api_reponse = api_instance.list_candlesticks(currency_pair=currency_pair, limit=limit,
                                                                 interval=interval, _from=_from, to=to)
                    price = []
                    for i in api_reponse:
                        pp = {'timestamp': int(i[0]), 'TotalAmount': float(i[1]),
                              'ClosePrice': float(i[2]), 'HighPrice': float(i[3]),
                              'LowPrice': float(i[4]), 'Open': float(i[5])}

                    price.append(pp)
                except GateApiException as ex:
                    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                    price = None
                except ApiException as e:
                    print("Exception when calling FuturesApi->list_candlesticks: %s\n" % e)
                    price = None
                price = pd.DataFrame(price)

                return price

    ## futures rate history
    #         api_client = gate_api.ApiClient(self.configuration)
    def futures_rates_history(self,settle:str, contract:str, limit:int):
        api_client = gate_api.ApiClient(self.configuration)
        api_instance = gate_api.FuturesApi(api_client)
        try:
            # Funding rate history
            api_response = api_instance.list_futures_funding_rate_history(settle=settle, contract=contract, limit=limit)
            print(api_response)
            logging.info()
        except GateApiException as ex:
            api_response =None
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling FuturesApi->list_futures_funding_rate_history: %s\n" % e)
            api_response =None
        return api_response

    ##下单函数
    def create_order(self, Type: str, currency_pair: str, amount: str, price: str, side: str,settle='usdt',contract='BTC_USDT',size=1,close=False,auto_size=None,text=None,
                     order_type='limit', auto_borrow=None, iceberg=None, time_in_force='gtc',tif ='gtc'):
        '''

        '''

        # Create an instance of the API class
        api_client = gate_api.ApiClient(self.configuration)
        if Type =='Spot':
            api_instance = gate_api.SpotApi(api_client)
            order = gate_api.Order(text=text, currency_pair=currency_pair, type=order_type, account="spot", side=side,
                                   iceberg=iceberg,
                                   amount=amount, price=price, time_in_force=time_in_force, auto_borrow=auto_borrow)
            try:
                # Create an order
                api_response = api_instance.create_order(order)
                print(api_response)
                self.create_order_record.append(api_response.to_dict())
                logging.info(str(api_response.to_dict()))
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                logging.warning("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling SpotApi->create_order: %s\n" % e)
                logging.warning("Exception when calling SpotApi->create_order: %s\n" % e)
                api_response = None
            return api_response.to_dict()  # 输出下单信息
        if Type =='Futures':
            api_instance = gate_api.FuturesApi(api_client)
            futures_orders = gate_api.FuturesOrder(contract = contract, size =size, close=close, atuo_size=auto_size, price=price, iceberg= iceberg, text=text,
                                                  tif=tif)
            try:
                # Create a futures order
                api_response = api_instance.create_futures_order(settle, futures_orders)
                self.future_orders[api_response.to_dict()]
                logging.info(str(api_response.to_dict()))
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                logging.warning("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response =None
            except ApiException as e:
                print("Exception when calling FuturesApi->create_futures_order: %s\n" % e)
                logging.warning("Exception when calling FuturesApi->create_futures_order: %s\n" % e)
                api_response = None
            return api_response.to_dict()
    # composed order
    def orders(self,Type:str,currency_pair:str,amount :str,price:str,side:str,upper_price:str,down_price:str,settle='usdt',contract='BTC_USDT',size=1,close=False,auto_size=None,text=None,
                     order_type='limit', auto_borrow=None, iceberg=None, time_in_force='gtc',tif ='gtc',waiting_time=10,expiration=60):
        if Type =='Spot':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.SpotApi(api_client)
            order = gate_api.Order(text=text, currency_pair=currency_pair, type=order_type, account="spot", side=side,
                                   iceberg=iceberg,
                                   amount=amount, price=price, time_in_force=time_in_force, auto_borrow=auto_borrow)
            try:
                # Create an order
                api_response = api_instance.create_order(order)
                print(api_response)
                self.create_order_record.append(api_response.to_dict())
                logging.info(str(api_response.to_dict()))
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                logging.warning("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling SpotApi->create_order: %s\n" % e)
                api_response = None
            if api_response != None:
                time.sleep(waiting_time)
                order_id = api_response.id
                order_info = self.get_order(Type = 'Spot',order_id=order_id, currency_pair=currency_pair)
                if order_info.status =='closed':
                    buy_side_op = {'buy': 'sell', 'sell': 'buy'}
                    # stop profit order
                    upper_trigger = {'price': upper_price, 'rule': '>=', 'expiration': expiration}

                    upper_put = {"type": order_type, "side": buy_side_op[side], "price": upper_price, "amount": amount,
                                 "account": "normal",
                                 "time_in_force": time_in_force}
                    upper_order = self.create_trigger_order(Type='Spot', currency_pair=currency_pair,
                                                           trigger=upper_trigger, put=upper_put)
                    # stop_loss
                    down_trigger = {'price': down_price, 'rule': '<=', 'expiration': expiration}

                    down_put = {"type": order_type, "side": buy_side_op[side], "price": down_price, "amount": amount,
                                "account": "normal",
                                "time_in_force": time_in_force}
                    down_order = self.create_trigger_order(Type='Spot', currency_pair=currency_pair,
                                                          trigger=down_trigger, put=down_put)

                else:
                    print('order is not closed, please set trigger order manually')
                    down_order = None
                    upper_order = None
                re = {'order': api_response.to_dict(), 'upper': upper_order, 'down': down_order,'Type':'Spot'}
                self.orders_record.append(re)
                logging.info(str(re))
                return re
        if Type == 'Futures':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.FUturesApi(api_client)

            order = gate_api.FuturesOrde(text=text, currency_pair=currency_pair, type=order_type, account="spot", side=side,
                                   iceberg=iceberg,
                                   amount=amount, price=price, time_in_force=time_in_force, auto_borrow=auto_borrow)
            try:
                # Create an order
                api_response = api_instance.create_futures_order(order)
                print(api_response)
                self.create_order_record.append(api_response.to_dict())
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling FututresApi->create_order: %s\n" % e)
                api_response = None
            if api_response != None:
                time.sleep(waiting_time)
                order_id = api_response.id
                order_info = self.get_order(Type='Futures', order_id=order_id, currency_pair=currency_pair)
                if order_info.status == 'closed':
                    buy_side_op = {'buy': 'sell', 'sell': 'buy'}
                    # stop profit order
                    upper_trigger = {'price': upper_price, 'rule': '>=', 'expiration': expiration}

                    upper_put = {"type": order_type, "side": buy_side_op[side], "price": upper_price, "amount": amount,
                                 "account": "normal",
                                 "time_in_force": time_in_force}
                    upper_order = self.create_trigger_order(Type='Futures', currency_pair=currency_pair,
                                                            trigger=upper_trigger, put=upper_put)
                    # stop_loss
                    down_trigger = {'price': down_price, 'rule': '<=', 'expiration': expiration}

                    down_put = {"type": order_type, "side": buy_side_op[side], "price": down_price, "amount": amount,
                                "account": "normal",
                                "time_in_force": time_in_force}
                    down_order = self.create_trigger_order(Type='Futures', currency_pair=currency_pair,
                                                           trigger=down_trigger, put=down_put)
                else:
                    print('order is not closed, please set trigger order manually')
                    down_order = None
                    upper_order = None
                re = {'order': api_response.to_dict(), 'upper': upper_order, 'down': down_order,'Type':'Futurees'}
                self.orders_record.append(re)
                return re

    # get
    def get_orders(self,record=None,check=True):
        if record != None:
            Type = record['Type']
            currency_pair = record['order']['currency_pair']
            order_id = record['order']['id']
            order_info = self.get_order(Type =Type,currency_pair=currency_pair,order_id=order_id)
            trigger_upper_info = self.get_trigger_order(Type =Type,id=record['upper']['id'],check=check,pair=record['down']['id'])
            trigger_down_info = self.get_trigger_order(Type =Type,id=record['down']['id'],check=check,pair=record['upper']['id'])
            re = {'order_info':order_info,'trigger_upper_info':trigger_upper_info,'trigger_down_info':trigger_down_info}
            self.get_order_record.append(re)
            return re

    def cancel_orders(self, Type:str, currency_pair:str, side:str,settle='usdt',contract='BTC_USDT'):
        api_client = gate_api.ApiClient(self.configuration)

        if Type =='Spot':
            api_instance = gate_api.SpotApi(api_client)
            try:
                # Cancel all `open` orders in specified currency pair
                api_response = api_instance.cancel_orders(currency_pair, side=side, account='spot')
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
            except ApiException as e:
                print("Exception when calling SpotApi->cancel_orders: %s\n" % e)
        if Type == 'Futures':
            api_instance = gate_api.FuturesApi(api_client)
            try:
                # Cancel all `open` orders matched
                api_response = api_instance.cancel_futures_orders(settle=settle, contract=contract, side=side)
                print(api_response)

            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling FuturesApi->cancel_futures_orders: %s\n" % e)
                api_response = None
            return api_response

    ## 查询订单信息
    def get_order(self,Type:str, order_id: str, currency_pair: str, settle='usdt'):
        if Type =='Spot':
            api_client = gate_api.ApiClient(self.configuration)
            # Create an instance of the API class
            api_instance = gate_api.SpotApi(api_client)
            order_id = order_id  # str | Order ID returned, or user custom ID(i.e., `text` field). Operations based on custom ID are accepted only in the first 30 minutes after order creation.After that, only order ID is accepted.
            currency_pair = currency_pair  # str | Currency pair

            try:
                # Get a single order
                api_response = api_instance.get_order(order_id, currency_pair, account='spot')
                print(api_response)
                self.get_order_record.append(api_response.to_dict())  # 订单状态查询记录

            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling SpotApi->get_order: %s\n" % e)
                api_response = None
            return api_response
        if Type == 'Futures':
            api_client = gate_api.ApiClient(self.configuration)
            # Create an instance of the API class
            api_instance = gate_api.FuturesApi(api_client)

            try:
                # Get a single order
                api_response = api_instance.get_futures_order(settle = settle, order_id=order_id)
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response =None
            except ApiException as e:
                print("Exception when calling FuturesApi->get_futures_order: %s\n" % e)
                api_response =None
            return api_response.to_dict()
    ##
    ### 价格触发订单 ##
    def create_trigger_order(self, Type: str, trigger: dict, put: dict, currency_pair: str,initial={},settle='usdt'):
        '''
        :param trigger: price: str,trigger price, rule: str, >= or <= , expiration: int, how long to wait (second)
        :param put: type:str, default limit,, side:str, price:str,OrderPrice,amount:str,type: str  normal for spot trading margin for margin trading ,
        time_in_force: str gtc：GoodTillCancelled  ioc:ImmediateOrCancelled taker only
        :param currency_pair: currency_pair
           trigger = {"price": "6.9", "rule": ">=", "expiration": 60}
            put = {"type": "limit", "side": "buy", "price": "6.9", "amount": "1.00000000", "account": "normal",
                   "time_in_force": "gtc"}

        :param initial: contract:str, size:[optional] int, price : Set to 0 to use market price, close: bool,
                tif : Time in force, if using market price, only 'ioc' is supported ,GoodTillCancelled (gtc),ImmediateOrCancalled(ioc)
        :param trigger: strategy_type:int,price_type: int, price :str, rule :str, expiration: int
        :return:
        '''
        if Type == 'Spot':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.SpotApi(api_client)
            spot_price_triggered_order = gate_api.SpotPriceTriggeredOrder(trigger=trigger, put=put,
                                                                          market=currency_pair)  # SpotPriceTriggeredOrder |
            try:
                # Create a price-triggered order
                api_response = api_instance.create_spot_price_triggered_order(spot_price_triggered_order)
                print(api_response)
                self.create_order_record.append(api_response.to_dict())
                api_response = api_response.to_dict()
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None

            except ApiException as e:
                api_response = None
                print("Exception when calling SpotApi->create_spot_price_triggered_order: %s\n" % e)
            return api_response
        if Type =='Futures':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.SpotApi(api_client)
            futures_price_triggered_order = gate_api.FuturesPriceTriggeredOrder(initial=initial, trigger=trigger)  # FuturesPriceTriggeredOrder |
            try:
                # Create a price-triggered order
                api_response = api_instance.create_price_triggered_order(settle, futures_price_triggered_order)
                print(api_response)
                self.create_futures_trigger_order(api_response.to_dict)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None

            except ApiException as e:
                print("Exception when calling FuturesApi->create_price_triggered_order: %s\n" % e)
                api_response = None

            return api_response.to_dict()
    ## 查询限价订单订单执行情况
    def get_trigger_order(self, Type: str, id: str, check=False,settle='usdt',pair=None):
        '''
        :param id:
        :return:
        '''
        if Type == 'Spot':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.SpotApi(self.api_client)
            order_id = id  # str | Retrieve the data of the order with the specified ID
            try:
                # Get a single order
                api_response = api_instance.get_spot_price_triggered_order(order_id)
                print(api_response)
                self.get_order_record.append(api_response.to_dict())
                if check:
                    status = api_response.status
                    if status == 'closed':
                        self.cancel_trigger_order(Type='Spot', order_id=id, settle=settle, pair_id=pair)
                        api_response =api_response.to_dict()
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling SpotApi->get_spot_price_triggered_order: %s\n" % e)
                api_response = None
            return api_response
        if Type == 'Futures':
            api_client = gate_api.ApiClient(self.configuration)
            # Create an instance of the API class
            api_instance = gate_api.FuturesApi(api_client)
            settle = settle  # str | Settle currency
            order_id = id  # str | Retrieve the data of the order with the specified ID

            try:
                # Get a single order
                api_response = api_instance.get_price_triggered_order(settle, order_id)
                print(api_response)

                if check:
                    status = api_response.status
                    if status =='closed':
                        self.cancel_trigger_order(Type='Futures',order_id=id, settle = settle,pair_id=pair)
                api_response = api_response.to_ditc()

            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response=None
            except ApiException as e:
                print("Exception when calling FuturesApi->get_price_triggered_order: %s\n" % e)
                api_response=None
            return api_response

    ### 撤销订单
    def cancel_trigger_order(self,Type:str,order_id: str,settle=None,pair_id=None):
        api_client = gate_api.ApiClient(self.configuration)
        if Type =='Spot':
            api_instance = gate_api.SpotApi(self.api_client)
            order_id = pair_id  # str | Retrieve the data of the order with the specified ID
            try:
                # Cancel a single order
                api_response = api_instance.cancel_spot_price_triggered_order(order_id)
                self.get_order_record.append(api_response.to_dict())
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None

            except ApiException as e:
                print("Exception when calling SpotApi->cancel_spot_price_triggered_order: %s\n" % e)
                api_response = None
        if Type =='Futures':
            api_instance = gate_api.FuturesApi(api_client)
            settle = settle  # str | Settle currency
            order_id = pair_id  # str | Retrieve the data of the order with the specified ID

            try:
                # Cancel a single order
                api_response = api_instance.cancel_price_triggered_order(settle, order_id)
                self.future_orders.append(api_response)
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
            except ApiException as e:
                print("Exception when calling FuturesApi->cancel_price_triggered_order: %s\n" % e)


        return api_response
        ## list all trades

    ## list all trades
    def list_all_open_orders(self,Type:str,page:int,limit:int):
        if Type =='Spot':
            try:
            # List all open orders
                api_client = gate_api.ApiClient(self.configuration)
                api_instance = gate_api.SpotApi(api_client)
                api_response = api_instance.list_all_open_orders(page=page, limit=limit, account=Type.lower())
                print(api_response)
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
            except ApiException as e:
                print("Exception when calling SpotApi->list_all_open_orders: %s\n" % e)
        if Type =='Futures':
            api_client = gate_api.ApiClient(self.configuration)
            api_instance = gate_api.FtuuresApi(api_client)
            settle = 'usdt'
            status = 'open'
            all_open_orders =[]
            for contract in  self.contracts:
                try:
                    api_response = api_instance.list_futures_orders(settle,contract,status)
                    all_open_orders.append(api_response)

                except GateApiException as ex:
                    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                    logging.warning("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                except ApiException as e:
                    print("Exception when calling SpotApi->list_all_open_orders: %s\n" % e)
                    logging.warning("Exception when calling SpotApi->list_all_open_orders: %s\n" % e)
            logging.info(str(all_open_orders))
            return all_open_orders


    def list_trades(self, Type: str, currency_pair: str, page: int, limit: int, trigger_status: str, account: str,
                    offset: int, last_id=None, reverse=True, _from=None, to=None):
        '''
        :param type:
        :param page:
        :param currency_pair: # currency_pair = 'BTC_USDT'  # str | Currency pair
        :param limit: # int | Maximum number of records to be returned in a single list (optional) (default to 100)
        :param last_id: # str | Specify list staring point using the `id` of last record in previous list-query results (optional)
        :param reverse:  # bool | Whether the id of records to be retrieved should be smaller than the last_id specified- true: Retrieve records where id is smaller than the specified last_id- false: Retrieve records where id is larger than the specified last_idDefault to false.  When `last_id` is specified. Set `reverse` to `true` to trace back trading history; `false` to retrieve latest tradings.  No effect if `last_id` is not specified. (optional) (default to False)
        :param _from: # int | Start timestamp of the query (optional)
        :param to: # int | Time range ending, default to current time (optional)
        :return:
        '''
        if Type == 'Spot':
            api_client = gate_api.ApiClient(self.configuration)

            api_instance = gate_api.SpotApi(api_client)
            try:
                # Retrieve market trades
                api_response = api_instance.list_trades(currency_pair, limit=limit, last_id=last_id, reverse=reverse,
                                                        _from=_from, to=to, page=page)
                print(api_response)
                self.list_order.append(api_response.to_dict())
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response = None
            except ApiException as e:
                print("Exception when calling SpotApi->list_trades: %s\n" % e)
                api_response = None

            status = trigger_status  # str | Only list the orders with this status
            market = currency_pair  # str | Currency pair (optional)
            account = account  # str | Trading account (optional)
            limit = 100  # int | Maximum number of records to be returned in a single list (optional) (default to 100)
            offset = 0  # int | List offset, starting from 0 (optional) (default to 0)

            try:
                # Retrieve running auto order list
                api_response_trigger = api_instance.list_spot_price_triggered_orders(status, market=market,
                                                                                     account=account,
                                                                                     limit=limit, offset=offset)
                print(api_response_trigger)
                self.list_trigger_order.append(api_response_trigger.to_dict())
            except GateApiException as ex:
                print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
                api_response_trigger = None
            except ApiException as e:
                print("Exception when calling SpotApi->list_spot_price_triggered_orders: %s\n" % e)
                api_response_trigger
            return [api_response, api_response_trigger]
    def list_positon(self,settle):
        api_client = gate_api.ApiClient(self.configuration)
        api_instance = gate_api.FuturesApi(api_client)
        settle = 'usdt'  # str | Settle currency

        try:
            # List all positions of a user
            api_response = api_instance.list_positions(settle)
            logging.info(str(api_response))
            print(api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
        except ApiException as e:
            print("Exception when calling FuturesApi->list_positions: %s\n" % e)

    def get_account(self,currency =None):
        # Create an instance of the API class

        api_instance = gate_api.SpotApi(self.api_client)
        currency = currency # str | Retrieve data of the specified currency (optional)

        try:
            # List spot accounts
            api_response = api_instance.list_spot_accounts(currency=currency)
            timestamp = datetime.datetime.now().timestamp() #记录当前时间
            re = [i.to_dict() for i in api_response]
            re.append
            re.append(timestamp)
            # self.account.append(re)
            print(api_response)
        except GateApiException as ex:
            print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
            re=None
        except ApiException as e:
            print("Exception when calling SpotApi->list_spot_accounts: %s\n" % e)
            re = None
        return re
    def Close_position(self,price:dict,currency =None,Type = 'Spot'):
        if Type =='Spot':
            position_amount = self.get_account(currency = currency)
            for item in position_amount[0:-1]:
                currency_pair= item.get('currency') +"_USDT"
                amount = item.get('available')
                amount = float(amount)
                price = float(price.get('currency'))
                order = self.create_order(Type = 'Spot',currency_pair=currency_pair,price = price,side = 'sell')
                logging.info('Close {cur} postion, amount: {amount},price:{price}'.format(cur=currency,amount =amount, pirce =price))



    def close_time(self,timestamp,interval):
        '''

        :param timestamp:
        :param interval:
        :return:
        '''
        interval_scale_set = {'d':24*60*60,'h':60*60,'m':60,'s':1}
        interval_time = int(interval[0])
        interval_scale = interval[1]
        time_amount = interval_time*interval_scale_set[interval_scale]
        close_time = int(timestamp/time_amount)*time_amount
        next_time =(int(timestamp/time_amount)+1)*time_amount
        return close_time,next_time

    def account_value(self,interval:str,account_info=None):
        #  获取当前账户持有币种信息和
        if account_info == None:

            value_dist = None

        else:
            account_info = self.get_account()
            timestamp= account_info[-1]
            account_info.pop(-1)
            timestamp =int(timestamp)
            Close_time, next_time = self.close_time(timestamp =timestamp,interval =interval)
            value_dist = {}
            value_dist['timestamp'] = Close_time
            for i in account_info:
                if (i['currency'] !='USDT') and (i['currency']!= 'POINT'):
                    currency_pair = i['currency'] +"_USDT"
                    amount = float(i['available']) + float(i['locked'])
                    Candelsticks = self.candelsticks(Type='Spot', currency_pair=currency_pair,_from=Close_time,to=next_time,interval=interval)
                    value_dist[currency_pair] = amount*Candelsticks['ClosePrice']
            usdt = np.array(account_info)[[i['currency'] == 'USDT' for i in account_info]]
            value_dist['USDT'] = usdt[0]['available']
            self.account.append([value_dist])
        return value_dist


        ###





    def save(self, path=os.getcwd()):
        if self.create_order_record != []:
            create_order_record_pd = pd.DataFrame(self.create_order_record,
                                                  columns=self.create_order_record[0].keys())  # 下单信息记录
            create_order_record_pd.to_csv('{path}/create_order_record.csv'.format(path=path))
        if self.get_order_record != []:
            get_order_record_pd = pd.DataFrame(self.get_order_record, columns=self.get_order_record[0].keys())  # 下单信息记录
            get_order_record_pd.to_csv('{path}/get_order_record.csv'.format(path=path))
        if self.holing_record != []:
            holing_record_pd = pd.DataFrame(self.holing_record, columns=self.holing_record[0].keys())  # 下单信息记录
            holing_record_pd.to_csv('{path}/holing_record.csv'.format(path=path))
        if self.list_order != []:
            list_order_pd = pd.DataFrame(self.list_order, columns=self.list_order[0].keys())  # 下单信息记录
            list_order_pd.to_csv('{path}/list_order.csv'.format(path=path))
        if self.list_trigger_order != []:
            list_trigger_order = pd.DataFrame(self.list_trigger_order,
                                              columns=self.list_trigger_order[0].keys())  # 下单信息记录
            list_trigger_order.to_csv('{path}/list_trigger_order.csv'.format(path=path))
        if self.price_record != []:
            price_record = pd.DataFrame(self.price_record, columns=self.price_record[0].keys())  # 下单信息记录
            price_record.to_csv('{path}/price_record.csv'.format(path=path))

        if self.account != []:
            for i in self.account:
                for j in i[0].keys():
                    with open('{path}/account_record.csv'.format(path=path), 'a+') as f:
                        f.write('{}:{}\n'.format(j, i[0][j]))

        if self.orders_record != []:
            for i in self.orders_record:
                for j in i[0].keys():
                    with open('{path}/orders_record.csv'.format(path=path), 'a+') as f:
                        f.write('{}:{}\n'.format(j, i[0][j]))






