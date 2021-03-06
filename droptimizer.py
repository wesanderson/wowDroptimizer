import gspread
import selenium
import re
from selenium import webdriver
from oauth2client.service_account import ServiceAccountCredentials

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# ONLY NEEDED FOR LAMBDA SUPPORT
#import os
 
#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument('--window-size=1280x1696')
#chrome_options.add_argument('--user-data-dir=/tmp/user-data')
#chrome_options.add_argument('--hide-scrollbars')
#chrome_options.add_argument('--enable-logging')
#chrome_options.add_argument('--log-level=0')
#chrome_options.add_argument('--v=99')
#chrome_options.add_argument('--single-process')
#chrome_options.add_argument('--data-path=/tmp/data-path')
#chrome_options.add_argument('--ignore-certificate-errors')
#chrome_options.add_argument('--homedir=/tmp')
#chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
#chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
#chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

googleDocName = "Copy of WoW"
prioritiesTab = "Boss Priorities"

sheet = client.open(googleDocName).worksheet(prioritiesTab)

# Extract and print all of the values
raider_names = sheet.col_values(1)[1:]
print(raider_names)

success = []
fails = []
skips = []
wrongSpec = []

# Using Chrome to access web
driver = webdriver.Chrome()#chrome_options=chrome_options)
tabNum=0;
for raider in (raider_names) :
	print("\n_______________________________________________________")
	print("Running", raider,"'s parse")
	
	charRow = sheet.find(raider).row
	roleColumn = sheet.find('Role').col
	charRole = sheet.cell(charRow, roleColumn).value
	
	if charRole == 'Heals':
		print("Skipping simming heals")
		skips.append(raider)
		continue
	
	try :
		# Navigate to Droptimizer
		driver.get('https://www.raidbots.com/simbot/droptimizer')
		waitForLoad = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "ArmoryInput-armorySearch")))

		# Input character name
		character = driver.find_element_by_id('ArmoryInput-armorySearch')
		character.clear()
		character.send_keys(raider)

		# Set Area 52 Realm
		realm = driver.find_element_by_id('ArmoryInput-armoryRealm')
		realm.click()
		area52 = driver.find_element_by_xpath("//*[@id='react-select-2-option-17']") 
		area52.click()

		run = driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div[2]/section/div[7]/div/div/button")
		run.click()

		print("Waiting for character to load")
		# wait for element to appear
		waitForLoad = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//*[@id='app']/div/div[2]/section/section/div[2]/section/div[1]/div[2]/div[1]/div[3]/div/div[2]/div/div[2]")))

		# if wrong spec
		src = driver.page_source
		text_found = re.search("Your spec is not supported in SimulationCraft at this time", src)
		if text_found:
			print("Wrong spec! Skipping")
			tabNum+=1;
			print("Switching to tab", str(tabNum))
			driver.execute_script("window.open();")
			driver.switch_to.window(driver.window_handles[tabNum])
			wrongSpec.append(raider)
			continue
		else :
			print("Spec good. Proceeding")

		print("Selecting Castle Nathria")
		castleNathria = driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div[2]/section/div[2]/div[1]/div[2]/div/div[2]")
	
		actions = ActionChains(driver)
		actions.move_to_element(castleNathria).perform()
	
		body = driver.find_element_by_css_selector('body')
		body.click()
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
		body.send_keys(Keys.DOWN)
	
		WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.XPATH, "//*[@id='app']/div/div[2]/section/section/div[2]/section/div[2]/div[1]/div[2]/div/div[2]"))).click()
	
		print("Time to sim!")
		button = driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div[2]/section/div[7]/div/div/button")
		driver.execute_script("arguments[0].click();", button)

		waitForLoad = WebDriverWait(driver, 900).until(ec.visibility_of_element_located((By.XPATH, "//*[@id='app']/div/div[2]/section/section/div/div[2]/div[1]/div[1]/div[1]/div[2]")))
		print("Sim complete!")

		sheet.update_cell(charRow, 14, driver.current_url)
		
		print("Sim URL updated. Parsing priorities")

		priorityDiv = 2
		try :
			if driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div/div[2]/div[1]/div[3]/div[2]/div[2]"):
				priorityDiv = 3
		except :
			print("Trying the alt priority lookup div (2)")
		for i in range (2,12) :
			bossName = driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div/div[2]/div[1]/div["+str(priorityDiv)+"]/div["+str(i)+"]/div[2]").text
			bossPriority = driver.find_element_by_xpath("//*[@id='app']/div/div[2]/section/section/div/div[2]/div[1]/div["+str(priorityDiv)+"]/div["+str(i)+"]/div[6]/div/div").text
			print("\t",bossName, "priority", bossPriority)
		
			bossColumn = sheet.find(bossName).col
	
			sheet.update_cell(charRow, bossColumn, bossPriority)
		
		print(raider,"'s sim is complete")
		success.append(raider)
	except Exception as e :
		print("Failed to parse", raider)
		print (e)
		fails.append(raider)
	tabNum+=1;
	print("Switching to tab", str(tabNum))
	driver.execute_script("window.open();")
	driver.switch_to.window(driver.window_handles[tabNum])
	
print("Successful parses",success)
print("Failed parses",fails)
print("Skipped parses",skips)
print("Wrong spec parses",wrongSpec)