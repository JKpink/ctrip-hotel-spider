import getHotelComments as GHC
import getHotelList as GHL


"""
curl ^"https://m.ctrip.com/restapi/soa2/34951/fetchHotelList^" ^
  -X ^"OPTIONS^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7^" ^
  -H ^"access-control-request-headers: content-type,cookieorigin,phantom-token,x-ctx-country,x-ctx-currency,x-ctx-locale,x-ctx-ubt-pageid,x-ctx-ubt-pvid,x-ctx-ubt-sid,x-ctx-ubt-vid,x-ctx-wclient-req^" ^
  -H ^"access-control-request-method: POST^" ^
  -H ^"origin: https://hotels.ctrip.com^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://hotels.ctrip.com/^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36^"
  
  curl ^"https://m.ctrip.com/restapi/soa2/34951/fetchHotelList^" ^
  -H ^"accept: application/json^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7^" ^
  -H ^"content-type: application/json^" ^
  -b ^"GUID=09031138317062936616; UBT_VID=1767516589173.22e8NgSJdDEM; _RGUID=320b22b7-8647-4378-ba22-f3cdb07984dd; StartCity_Pkg=PkgStartCity=428; MKT_CKID=1767516599308.hgkwl.ubk0; _ga=GA1.1.1622264172.1767516670; nfes_isSupportWebP=1; ibulocale=zh_cn; cookiePricesDisplayed=CNY; IBU_showtotalamt=2; _bfaStatusPVSend=1; _bfi=p1^%^3D600001375^%^26p2^%^3D600001375^%^26v1^%^3D13^%^26v2^%^3D12; ibu_h5_site=CN; ibu_h5_group=ctrip; ibu_h5_local=zh-cn; ibu_h5_local=zh-cn; ibu_h5_lang=zhcn; ibu_h5_curr=CNY; ibu_country=CN; nfes_isSupportWebP=1; _pd=^%^7B^%^22_o^%^22^%^3A80^%^2C^%^22s^%^22^%^3A592^%^2C^%^22_s^%^22^%^3A1^%^7D; _ga_9BZF483VNQ=GS2.1.s1767604533^$o2^$g0^$t1767604533^$j60^$l0^$h0; _ga_5DVRDQD429=GS2.1.s1767604533^$o2^$g0^$t1767604533^$j60^$l0^$h1104736324; _ga_B77BES1Z8Z=GS2.1.s1767604533^$o2^$g0^$t1767604533^$j60^$l0^$h0; MKT_Pagesource=PC; manualclose=1; _bfaStatus=send; cticket=36174BB26B0769D3D059BBD1E22295B87491A98A8211049D8A074C5A825ADF5D; login_type=0; login_uid=BB0F93C895883B39349A31879F6963B3810F50D9AFB0416BDD56891663AB5740; DUID=u=9C85EA62879DA3E20B795F47541D1DBD^&v=0; IsNonUser=F; AHeadUserInfo=VipGrade=0^&VipGradeName=^%^C6^%^D5^%^CD^%^A8^%^BB^%^E1^%^D4^%^B1^&UserName=^&NoReadMessageCount=0; _udl=708D70C2B179E2F91CC5ED1C2CCE362D; Session=smartlinkcode=U1535^&smartlinklanguage=zh^&SmartLinkKeyWord=^&SmartLinkQuary=^&SmartLinkHost=; Union=AllianceID=1315^&SID=1535^&OUID=^&createtime=1767605644^&Expires=1768210443623; _abtest_userid=f77134e0-e9ce-4e65-8e0a-2cf18f09e738; _ubtstatus=^%^7B^%^22vid^%^22^%^3A^%^221767516589173.22e8NgSJdDEM^%^22^%^2C^%^22sid^%^22^%^3A4^%^2C^%^22pvid^%^22^%^3A5^%^2C^%^22pid^%^22^%^3A600001375^%^7D; ibulanguage=ZH-CN; _jzqco=^%^7C^%^7C^%^7C^%^7C^%^7C1.1219664144.1767516599310.1767612247397.1767612966671.1767612247397.1767612966671.0.0.0.39.39; _bfa=1.1767516589173.22e8NgSJdDEM.1.1767612247928.1767612966244.4.9.10650171192^" ^
  -H ^"cookieorigin: https://hotels.ctrip.com^" ^
  -H ^"origin: https://hotels.ctrip.com^" ^
  -H ^"phantom-token: 1004-common-90BYmhYhUKd9J4kxn0jcnJD4yGHjsMyO4JS3W5Oi9TwsNRQPybZjGZEOtR6ovAQvbzwp6jAsJH0wnAjs8j8dedGEsDvdFiZ1iUDEdtEQ3YkZw9gvBzE7YtheQ9E6ojmARLpy3qw8XyqOwQoRb5YlFv80jpoiFDwmXY0ajnBj8QKsFjQYldyz3WGXic5KZdjG1j7lEPnyAE4niApYqEd3YcaySE1hYtGyP9KOdibAjLZjc3W80y5cI1XwcLjOZw9GezfEcMImZwUTiS9RLEf7YSBy1NKqgiPojFdjLcWnSyGEszYhgy08WF9eSHyZdjNEfUigoytqvONWQBjlzeU1wU6ItgEhQjUET6isSJtdRZE16YbqwaOv1teUPeltj7XylOJbmE1Nj9Zj6E0Mi7PJShWbEkoY65wmNwTLel0jUHI5txS7yBEUmiTmJBLYhE6XYDawSkwDMeHNjZMImXWADEpfRDHjpEg9iPfJgEsaYL4JtPwA8EZEMHYLHJpkilSj3EOaYgfJk4j3GYoEQkYfFJl7wzZwmEZdY4NJ3niH9JmEXQYALJ8SiSmybEpgY8zw3Uy0AjDzySDjhgWcdE6aRLcjHEf6i8pJMEHFYTzJ41wokElEpaYqNJOni7qj3EbdYnoJh8jQgY8EGfYOHJQgwhTwnEzOY8sJb0ikbJhEozYX4JqLi4PyfEtUYAUwlfyLnjctEn8w14wb5Kf8wdpI81EhLj7EfbiQnJfEaLYdHwQLwAoK91j7bwslrnkezhYmE9OiFdJB4YpHWhQYM9wTse1FWzTRXce58WnUJaEUQYctwsDw5QKZzjBTwUPrbTizLvfNj8E1PiQlJ7HYHkWBOYH8w40e8NWBTRT9ef9WP9wAEDkY1OwpQwblwo5YcEzTiNnJFLRfEo9YgmwdBWPneTky5ljAZytfec0W5kjhMjTbwf4yZEkXi7PJt9Y1Zv14ioHRNvl7YHbEF1Kfmr3YDhyMNES3eotRZ6yPFwmtykdJZPRlLw0lJNsjasvktRm0yaBiOzIXAYLFYaMj0SjThWBPxasJ9cKcnym1JXqw3qrDkJzOI7nE6YsJO9ilMwQljSzwtcRstipGRfDy9BwQ9ybteXnE9MYqpv8HEtAezDEpTE0oJTcEzdeHbvLhE31y53jtne8hyqhvmowoHvXsjtDwd6JL7E86iP7i8LiZHYl9yMkxOHJTYhFv45E9UeZ4wHbySMY64wAcjcMwtnYm8w4zJHqJH7y3YgOWLFx8y6pYAfEp0KDTEOEHYOGRqLRkHWflvkhen6YSDi5LYHw4crp1vhYdai9HEQPY09eQTEhlj3MWhmEq5Rf7vLYDzi8Ehy4XrTcKksestEcTWmBeUlrazI5YXvscRsAJN0Rhzy1ZWd5y0hetBRpMWbDwd8yo8xa3JcAKMYL3E4Qyq5ITDRlOy4NW6GycUesnRPBW8FR6DvnkK0FKhBE8YNTwP3xATj4cEq4iN7RobYbGRQlE6YzlWsdxpDRgkY7Fi3PwabRUSE7BWBAWb7xHpWMYaSKaAJmGiSzJZBxgpyUdx0YA4vDfY4tK5oj3Hw9zvcljUFYzMY3OY6Y8hv0vkOK1ZYLoE3ZrUHyqYlXylsYzXY8FjNGw45vmdjcSipbJa7e0YohvQ8vaAvsURLgW6bWfNw4se9txoYamekaRDvMPjzBiLkid1xkGW98jLrX3xpPYdGwNfIpr8yGBWQpjQOxMsJH5xsLYXj4dKNMxPneLY7vMkRBlrZ5RqZW39wnhJG6WkSR0sy6ORz3R3bvOkYahYmMiSB^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://hotels.ctrip.com/^" ^
  -H ^"sec-ch-ua: ^\^"Google Chrome^\^";v=^\^"143^\^", ^\^"Chromium^\^";v=^\^"143^\^", ^\^"Not A(Brand^\^";v=^\^"24^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36^" ^
  -H ^"x-ctx-country: CN^" ^
  -H ^"x-ctx-currency: CNY^" ^
  -H ^"x-ctx-locale: zh-CN^" ^
  -H ^"x-ctx-ubt-pageid: 10650171192^" ^
  -H ^"x-ctx-ubt-pvid: 9^" ^
  -H ^"x-ctx-ubt-sid: 4^" ^
  -H ^"x-ctx-ubt-vid: 1767516589173.22e8NgSJdDEM^" ^
  -H ^"x-ctx-wclient-req: 38d60d2bc37fa26799445e014269af15^" ^
  --data-raw ^"^{^\^"date^\^":^{^\^"dateType^\^":1,^\^"dateInfo^\^":^{^\^"checkInDate^\^":^\^"20260105^\^",^\^"checkOutDate^\^":^\^"20260106^\^"^}^},^\^"destination^\^":^{^\^"type^\^":1,^\^"geo^\^":^{^\^"cityId^\^":2^},^\^"keyword^\^":^{^\^"word^\^":^\^"^\^"^}^},^\^"extraFilter^\^":^{^\^"childInfoItems^\^":^[^],^\^"ctripMainLandBDCoordinate^\^":true,^\^"sessionId^\^":^\^"^\^",^\^"extendableParams^\^":^{^\^"tripWalkDriveSwitch^\^":^\^"T^\^",^\^"isUgcSentenceB^\^":^\^"^\^",^\^"timeStamp^\^":^\^"1767612983616^\^"^}^},^\^"filters^\^":^[^{^\^"type^\^":^\^"17^\^",^\^"title^\^":^\^"^ ^ ^ ^ ^ ^\^",^\^"value^\^":^\^"1^\^",^\^"filterId^\^":^\^"17^|1^\^"^},^{^\^"type^\^":^\^"80^\^",^\^"title^\^":^\^"^\^",^\^"value^\^":^\^"2^\^",^\^"filterId^\^":^\^"80^|2^\^"^},^{^\^"filterId^\^":^\^"29^|1^\^",^\^"type^\^":^\^"29^\^",^\^"value^\^":^\^"1^|1^\^"^}^],^\^"roomQuantity^\^":1,^\^"marketInfo^\^":^{^},^\^"paging^\^":^{^\^"pageIndex^\^":1,^\^"pageSize^\^":10,^\^"pageCode^\^":^\^"10650171192^\^"^},^\^"hotelIdFilter^\^":^{^\^"hotelAldyShown^\^":^[^]^},^\^"head^\^":^{^\^"platform^\^":^\^"PC^\^",^\^"cver^\^":^\^"0^\^",^\^"cid^\^":^\^"1767516589173.22e8NgSJdDEM^\^",^\^"bu^\^":^\^"HBU^\^",^\^"group^\^":^\^"ctrip^\^",^\^"aid^\^":^\^"1315^\^",^\^"sid^\^":^\^"1535^\^",^\^"ouid^\^":^\^"^\^",^\^"locale^\^":^\^"zh-CN^\^",^\^"timezone^\^":^\^"8^\^",^\^"currency^\^":^\^"CNY^\^",^\^"pageId^\^":^\^"10650171192^\^",^\^"vid^\^":^\^"1767516589173.22e8NgSJdDEM^\^",^\^"guid^\^":^\^"^\^",^\^"isSSR^\^":false,^\^"extension^\^":^[^{^\^"name^\^":^\^"cityId^\^",^\^"value^\^":^\^"^\^"^},^{^\^"name^\^":^\^"checkIn^\^",^\^"value^\^":^\^"2026-01-05^\^"^},^{^\^"name^\^":^\^"checkOut^\^",^\^"value^\^":^\^"2026-01-06^\^"^},^{^\^"name^\^":^\^"region^\^",^\^"value^\^":^\^"CN^\^"^}^]^}^}^"
"""
if __name__ == "__main__":
    pass
