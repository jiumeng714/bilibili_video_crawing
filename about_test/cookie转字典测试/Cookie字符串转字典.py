import json
import struct
import re

cook = 'buvid3=27AE5D48-1217-4466-F8DB-3135928BD57431748infoc; i-wanna-go-back=-1; _uuid=10B947524-314F-107D7-F23B-B25A103D935FD33501infoc; buvid4=40210152-0B10-61FB-03AF-5AFBE71CD37E35378-022031221-9TjwrHxcIBsA7Vm4zewkUg==; buvid_fp_plain=undefined; DedeUserID=274308304; DedeUserID__ckMd5=9552bbbc4c1a35c1; CURRENT_BLACKGAP=0; b_ut=5; LIVE_BUVID=AUTO4916471516555643; nostalgia_conf=-1; hit-dyn-v2=1; blackside_state=0; is-2022-channel=1; b_timer={"ffp":{"333.1007.fp.risk_27AE5D48":"182CFF33658","333.788.fp.risk_27AE5D48":"182CFF3518B","444.41.fp.risk_27AE5D48":"180C5F294EA","333.337.fp.risk_27AE5D48":"182C56D2D6B","333.976.fp.risk_27AE5D48":"1810E0F70E7","888.65485.fp.risk_27AE5D48":"180C600C8A9","333.999.fp.risk_27AE5D48":"182CFF342F5","777.5.0.0.fp.risk_27AE5D48":"182CB1FF652","888.2421.fp.risk_27AE5D48":"182CB1FF5CF","333.937.fp.risk_27AE5D48":"181D8FB399D","444.8.fp.risk_27AE5D48":"1823AC5E01B",".fp.risk_27AE5D48":"18235851361","333.1193.fp.risk_27AE5D48":"182CF9CD510","333.1073.fp.risk_27AE5D48":"182B106BDDB"}}; SESSDATA=d157dd5f,1677676302,81dd2*91; bili_jct=ebf5486811e98eb698fa540b55a64b0f; sid=72euvg0o; b_nut=100; rpdid=|(J|)ll~m|l|0JuYY)lmJRuJ; hit-new-style-dyn=0; CURRENT_FNVAL=4048; share_source_origin=WEIXIN; fingerprint=c5f780ae17e05bb043bd50274759077b; buvid_fp=c5f780ae17e05bb043bd50274759077b; bp_t_offset_274308304=747678803426279463; PVID=2; bsource=search_baidu; CURRENT_QUALITY=80; bp_video_offset_274308304=747986752568819700; b_lsid=5BA895B10_185867913E4; innersign=0'
result = re.search('SESSDATA([\w\W])*;', cook).group()
result = result.split(';')[0]
print(result)



