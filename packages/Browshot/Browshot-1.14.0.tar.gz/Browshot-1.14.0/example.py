from browshot import BrowshotClient
import simplejson  as json

client = BrowshotClient('wyiaUrmuTeRENjQJByQDRRsQqxyq', 'http://127.0.0.1:3000/api/v1/', 1)

print "API version : " + client.api_version() + "\n"

instances = client.instance_list()
print json.dumps(instances) + "\n"

instance = client.instance_info(11)
print json.dumps(instance) + "\n"

browsers = client.browser_list()
print json.dumps(browsers) + "\n"

browser = client.browser_info(10)
print json.dumps(browser) + "\n"

screenshot = client.screenshot_create('http://www.google.fr/');
print json.dumps(screenshot) + "\n"

screenshot = client.screenshot_info(screenshot['id'])
print json.dumps(screenshot) + "\n"

screenshots = client.screenshot_list()
print json.dumps(screenshots) + "\n"

data = client.screenshot_thumbnail('http://127.0.0.1:3000/screenshot/image/52942?key=wyiaUrmuTeRENjQJByQDRRsQqxyq');
print "PNG length: " + str(len(data)) + "\n"

client.screenshot_thumbnail_file('http://127.0.0.1:3000/screenshot/image/52942?key=wyiaUrmuTeRENjQJByQDRRsQqxyq', '/tmp/52942-py.png')