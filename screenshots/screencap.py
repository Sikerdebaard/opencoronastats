import os
import time

from optparse import OptionParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = '/usr/bin/google-chrome'
CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
WINDOW_SIZE = "1920,1080"
#WINDOW_SIZE = "2560,1440"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--verbose")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-file-access-from-files")
chrome_options.binary_location = CHROME_PATH

def make_screenshot(driver, url, output):
    driver.get(url)

    retval = ""
    while retval.lower().strip() != 'complete':
        retval = driver.execute_script("return document.readyState")
        time.sleep(1)

    driver.save_screenshot("/tmp/tmp.png")

    el_id = url.split('#')[1]


    times = 0
    while driver.execute_script(f"return document.getElementById('{el_id}');") is None:
        time.sleep(10)
        times += 1
        if times >= 6:
            times = 0
            driver.get(url)
            time.sleep(20)

    retval = driver.execute_script(f"return document.getElementById('{el_id}').getBoundingClientRect();")

    box = [retval['left'], retval['top'], retval['right'], retval['bottom']]
    el = driver.find_element_by_id(url.split('#')[1]);
    
    from PIL import Image
    im = Image.open("/tmp/tmp.png")
    im2 = im.crop(box)
    im2.save(output)

    for log in driver.get_log('browser'):
        print(log)


if __name__ == '__main__':
    usage = "usage: %prog [options] <urlmap>"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("please specify a URL and an output")

    import json
    with open(args[0], 'r') as fh:
        pagemap = json.load(fh)
    
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        chrome_options=chrome_options
    )


    for url, output in pagemap.items():
        make_screenshot(driver, url, output)
    
    driver.close()


