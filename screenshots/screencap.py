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
chrome_options.binary_location = CHROME_PATH

def make_screenshot(url, output):

    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        chrome_options=chrome_options
    )
    driver.get(url)

    retval = ""
    while retval.lower().strip() != 'complete':
        retval = driver.execute_script("return document.readyState")
        time.sleep(1)

    driver.save_screenshot("/tmp/tmp.png")

    el_id = url.split('#')[1]
    retval = driver.execute_script(f"return document.getElementById('{el_id}').getBoundingClientRect();")

    box = [retval['left'], retval['top'], retval['right'], retval['bottom']]
    el = driver.find_element_by_id(url.split('#')[1]);
    
    from PIL import Image
    im = Image.open("/tmp/tmp.png")
    im2 = im.crop(box)
    im2.save(output)

    driver.close()

if __name__ == '__main__':
    usage = "usage: %prog [options] <url> <output>"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("please specify a URL and an output")

    make_screenshot(args[0], args[1])


