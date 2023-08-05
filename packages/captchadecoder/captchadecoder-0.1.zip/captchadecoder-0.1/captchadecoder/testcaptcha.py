import mechanize
import urllib
import json
import captchadecoder;

cd = captchadecoder.CaptchaDecoder()

br = mechanize.Browser()
url = "http://skyscraper.zenyai.net/captcha_api.php"


result = []
data = json.loads(br.open(url).read())
i = 1
for dt in data:
    answer = dt['answer']
    img_url = "http://skyscraper.zenyai.net/captchas/"+dt['md5_hash']+".png"

    # f = open('example/%s.png' % answer,'wb')
    # f.write(br.open(img_url).read())
    # f.close()

    guess = cd.DecodeImageURL(img_url, False)

    if guess == answer:
        result.append("Yes")
    else:
        result.append("No")

    try:
        percentage = float(result.count("No"))/float(result.count("Yes")) * 100
    except Exception:
        percentage = 0

    print "#" + str(i) + ": " + str(guess) + " " + str(answer) + ", C: " +  str(result.count("Yes")) + " W: " + str(result.count("No")) + " WP: " + str(percentage) + "%"
    i += 1


print "Total number of correct guess: " + str(result.count("Yes"))
print "Wrong guess: " + str(result.count("No"))