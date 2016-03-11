#coding=utf-8
#!/usr/bin/python

import re
import json

'''
    收银机预设置：
    内容包括条形码、名称、单价、单位、是否‘买二赠一’，是否95折；
    数据设置形式：{条形码:[名称，单价，单位，是否参加‘买二赠一’活动，是否95折]}；
    其中，是否‘买二赠一’和是否95折两个数据，以‘1’代表是，‘0’代表否；
'''
cargoInStore = {
                'ITEM000001':['可口可乐',3.00,'瓶', 1, 1],\
                'ITEM000002':['羽毛球',1.00,'个',0, 1],\
                'ITEM000003':['苹果',5.50,'斤',0,0],\
                'ITEM000004':['苹果5s',5.50,'台',1,0],\
                'ITEM000005':['苹果6',5.50,'台',1,0],\
               }

class CARGOINFO:
    def __init__(self):
        self.toBuy = []    #顾客所购全部商品条形码
        self.tickCotent = '***<没钱赚商店>购物清单***'   #小票内容初始化

    #def cus_Wants(self):
    def __call__(self):
        basket = []
        for line in iter(raw_input, ''):
            pattern = re.search("\s*\'(ITEM\d+(-\d+)?)\',",line)
            if pattern:
                itemInfo = pattern.group(1)
                basket.append(itemInfo)
        self.toBuy = json.dumps(self.Lst2Patt(basket))
        #return self.toBuy
        return self

    def Lst2Patt(self, origLst):
        '''
            支持该程序适应多种输入格式：
            1.多次输入同一商品的条形码，如买了3个羽毛球：'ITEM000002','ITEM000002','ITEM000002'；
            2.输入某一商品的条形码和数量，如顾客购买了3个羽毛球，'ITEM000002-3'
        '''
        destLst = []
        if isinstance(origLst, list):
            myLst = set(origLst)
            for i in myLst:
                if '-' not in i:
                    destLst.append(i+'-'+str(origLst.count(i)))
                else:
                    destLst.append(i)
        return destLst

    def geteticket(self): #获得小票内容
        totalToPay = 0
        willSave = 0
        onsaleInfo = []

        for thing in json.loads(self.toBuy):
            eachCargo_Obj = eachCargo(thing).getEachCargoInfo()
            self.tickCotent += '\n'+eachCargo_Obj.getTicketInfo()
            if eachCargo_Obj.onsale:
                onsaleInfo.append([eachCargo_Obj.cargoName, eachCargo_Obj.onsaleNum, eachCargo_Obj.quantity])
            totalToPay += eachCargo_Obj.eachCargoTotal
            willSave += (eachCargo_Obj.thingToSave_offcount + eachCargo_Obj.thingToSave_onsale)
        self.tickCotent += '\n----------------------'

        if len(onsaleInfo) != 0 and eachCargo_Obj.onsaleNum != 0:
            self.tickCotent += '\n买二赠一商品：'
            for i in xrange(len(onsaleInfo)):
                self.tickCotent += '\n名称：%s，数量：%s%s' % tuple(onsaleInfo[i][0:])
            self.tickCotent += '\n----------------------'

        self.tickCotent += '\n总计：%.2f' % totalToPay
        if willSave != 0:
            self.tickCotent += '\n节省：%.2f(元)' % willSave

        return self.tickCotent + '\n**********************'

class eachCargo(object):

    def __init__(self, erweima_n):
        self.erweima_n = erweima_n    #输入文本格式，如：'ITEM000001-2',
        self.cargoName = ''           #顾客所购买的该商品的名称
        self.eachCargoNum = 1         #顾客所购买的该商品的数量
        self.eachCargoPrice = 0       #顾客所购买的该商品的单价
        self.quantity = ''            #顾客所购买的该商品的单位，如‘个’，‘斤’
        self.eachCargoTotal = 0       #顾客所购买的该商品优惠后的小计金额
        self.onsale = 0               #该商品是否参加‘买二赠一’，0：不参加，1：参加
        self.offcount = 0             #该商品是否参加‘95折’，0：不参加，1：参加
        self.onChargeCargoNum = 0     #该商品参加完买二赠一活动后，顾客实际应支付的数量
        self.thingToSave_offcount = 0 #对应该商品95折的优惠金额
        self.thingToSave_onsale = 0   #对应该商品买二赠一的优惠金额
        self.onsaleNum = 0            #买二赠一活动中赠送的该商品数量

    def getEachCargoInfo(self):
        '''
            根据输入条码信息，解析对应该商品的基本信息
            {条码:[商品名，单价，单位，买二赠一，95折]}
        '''
        if '-' in self.erweima_n:
            erweima = self.erweima_n.split('-')[0]
            self.eachCargoNum = int(self.erweima_n.split('-')[1])
        else:
            erweima = self.erweima_n
        self.cargoName, self.eachCargoPrice, self.quantity, self.onsale, self.offcount = cargoInStore[erweima][0:]
        return self

    def getTicketInfo(self):  #功能：统计该商品对应的小票信息

        if 1 == self.onsale:  # 当前商品符合“买二赠一”活动，那么计算价格时按照减去促销后的金额表示
            self.onsaleNum = self.eachCargoNum / 2
            self.onChargeCargoNum = self.eachCargoNum - self.onsaleNum
        else:
            self.onChargeCargoNum = self.eachCargoNum
        self.thingToSave_onsale = self.onsaleNum * self.eachCargoPrice
        self.eachCargoTotal = self.eachCargoPrice * self.onChargeCargoNum

        #单行内容格式：“名称：可口可乐，数量：3瓶，单价：3.00(元)，小计：6.00(元)”
        eachThingContent = '名称：%s，数量：%s%s，单价：%.2f(元)' % \
               (self.cargoName, self.eachCargoNum, self.quantity, self.eachCargoPrice, )

        if 1 == self.offcount and 1 != self.onsale:  #当前商品符合“95折促销”活动时，要注明节省的金额
            self.thingToSave_offcount = self.eachCargoTotal*0.05
            self.eachCargoTotal -= self.thingToSave_offcount
            eachThingContent +='，小计：%.2f(元), 节省：%.2f(元)' % (self.eachCargoTotal,self.thingToSave_offcount)

            return eachThingContent
        return eachThingContent + '，小计：%.2f(元)' % self.eachCargoTotal

if __name__ == "__main__":
    a = CARGOINFO()()
    print a.geteticket()