# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import json
from gm_work.items import softtime

class SorftimeSpider(RedisSpider):
    name = 'softtime_detail'
    start_urls = ['']
    redis_key = "softtime_detail:start_url"

    def start_requests(self):
        yield scrapy.Request("https://www.baidu.com")

    def parse(self, response):
        with open(r"D:\spider_data\softtime_sort-data\20200507-105039softtime_sort154_合并.txt[F3].txt","r",encoding="utf-8") as f:
            for i in f:
                NodeId = i.strip()
                url = "https://api.sorftime.com/FlowCircle/Index"
                headers = self.get_headers(1)
                Hm_lvt = "1586504587"
                Hm_lvt2 = "1586511127"
                auth = "eyJjcHVJZCI6Ik9EazVPRGxCTURBdE1EaEdOUzB4TVVVNUxUazVPVEV0TmpRMFFVTkdSamt6UkRBdyIsIm1hY2hpbmVDb2RlIjoiTkdORmVHTk5NVXRWV0RndlZUQldNRXBPY0VaS05VNTNNWFpIZVdsbVRVTlhWM1ZLS3paVk5teHBRbE5XV1ZsRUt6RmlaMkpyVDBOaVoxUk9Sa2x6VVE9PSIsImNoZWNrQ29kZSI6Ik1qQXlNREEwTVRBeE5UUXlOVFl6T1RNPSIsInNlcmlhbE5vIjoiT1VVNU1qRTVRMFJDT1RFd1FqWkVOUT09IiwidWNvZGUiOiI4OTFiNDgzYzI4Yjg0N2FkYmVmYmI5OTFlZTY4YWRiZSJ9"
                headers["Referer"] = "https://api.sorftime.com/flowCircle/Index?nodeId={}&name=&auth={}&lang=zh-CN&auth={}".format(NodeId,auth,auth)
                headers["Cookie"] = "LanguageCulture=zh-CN; Hm_lvt_37085cda84608d899833965da1208c82={}; Hm_lpvt_37085cda84608d899833965da1208c82={}".format(Hm_lvt,Hm_lvt2)
                prama = "nodeIdStr={}&keywordsId=0&auth={}&lang=zh-CN&field=SaleCount&order=desc".format(NodeId,auth)
                yield scrapy.FormRequest(url, method="POST", headers=headers, body=prama, callback=self.get_detail,dont_filter=True,meta={"nodeid":NodeId})

    def get_detail(self,response):
        key = response.meta.get("nodeid")
        try:
            detail_data = json.loads(response.text)
            totalsalecount = str(detail_data.get("TotalSaleCount"))
            Data = detail_data.get("Data")
            for i in Data:
                Id = i.get("Id")
                ASIN = i.get("ASIN")
                Name = i.get("Name")
                NodeId = i.get("NodeId")
                NameEncode = i.get("NameEncode")
                Brand = i.get("Brand")
                BrandEncode = i.get("BrandEncode")
                ImageEncode = i.get("ImageEncode")
                Url = i.get("Url")
                Store = i.get("Store")
                Rank = i.get("Rank")
                Solder = i.get("Solder")
                CommentCount = i.get("CommentCount")
                SaleTime = i.get("SaleTime")
                Score = i.get("Score")
                Variants = i.get("Variants")
                OtherSellerCount = i.get("OtherSellerCount")
                EBC = i.get("EBC")
                CurrentSalePrice = i.get("CurrentSalePrice")
                SalePrice = i.get("SalePrice")
                SaleCount = i.get("SaleCount")
                PromotionRecords = i.get("PromotionRecords")
                PotentialEvaluation = i.get("PotentialEvaluation")
                Income = i.get("Income")
                FBAFee = i.get("FBAFee")
                BestSeller = i.get("BestSeller")
                ListingHeight = i.get("ListingHeight")
                ListingWidth = i.get("ListingWidth")
                ListingDepath = i.get("ListingDepath")
                SizeStr = i.get("SizeStr")
                ShippingWeight = i.get("ShippingWeight")
                PickAndPack = i.get("PickAndPack")
                Referral = i.get("Referral")
                Storage = i.get("Storage")
                Deliver = i.get("Deliver")
                ReferralRate = i.get("ReferralRate")
                TypeName = i.get("TypeName")
                Image = i.get("Image")
                BrandSalePercent = i.get("BrandSalePercent")
                TotalSalePercent = i.get("TotalSalePercent")
                BDCount = i.get("BDCount")
                Coupon = i.get("Coupon")
                CouponRecord = i.get("CouponRecord")
                ActualSalePrice = i.get("ActualSalePrice")
                Volume = i.get("Volume")
                Productsize = i.get("Productsize")

                item = softtime()
                item["totalsalecount"] =str(totalsalecount)
                item["Id"] =str(Id)
                item["ASIN"] =str(ASIN)
                item["Name"] =str(Name)
                item["NodeId"] =str(NodeId)
                item["NameEncode"] =str(NameEncode)
                item["Brand"] =str(Brand)
                item["BrandEncode"] =str(BrandEncode)
                item["ImageEncode"] =str(ImageEncode)
                item["Url"] =str(Url)
                item["Store"] =str(Store)
                item["Rank"] =str(Rank)
                item["Solder"] =str(Solder)
                item["CommentCount"] =str(CommentCount)
                item["SaleTime"] =str(SaleTime)
                item["Score"] =str(Score)
                item["Variants"] =str(Variants)
                item["OtherSellerCount"] =str(OtherSellerCount)
                item["EBC"] =str(EBC)
                item["CurrentSalePrice"] =str(CurrentSalePrice)
                item["SalePrice"] =str(SalePrice)
                item["SaleCount"] =str(SaleCount)
                item["PromotionRecords"] =str(PromotionRecords)
                item["PotentialEvaluation"] =str(PotentialEvaluation)
                item["Income"] =str(Income)
                item["FBAFee"] =str(FBAFee)
                item["BestSeller"] =str(BestSeller)
                item["ListingHeight"] =str(ListingHeight)
                item["ListingWidth"] =str(ListingWidth)
                item["ListingDepath"] =str(ListingDepath)
                item["SizeStr"] =str(SizeStr)
                item["ShippingWeight"] =str(ShippingWeight)
                item["PickAndPack"] =str(PickAndPack)
                item["Referral"] =str(Referral)
                item["Storage"] =str(Storage)
                item["Deliver"] =str(Deliver)
                item["ReferralRate"] =str(ReferralRate)
                item["TypeName"] =str(TypeName)
                item["Image"] =str(Image)
                item["BrandSalePercent"] =str(BrandSalePercent)
                item["TotalSalePercent"] =str(TotalSalePercent)
                item["BDCount"] =str(BDCount)
                item["Coupon"] =str(Coupon)
                item["CouponRecord"] =str(CouponRecord)
                item["ActualSalePrice"] =str(ActualSalePrice)
                item["Volume"] =str(Volume)
                item["Productsize"] =str(Productsize)

                yield item
            item_s = softtime()
            item_s["key"] = key
            item_s["source_code"] = response.text
            yield item_s
        except Exception as e:
            self.try_again(response,key=key)
            print(e)

    def get_headers(self,num):
        if num == 1:
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection":"keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "api.sorftime.com",
                "Origin": "https://api.sorftime.com",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
            }
            '''Host: api.sorftime.com
Connection: keep-alive
Content-Length: 455
Accept: application/json, text/javascript, */*; q=0.01
Origin: https://api.sorftime.com
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Referer: https://api.sorftime.com/flowCircle/Index?nodeId=15718271&name=&auth=eyJjcHVJZCI6Ik9EazVPRGxCTURBdE1EaEdOUzB4TVVVNUxUazVPVEV0TmpRMFFVTkdSamt6UkRBdyIsIm1hY2hpbmVDb2RlIjoiTkdORmVHTk5NVXRWV0RndlZUQldNRXBPY0VaS05VNTNNWFpIZVdsbVRVTlhWM1ZLS3paVk5teHBRbE5XV1ZsRUt6RmlaMkpyVDBOaVoxUk9Sa2x6VVE9PSIsImNoZWNrQ29kZSI6Ik1qQXlNREEwTVRBeE5UUXlOVFl6T1RNPSIsInNlcmlhbE5vIjoiT1VVNU1qRTVRMFJDT1RFd1FqWkVOUT09IiwidWNvZGUiOiI4OTFiNDgzYzI4Yjg0N2FkYmVmYmI5OTFlZTY4YWRiZSJ9&lang=zh-CN&auth=eyJjcHVJZCI6Ik9EazVPRGxCTURBdE1EaEdOUzB4TVVVNUxUazVPVEV0TmpRMFFVTkdSamt6UkRBdyIsIm1hY2hpbmVDb2RlIjoiTkdORmVHTk5NVXRWV0RndlZUQldNRXBPY0VaS05VNTNNWFpIZVdsbVRVTlhWM1ZLS3paVk5teHBRbE5XV1ZsRUt6RmlaMkpyVDBOaVoxUk9Sa2x6VVE9PSIsImNoZWNrQ29kZSI6Ik1qQXlNREEwTVRBeE5UUXlOVFl6T1RNPSIsInNlcmlhbE5vIjoiT1VVNU1qRTVRMFJDT1RFd1FqWkVOUT09IiwidWNvZGUiOiI4OTFiNDgzYzI4Yjg0N2FkYmVmYmI5OTFlZTY4YWRiZSJ9
Cookie: LanguageCulture=zh-CN; Hm_lvt_37085cda84608d899833965da1208c82=1586504587; Hm_lpvt_37085cda84608d899833965da1208c82=1586511127
'''
            return headers

    def try_again(self,rsp,**kwargs):
        max_num = 5
        meta = rsp.meta
        try_num = meta.get("try_num",0)
        if try_num < max_num:
            try_num += 1
            request = rsp.request
            request.dont_filter = True
            request.meta["try_num"] = try_num
            return request
        else:
            item_e = softtime()
            item_e["error_id"] = 1
            for i in kwargs:
                item_e[i] = kwargs[i]
            return item_e
