import requests

from urllib.parse import parse_qs, urlparse, urlencode

url = 'https://trade-acs.m.taobao.com/gw/mtop.taobao.detail.getdetail/6.0/?data=%7B%22detail_v%22%3A%223.1.1%22%2C%22itemNumId%22%3A%22@%22%7D'
query = urlparse(url).query
params = parse_qs(query)
# print(params)
data = {'"detail_v"': '"3.3.2"',
        '"exParams"': '"{\"NAV_START_ACTIVITY_TIME\":\"1574314027817\",\"NAV_TO_URL_START_TIME\":\"1574314027778\",\"ad_type\":\"1.0\",\"appReqFrom\":\"detail\",\"clientCachedTemplateKeys\":\"[]\",\"container_type\":\"xdetail\",\"countryCode\":\"CN\",\"cpuCore\":\"8\",\"cpuMaxHz\":\"1805000\",\"detail_url\":\"http://item.taobao.com/item.htm?id=558587300390&from=shopsearch&track_params={\\\"bucket_id\\\":\\\"3\\\",\\\"from\\\":\\\"shopsearch\\\",\\\"inshops\\\":\\\"allauc\\\",\\\"rn\\\":\\\"3fb8f839983c52e42c21b14617ac6a5f\\\",\\\"sort_tag\\\":\\\"_sale\\\"}&spm=a2141.7631671.0.0\",\"dinamic_v3\":\"true\",\"from\":\"shopsearch\",\"id\":\"558587300390\",\"item_id\":\"558587300390\",\"latitude\":\"0\",\"longitude\":\"0\",\"osVersion\":\"24\",\"phoneType\":\"HUAWEI+NXT-DL00\",\"soVersion\":\"2.0\",\"spm\":\"a2141.7631671.0.0\",\"spm-cnt\":\"a2141.7631564\",\"track_params\":\"{\\\"bucket_id\\\":\\\"3\\\",\\\"from\\\":\\\"shopsearch\\\",\\\"inshops\\\":\\\"allauc\\\",\\\"rn\\\":\\\"3fb8f839983c52e42c21b14617ac6a5f\\\",\\\"sort_tag\\\":\\\"_sale\\\"}\",\"ultron2\":\"true\",\"utdid\":\"XdUIhe06REsDAHKx+yC8TSDo\"}"',
        '"itemNumId"': '"558587300390"'}
a = urlencode(data)
# print(a)
url = "http://106.11.162.148/gw/mtop.taobao.detail.getdetail/6.0/"
b = {"data":{'"detail_v"': '"3.3.2"',
        '"exParams"': '"{\"NAV_START_ACTIVITY_TIME\":\"1574314027817\",\"NAV_TO_URL_START_TIME\":\"1574314027778\",\"ad_type\":\"1.0\",\"appReqFrom\":\"detail\",\"clientCachedTemplateKeys\":\"[]\",\"container_type\":\"xdetail\",\"countryCode\":\"CN\",\"cpuCore\":\"8\",\"cpuMaxHz\":\"1805000\",\"detail_url\":\"http://item.taobao.com/item.htm?id=558587300390&from=shopsearch&track_params={\\\"bucket_id\\\":\\\"3\\\",\\\"from\\\":\\\"shopsearch\\\",\\\"inshops\\\":\\\"allauc\\\",\\\"rn\\\":\\\"3fb8f839983c52e42c21b14617ac6a5f\\\",\\\"sort_tag\\\":\\\"_sale\\\"}&spm=a2141.7631671.0.0\",\"dinamic_v3\":\"true\",\"from\":\"shopsearch\",\"id\":\"558587300390\",\"item_id\":\"558587300390\",\"latitude\":\"0\",\"longitude\":\"0\",\"osVersion\":\"24\",\"phoneType\":\"HUAWEI+NXT-DL00\",\"soVersion\":\"2.0\",\"spm\":\"a2141.7631671.0.0\",\"spm-cnt\":\"a2141.7631564\",\"track_params\":\"{\\\"bucket_id\\\":\\\"3\\\",\\\"from\\\":\\\"shopsearch\\\",\\\"inshops\\\":\\\"allauc\\\",\\\"rn\\\":\\\"3fb8f839983c52e42c21b14617ac6a5f\\\",\\\"sort_tag\\\":\\\"_sale\\\"}\",\"ultron2\":\"true\",\"utdid\":\"XdUIhe06REsDAHKx+yC8TSDo\"}"',
        '"itemNumId"': '"558587300390"'}}
req = requests.get(url=url,params=b)
print(req.status_code)
