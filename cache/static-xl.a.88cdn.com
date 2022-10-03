HTTP/1.1 200 OK
Server: Tengine
Content-Type: application/json
Content-Length: 803
Connection: keep-alive
Date: Mon, 03 Oct 2022 04:46:25 GMT
Last-Modified: Fri, 09 Sep 2022 08:16:14 GMT
ETag: "631af64e-323"
Expires: Mon, 03 Oct 2022 05:46:25 GMT
Cache-Control: max-age=3600
Access-Control-Allow-Origin: *
Accept-Ranges: bytes
Ali-Swift-Global-Savetime: 1664772385
Via: cache48.l2cm9-5[0,0,304-0,H], cache7.l2cm9-5[0,0], cache3.cn4473[0,0,200-0,H], cache2.cn4473[1,0]
Age: 1081
X-Cache: HIT TCP_MEM_HIT dirn:11:224599460
X-Swift-SaveTime: Mon, 03 Oct 2022 04:46:25 GMT
X-Swift-CacheTime: 3600
Access-Control-Allow-Methods: POST, GET, PUT, OPTIONS, DELETE
Timing-Allow-Origin: *
EagleId: dec0bb1616647734667932925e

{"type":"black","domains":["v.youku.com","iqiyi.com","v.qq.com","ixigua.com","weibo.com","cctv.com","huya.com","douyu.com","bilibili.com","bilibili.to","163.com","youdao.com","zhihu.com","haokan.baidu.com","video.sina.com.cn","zjstv.com","qq.com","64memo.com","64tianwang.com","asp.fgmtv.org","bannedbook.net","bannedbook.org","beijingzx.org","china21.org","dongtaiwang.com","epochtimes.com","falundafa.org","falundafamuseum.org","fgmtv.org","hrichina.org","internetfreedom.org","maxtv.cn","mhradio.org","minghui.org","mingjingnews.com","ntdtv.com","rfa.org","secretchina.com","tuidang.org","publicdbhost.dmca.gripe","ai-course.cn","mingpao.com","xiaohongshu.com","douyin.com","le.com","pptv.com","mgtv.com","migu.cn","fun.tv","sohu.com","kuaishou.com"],"black_list":["*.aliyundrive.com"],"isStat":true}