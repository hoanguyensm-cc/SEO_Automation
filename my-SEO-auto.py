from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
from selenium.webdriver.support.ui import Select
import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import random
import datetime
# packages for Google Sheet
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
MY_SPREADSHEET_ID = "1XqNC37YO0J8FaJe_BTCItgqVRzqDhoGJPdOllK8ml6Q" #sheet name: SEO metatags request

SHEET_IMPLEMENT_META_TAGS = "1. Implement Meta tags!A2:E" #tab 1. Implement Meta tags
SHEET_IMPLEMENT_META_TAGS_QA_COLUMN = "1. Implement Meta tags!D2:D" #tu cell 2 tro di cua column D

SHEET_IMPLEMENT_SOCIAL_TAGS = "2. Implement social tags!A2:D" #tab 2. Implement social tags
SHEET_IMPLEMENT_SOCIAL_TAGS_QA_COLUMN = "2. Implement social tags!D2:G" #tu cell 2 tro di cua column D

SHEET_QA_META_TAGS = "QA metatags!A2:G" #tab QA metatags
SHEET_QA_META_TAGS_QA_COLUMN = "QA metatags!B2:G" #tu cell 2 tro di cua column B -> G

SHEET_QA_SOCIAL_TAGS = "QA social tags!A2:G" #tab QA social tags
SHEET_QA_SOCIAL_TAGS_QA_COLUMN = "QA social tags!C2:G" #tu cell 2 tro di cua column C->G

SHEET_CHECK_META_TAGS = "Check metatags!A2:G" #tab Check metatags tags
SHEET_CHECK_META_TAGS_QA_COLUMN = "Check metatags!B2:G" #tu cell 2 tro di cua column B -> G

SHEET_CHECK_SOCIAL_TAGS = "Check social tags!A2:G" #tab Check social tags
SHEET_CHECK_SOCIAL_TAGS_QA_COLUMN = "Check social tags!B2:G" #tu cell 2 tro di cua column F va G

SHEET_VALIDATE_SOCIAL_TAGS = "Validate social tags!A2:B" #tab QA social tags
SHEET_VALIDATE_SOCIAL_TAGS_QA_COLUMN = "Validate social tags!B2:B" #tu cell 2 tro di cua column B

SHEET_PUSH_LIVE = "Push Live!A2:B" #tab Push Live
SHEET_PUSH_LIVE_STATUS_COLUMN = "Push Live!B2:B" #tu cell 2 tro di cua column B

SHEET_CHECK_RESPONSE = "Check response!A2:B" #tab Check response
SHEET_CHECK_RESPONSE_STATUS_COLUMN = "Check response!B2:B" #tu cell 2 tro di cua column B

SHEET_GET_LIST_SKUs_COLUMN = "Get SKUs!A2:B" #tab Get SKUs
SHEET_GET_LIST_SKUs_RESULT_COLUMN = "Get SKUs!B2:B" #tu cell 2 tro di cua column B

SHEET_OLD_DATA = "Old data!A2:L"


### CHECKLIST
# 1. cookie login
# 2. B2C/B2B
# 3. Sitecode
# 4. JIRA
###

####################### CHECKLIST#####################################
cookie_loggin = {
                "name": "JSESSIONID",
                "value": "D2163C5F71172712DFEFA4671A17CC4C"
                }
FLATFORM = 'B2C'
SITECODE = 'nz'
JIRA_URL = 'https://jira.secext.samsung.net/browse/WSC20200015-23521'
SEAO_TABLE_NEW = 'tbl_seao'
SEAO_TABLE = 'seao'

####################### end CHECKLIST##################################

SMARTDEVICES_CHARS = '-sm-'
SKU_NOT_FOUND = 'SKU not found'

WMC = 'https://wds.samsung.com/'
WMC_LoggedIn_Succeed = 'https://wds.samsung.com/wds/sso/login/ssoLoginSuccess.do'
SEO_Tag_Mgmt_B2C = 'https://p6-ap-author.samsung.com/pim/b2c/pdsetting/seo/page/list'
SEO_Tag_Mgmt_B2B = 'https://p6-ap-author.samsung.com/bim/b2b/pdsetting/seo/page/list'

twitterDict = {
    'vn': '@SamsungVN',
    'id': '@SamsungID',
    'my': '@SamsungMalaysia',
    'ph': '@SamsungPH',
    'nz': '@SamsungNZ', #account suspended due to violate X Rules
    'sg': '@SamsungSG',
    'th': '@SamsungThailand',
}
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome()

###SAMPLE URLs
SAMPLE_FEATURE_PDP = 'https://p6-qa.samsung.com/vn/smartphones/galaxy-a/galaxy-a35-5g-awesome-iceblue-128gb-sm-a356elbdxxv/'
SAMPLE_BUY_PDP1 = 'https://p6-qa.samsung.com/vn/smartphones/galaxy-a/galaxy-a35/buy/?modelCode=SM-A356ELBDXXV'
SAMPLE_BUY_PDP2 = 'https://p6-qa.samsung.com/vn/smartphones/galaxy-a/galaxy-a55/buy/'
SAMPLE_BUY_PDP3 = 'https://p6-qa.samsung.com/vn/watches/galaxy-watch/galaxy-watch6-40mm-gold-bluetooth-sm-r930nzeaxxv/buy/'
SAMPLE_BUY_PDP4 = 'https://p6-qa.samsung.com/vn/washers-and-dryers/washing-machines/ww7400t-10kg-platinum-silver-ww10tp44dsb-sv/'

listURLs = [
    SAMPLE_FEATURE_PDP,
    SAMPLE_BUY_PDP1,
    SAMPLE_BUY_PDP2,
    SAMPLE_BUY_PDP3,
    SAMPLE_BUY_PDP4
]
listSKUs = []
#####################################DEFINE FUNCTIONS########################################################


def isItemMatched(item, tobeItem):
    if (item == tobeItem):
        return 'Yes'
    else:
        return 'No'

def isInRegistration(pageURL):
    if 'p6-qa' in pageURL:
        return 'Yes'
    else:
        return 'No'

def openQAauthentication():
    QA_authen_link = driver.find_element(By.CSS_SELECTOR, '.wcmMenuTopWrap .wcmMenuTop dl:nth-of-type(4) dd:first-of-type a')
    if (QA_authen_link.text == 'QA'):
        QA_authen_link.click()
        time.sleep(5)
        return True
    else:
        print('QA authentication link is not found on AEM.')
        return False

def openSitesauthentication():
    sites_authen_link = driver.find_element(By.CSS_SELECTOR, '.wcmMenuTopWrap .wcmMenuTop dl:first-of-type dd:first-of-type a')
    if (sites_authen_link.text == 'B2C/B2B'):
        sites_authen_link.click()
        time.sleep(5)
        return True
    else:
        print('Sites authentication link is not found on AEM.')
        return False

def openAEM():
    driver.get(WMC)
    time.sleep(5)

    driver.add_cookie(cookie_loggin)

    try:
        driver.get(WMC_LoggedIn_Succeed)
        time.sleep(5)
        return True

    except Exception as e:
        print('Fail to login AEM.')

    return False #Login failed

def isBuyPage(pageURL):
    if ('/buy/' in pageURL):
        return True
    return False

#SmartDevices thi co ca Feature va Buy page
def isSmartDevices(pageURL):
    return SMARTDEVICES_CHARS in pageURL

def getSKU(pageURL):
    #1. Neu la SmartDevices
    ## Lay SKU dua tren URL
    if (isSmartDevices(pageURL)):
        skuText = pageURL.split(SMARTDEVICES_CHARS)[1]
        sku = skuText[:11] #Lay 11 ki tu
        return sku.upper()
    #2. Khong phai la SmartDevices
    ## Lay SKU dua ten HTML element
    else:
        try:
            driver.get(pageURL)
            time.sleep(4)
            sku = driver.find_element(By.CLASS_NAME, 'pd-info__sku-code').text
        except Exception as e:
            sku = SKU_NOT_FOUND
        return sku

def isB2C():
    if FLATFORM == 'B2C':
        return True
    else:
        return False

def getMetaTagsOnly(url):
    driver.get(url)
    time.sleep(2)
    titleElement = driver.find_element(By.XPATH, "//meta[@name='title']")
    descElement = driver.find_element(By.XPATH, "//meta[@name='description']")
    pageMetaTags = {
        'title' : titleElement.get_attribute('content'),
        'description' : descElement.get_attribute('content')
    }
    return pageMetaTags

def checkMetaTagsAfterLive():
    print('Start checking metatags afer live.')
    sheetdata = openGSheetTab(SHEET_CHECK_META_TAGS)
    driver.switch_to.new_window('tab')
    recacheStr = f'?recache={random.random()*100}'
    QAresults = []
    for row in sheetdata:
        url = row[0]
        url = url + recacheStr
        metatags = getMetaTagsOnly(url)
        title = metatags['title']
        desc = metatags['description']
        titleStatus = isItemMatched(title, row[3])
        descStatus = isItemMatched(desc, row[4])
        QAresults.append([title, desc, None, None, titleStatus, descStatus])
        updateToGoogleSheet(SHEET_CHECK_META_TAGS_QA_COLUMN, QAresults)

    print('Done checking metatags after live.')


def checkSocialTagsAfterLive():
    print('Start checking metatags for social after LIVE...')
    sheetdata = openGSheetTab(SHEET_CHECK_SOCIAL_TAGS)
    QAresults = []
    for row in sheetdata:
        url = row[0]
        result = getSocialTagsOnly(url)
        description = result['description']
        descStatus = isItemMatched(description, row[4])
        QAresults.append([None, description, None, None, None, descStatus])
        updateToGoogleSheet(SHEET_CHECK_SOCIAL_TAGS_QA_COLUMN, QAresults)

    print('Done checking metatags for social after LIVE.')

def getSocialTagsOnly(url):
    driver.get(url)
    time.sleep(1)
    twitterElement = driver.find_element(By.XPATH, "//meta[@name='twitter:description']")
    # ogElement = driver.find_element(By.XPATH, "//meta[@property='og:description']")
    socialMeta = {
        'description': twitterElement.get_attribute('content')
    }
    return socialMeta

def openGSheetTab(range):
    creds = getGoogleSheetCredential() #get credential
    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=MY_SPREADSHEET_ID, range=range)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        return values

    except HttpError as err:
        print(err)

def getGoogleSheetCredential():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials_googlesheets.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  return creds

def validateSocialTags():
    print("Start validating social tags if the implementation was correct or not......")
    sheetdata = openGSheetTab(SHEET_QA_SOCIAL_TAGS)
    #QAresults = []
    driver.switch_to.new_window('tab')
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        if canOpenQA:
            driver.switch_to.new_window('tab')
            QAresults = []
            for row in sheetdata:
                url = row[0]
                result = getSocialTagsOnly(url)
                description = result['description']
                descStatus = isItemMatched(description, row[4])
                QAresults.append([description, None, None, None, descStatus])
                updateToGoogleSheet(SHEET_QA_SOCIAL_TAGS_QA_COLUMN, QAresults)

            print('DONE validating social tags.')

def validateMetaTags():
    print('Start validating meta tags if the implementation was correct or not ....')
    sheetdata = openGSheetTab(SHEET_QA_META_TAGS)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            QAresults = []
            for row in sheetdata:
                url = row[0]
                metatags = getMetaTagsOnly(url)
                title = metatags['title']
                desc = metatags['description']
                titleStatus = isItemMatched(title, row[3])
                descStatus = isItemMatched(desc, row[4])
                QAresults.append([title, desc, None, None, titleStatus, descStatus])
                updateToGoogleSheet(SHEET_QA_META_TAGS_QA_COLUMN, QAresults)

            print('DONE validating meta tags.')

def isSocialTagsEmpty(url):
    driver.get(url)
    time.sleep(1)
    twitterElement = driver.find_element(By.XPATH, "//meta[@name='twitter:description']")
    ogElement = driver.find_element(By.XPATH, "//meta[@property='og:description']")
    cardElement = driver.find_element(By.XPATH, "//meta[@name='twitter:card']")
    twitterMeta = twitterElement.get_attribute('content')
    ogMeta = ogElement.get_attribute('content')
    cardMeta = cardElement.get_attribute('content')
    if ( len(twitterMeta) == 0 or len(ogMeta) == 0 or len(cardMeta) == 0):
        return False
    else:
        return True

def checkIfSocialTagsEmpty():
    print("Start running to check if social tags are empty or not. Return True if it's empty")
    sheetdata = openGSheetTab(SHEET_VALIDATE_SOCIAL_TAGS)
    driver.switch_to.new_window('tab')
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        if canOpenQA:
            driver.switch_to.new_window('tab')
            QAresults = []
            funcChecking = lambda x: 'Yes' if x == True else 'No'
            for row in sheetdata:
                url = row[0]
                isEmpty = isSocialTagsEmpty(url)
                itemCheck = [funcChecking(isEmpty)]
                QAresults.append(itemCheck)
                updateToGoogleSheet(SHEET_VALIDATE_SOCIAL_TAGS_QA_COLUMN, QAresults)

            print('DONE checking if social tags are empty or not.')
            driver.close()

def updateToGoogleSheet(sheetRange, values):
    creds = getGoogleSheetCredential() #get credential
    try:
        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=MY_SPREADSHEET_ID,
                range=sheetRange,
                valueInputOption="USER_ENTERED",
                body=body
            )
            .execute()
        )

    except HttpError as error:
        print(f"Writing to google sheet got errors: {error}")
        return error

def searchSKU(sku):
    if sku != SKU_NOT_FOUND:
        if (isB2C()): #B2C flatform
                driver.get(SEO_Tag_Mgmt_B2C)

        else: #B2B flatform
                driver.get(SEO_Tag_Mgmt_B2B)

        time.sleep(5)

        #set Sitecode value
        siteCode_dropdown = Select(driver.find_element(By.ID, 'searchSiteCodeList'))
        siteCode_dropdown.select_by_value(SITECODE)

        time.sleep(1)

        #click Model
        model_toggle = driver.find_element(By.ID, 'headingModel')
        model_toggle.click()

        # Setup wait for later
        wait = WebDriverWait(driver, 3)

        #input SKU to search
        skuElement = wait.until(EC.visibility_of_element_located((By.ID, 'txtInquiryModel')))
        skuElement.send_keys(sku)

        #hit Search button
        searchBtn = driver.find_element(By.ID, 'btnSearch')
        searchBtn.click()

        print('hit Search done')
        time.sleep(4)
        # check if the product is showing or not
        # displayFlag = driver.find_element(By.XPATH, "//*[@id='1']/td[6]")
        displayFlag = 'Y' # hardcode here
        if (displayFlag == 'Y'):
            btnSeoMgmt = driver.find_element(By.CLASS_NAME, 'btnSeoMgmt')
            ActionChains(driver).move_to_element(btnSeoMgmt).key_down(Keys.CONTROL).click(btnSeoMgmt).key_up(Keys.CONTROL).perform()
            time.sleep(3)
            return True

        else:
            print('The product is hidden (displaying No).')
            return False

    else:
        return False

def goPushLive(sku):
    #hit LIVE
    btnLIVE = driver.find_element(By.ID, 'btnLive')
    btnLIVE.click()
    time.sleep(2)

    #hit OK on popup
    btnOktoLIVE = driver.find_element(By.CSS_SELECTOR, "#ok.btn1Inp .btn")
    btnOktoLIVE.click()
    time.sleep(6)

    #hit Close popup
    btnCloseLIVE = driver.find_element(By.CSS_SELECTOR, '#close.btn1Inp .btn')
    btnCloseLIVE.click()
    time.sleep(2)

    print(f'Done pushing live for sku {sku}.')

    driver.close()


def pushLive():
    print('Start pushing LIVE...')
    sheetdata = openGSheetTab(SHEET_PUSH_LIVE)
    driver.switch_to.new_window('tab')
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenSiteAuthen = openSitesauthentication()
        time.sleep(2)

        if canOpenSiteAuthen:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            driver.switch_to.new_window('tab')
            time.sleep(1)
            liveStatus = []
            for row in sheetdata:
                # url = row[0]
                driver.switch_to.window(driver.window_handles[3]) #Tab nay de open page & get SKU
                # sku = getSKU(url)
                sku = row[0]
                if sku != SKU_NOT_FOUND:
                    driver.switch_to.window(driver.window_handles[4]) #Tab nay de open SEO Tag Mgmt
                    isSKUdisplaying = searchSKU(sku)
                    if isSKUdisplaying:
                        driver.switch_to.window(driver.window_handles[5]) # Detail tab
                        modelCode = driver.find_element(By.ID, 'detailModelCode').text
                        print(f'Number of window tabs: {len(driver.window_handles)}')
                        if (modelCode.endswith(sku)): #checking for sure that I'm on correct SKU
                            goPushLive(sku)
                            liveStatus.append(['Done'])
                        else:
                            print('Wrong tab/Wrong sku due to page redirected')
                            liveStatus.append(['Failed'])
                    '''
                    Note about Tabs order:
                        TAB1: GOOGLE SHEET
                        TAB2: WMC
                        TAB3: SITE AUTHENTICATION
                        TAB4: GET SKU
                        TAB5: SEO TAG MGMT
                        TAB6: SKU DETAIL
                    '''
                else:
                    liveStatus.append(['Failed'])
                    print(SKU_NOT_FOUND)

                updateToGoogleSheet(SHEET_PUSH_LIVE_STATUS_COLUMN, liveStatus)

            print("DONE pushing LIVE.")


def implementMetaTags():
    print('Start implementing SEO metatags...')
    sheetdata = openGSheetTab(SHEET_IMPLEMENT_META_TAGS)
    driver.switch_to.new_window('tab')
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        driver.switch_to.window(driver.window_handles[1]) # tab WMC
        time.sleep(2)
        canOpenSiteAuthen = openSitesauthentication()

        if (canOpenQA and canOpenSiteAuthen):
            implementStatus = []
            bqData = []
            qaLink = ''
            status = ''
            now = datetime.datetime.now()
            localDate = now.strftime("%x")
            localTime = now.strftime("%X")

            for row in sheetdata:
                url = row[0]
                driver.switch_to.window(driver.window_handles[2]) # tab Get SKU
                time.sleep(1)
                # sku = getSKU(url)
                sku = row[0] #This is SKU
                if (sku != SKU_NOT_FOUND):
                    driver.switch_to.window(driver.window_handles[3]) # tab SEO Tag Mgmt
                    isSKUdisplaying = searchSKU(sku)
                    if isSKUdisplaying:
                        driver.switch_to.window(driver.window_handles[4]) # Detail tab
                        modelCode = driver.find_element(By.ID, 'detailModelCode').text
                        recommendedTitle = row[1]
                        recommendedDesc = row[2]
                        recommendedKW = row[4]


                        if (modelCode.endswith(sku)): #checking for sure that I'm on correct SKU
                            goImplementMetaTags(url, recommendedTitle.strip() , recommendedDesc.strip(), recommendedKW.strip())
                            qaLink = url.replace('www', 'p6-qa')
                            implementStatus.append([qaLink])
                            status = 'implemented'
                            print(f'Done implementing for sku {sku}')

                        else:
                            qaLink = None
                            implementStatus.append(['Not implemented yet'])
                            status = 'Not implemented yet'
                            print('Wrong tab/Wrong sku due to page redirected')
                else:
                    print(SKU_NOT_FOUND)

                updateToGoogleSheet(SHEET_IMPLEMENT_META_TAGS_QA_COLUMN, implementStatus)

                isRegistering = isInRegistration(url)
                bqRow = [SITECODE, FLATFORM, JIRA_URL, url, recommendedTitle, recommendedDesc, qaLink, isRegistering, status, localDate, localTime, 'Metatags']
                bqData.append(bqRow)

            '''
            Note for Tabs order:
                TAB1: Google Sheet
                TAB2: WMC
                TAB3: Site authen
                TAB4: QA authen
                TAB5: SKU Detail
            '''
            column_names = columnNames()

            df = pd.DataFrame(bqData, columns=column_names)
            print(df)
            writeDataToBigQuery(df, SEAO_TABLE_NEW)

    print('Done implementing SEO metatags.')

def goImplementTwitterSiteCreator():
    siteEl = driver.find_element(By.ID, 'twitterSite')
    creatorEl = driver.find_element(By.ID, 'twitterCreator')
    twitterAccount = twitterDict[SITECODE]
    siteEl.clear()
    siteEl.send_keys(twitterAccount)
    creatorEl.clear()
    creatorEl.send_keys(twitterAccount)
    time.sleep(2)

def doImplementKeywords(kw):
    #Feature page
    metaTagKeyword = driver.find_element(By.ID, 'metaTagKeyword')
    metaTagKeyword.clear()
    metaTagKeyword.send_keys(kw)

    # Buy page
    # Check them dieu kien o day. Dung keywords nao?
    metaTagKeywordPd = driver.find_element(By.ID, 'metaTagKeywordPd')
    metaTagKeywordPd.clear()
    metaTagKeywordPd.send_keys(kw)


def goImplementMetaTags(url, title, desc, kw=''):
    if isBuyPage(url):
        # Buy pages
        if (title != 'N/A'):
            titleEl = driver.find_element(By.ID, 'webBrowserTitiePd')
            titleEl.clear()
            titleEl.send_keys(title)
        if (desc != 'N/A'):
            descEl = driver.find_element(By.ID, "metaTagDescriptionForPd")
            descEl.clear()
            descEl.send_keys(desc)

    else:
        # Feature pages
        if (title != 'N/A'):
            titleEl = driver.find_element(By.ID, 'webBrowserTitie')
            titleEl.clear()
            titleEl.send_keys(title)
        if (desc != 'N/A'):
            descEl = driver.find_element(By.ID, "metaTagDescription")
            descEl.clear()
            descEl.send_keys(desc)

        # keywords implementation goes here
        if(len(kw) != 0 and kw != 'N/A'):
            doImplementKeywords(kw)

    # doSingleTaskImplementSocials(title, desc) #Comment out this line if no need implementation for Socials

    saveChangesAndPushQA()

    driver.close()

def saveChangesAndPushQA():
    try:
        #hit Save
        btnSave = driver.find_element(By.ID, 'btnSave')
        btnSave.click()
        time.sleep(5)

        #hit Close popup
        btnCloseSave = driver.find_element(By.CSS_SELECTOR, '#close.btn1Inp .btn')
        btnCloseSave.click()
        time.sleep(2)

        #push QA
        btnQa = driver.find_element(By.ID, 'btnQa')
        btnQa.click()
        time.sleep(2)

        #hit OK on popup
        btnOktoQA = driver.find_element(By.CSS_SELECTOR, "#ok.btn1Inp .btn")
        btnOktoQA.click()
        time.sleep(5)

        #hit Close popup
        btnClosePopup = driver.find_element(By.CSS_SELECTOR, '#close.btn1Inp .btn')
        btnClosePopup.click()
        time.sleep(2)

    except Exception as e:
        print('Saving got errors.')
        print(e)

def doSingleTaskImplementSocials(title, desc):
    #input value for Summary
    summaryEle = driver.find_element(By.ID, 'twitterCardNm')
    summaryEle.clear()
    summary = summaryEle.text
    if (len(summary.strip()) == 0):
        summaryEle.send_keys('summary')

    if(len(title) != 0 and title != 'N/A'):
        #input value for Twitter/Og Title
        twitterTitle = driver.find_element(By.ID, 'twitterTitle')
        facebookTitle = driver.find_element(By.ID, 'facebookTitle')
        twitterTitle.clear()
        twitterTitle.send_keys(title)
        facebookTitle.clear()
        facebookTitle.send_keys(title)
        time.sleep(2)

    if(len(desc) != 0 and desc != 'N/A'):
        #input value for Twitter/Og Description
        twitterDescEle = driver.find_element(By.ID, 'twitterDesc')
        fbDescEle = driver.find_element(By.ID, 'facebookDesc')
        twitterDescEle.clear()
        twitterDescEle.send_keys(desc)
        fbDescEle.clear()
        fbDescEle.send_keys(desc)
        time.sleep(2)

    #input value for twitter:site and twitter:creator
    #temporarily for ID only
    if(SITECODE == 'id'):
        goImplementTwitterSiteCreator()

    # if (FLATFORM == 'B2B'):
    #     goImplementTwitterSiteCreator()

def goImplementSocials(title, desc):
    doSingleTaskImplementSocials(title, desc)

    saveChangesAndPushQA()

    driver.close()

def implementSocialTags():
    print('Start implementing SEO for social...')
    sheetdata = openGSheetTab(SHEET_IMPLEMENT_SOCIAL_TAGS)
    driver.switch_to.new_window('tab')
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        driver.switch_to.window(driver.window_handles[1]) # tab WMC
        time.sleep(2)
        canOpenSiteAuthen = openSitesauthentication()
        driver.switch_to.new_window('tab')
        time.sleep(1)
        if (canOpenQA and canOpenSiteAuthen):
            implementStatus = []
            bqData = []
            bqRow = []
            qaLink = ''
            status = ''
            now = datetime.datetime.now()
            localDate = now.strftime("%x")
            localTime = now.strftime("%X")

            for row in sheetdata:
                url = row[0]
                sku = row[0]
                driver.switch_to.window(driver.window_handles[4]) # tab Get SKU
                time.sleep(1)
                # sku = getSKU(url)
                if (sku != SKU_NOT_FOUND):
                    driver.switch_to.window(driver.window_handles[2]) # tab SEO Tag Mgmt
                    isSKUdisplaying = searchSKU(sku)
                    if isSKUdisplaying:
                        driver.switch_to.window(driver.window_handles[5]) # Detail tab
                        modelCode = driver.find_element(By.ID, 'detailModelCode').text

                        recommendedTitle = row[1]
                        recommendedDesc = row[2]
                        if (modelCode.endswith(sku)): #checking for sure that I'm on correct SKU
                            goImplementSocials(recommendedTitle.strip(), recommendedDesc.strip())
                            qaLink = url.replace('www', 'p6-qa')
                            implementStatus.append([qaLink])
                            status = 'implemented'
                            print(f'Done implementing for sku {sku}')
                    else:
                        qaLink = None
                        implementStatus.append(['Not implemented yet'])
                        status = 'Not implemented yet'
                        print('Wrong tab/Wrong sku due to page redirected')
                else:
                    qaLink = None
                    implementStatus.append(['Not implemented yet'])
                    print(SKU_NOT_FOUND)

                updateToGoogleSheet(SHEET_IMPLEMENT_SOCIAL_TAGS_QA_COLUMN, implementStatus)

                isRegistering = isInRegistration(url)
                bqRow = [SITECODE, FLATFORM, JIRA_URL, url, None, recommendedDesc, qaLink, isRegistering, status, localDate, localTime, 'Social tags']
                bqData.append(bqRow)

            print('Done implementing metatags for socials.')
            '''
            Note for Tabs order:
                TAB1: Google Sheet
                TAB2: WMC
                TAB3: Site authen
                TAB4: QA authen
                TAB5: Get SKU
                TAB6: SEO Tag Mgmt
                TAB7: SKU Detail
            '''
            column_names = columnNames()
            df = pd.DataFrame(bqData, columns=column_names)
            print(df)
            writeDataToBigQuery(df, SEAO_TABLE_NEW)

def writeDataToBigQuery(df, tableCountry):
    import pandas_gbq
    from google.oauth2 import service_account


    # TODO: set cred your Google Cloud Platform.
    # credentials = service_account.Credentials.from_service_account_file('credentials_googlecloud.json')

    # TODO: Set project_id  your Google Cloud Platform project ID.
    project_id = "my-seo-project-425503"
    # TODO: Set table_id to the full destination table ID (including the
    #       dataset ID).
    table_id = f'SEO_implementation_tracking.{tableCountry}'

    print("Writing data to Google BigQuery...")
    pandas_gbq.to_gbq(df,
                    table_id,
                    project_id=project_id,
                    if_exists="append")

    print("Writing data is completed!")

def columnNames():
    # column_names = ['Country', 'Flatform', 'Jira', 'URL', 'Recommended Title', 'Recommended Description', 'QA link', 'In Registration Progress', 'Status', 'Date', 'Time', 'Job name']
    column_names = ['Country', 'Flatform', 'Jira', 'URL', 'RecommendedTitle', 'RecommendedDescription', 'QAlink', 'InRegistrationProgress', 'Status', 'Date', 'Time', 'JobName']
    return column_names

def goCheckResponse(url):
    myResponse = requests.get(url)
    stausCode = myResponse.status_code
    return [stausCode]

def checkResponseStatus():
    print('Start checking page response...')
    sheetdata = openGSheetTab(SHEET_CHECK_RESPONSE)
    driver.switch_to.new_window('tab')
    QAresults = []
    for row in sheetdata:
        url = row[0]
        status = goCheckResponse(url)
        QAresults.append(status)
        updateToGoogleSheet(SHEET_CHECK_RESPONSE_STATUS_COLUMN, QAresults)
    print('Done checking page response.')

def loadOldData():
    print('Start loading old data...')
    sheetdata = openGSheetTab(SHEET_OLD_DATA)
    driver.switch_to.new_window('tab')
    oldData = []
    for row in sheetdata:
        oldData.append(row)
    column_names = columnNames()
    df = pd.DataFrame(oldData, columns=column_names)
    print(df)
    writeDataToBigQuery(df, SEAO_TABLE_NEW)
    print('Done loading old data...')

#####################################END FUNCTIONS########################################################


if __name__ == '__main__':

    #******** TO-DO LIST ********
    #1. IMPLEMENT META TAGS
    # implementMetaTags()

    #2. VALIDATE META TAGS IF THE IMPLEMENTATION WAS CORRECT
    # validateMetaTags()

    #3. IMPLEMENT SOCIAL TAGS ONLY (for Product Registration stage)
    # implementSocialTags()

    #4. VALIDATE SOCIAL TAGS IF THE IMPLEMENTATION WAS CORRECT
    # validateSocialTags()

    #5. PUSH LIVE THE CHANGES
    ##Only push live for pushlished pages. For pages under registration progress, we cannot push them live from SEO.
    pushLive()

    #6. CHECK META TAGS AFTER LIVE
    # checkMetaTagsAfterLive()

    #7. CHECK SOCIAL TAGS AFTER LIVE
    # checkSocialTagsAfterLive()

    #8. VALIDATE SOCIAL TAGS IF IT'S EMPTY
    ## False if it's empty. True if it has value.
    # checkIfSocialTagsEmpty()

    #9. CHECK RESPONSE STATUS
    # checkResponseStatus()

    #10. LOAD OLD DATA
    # loadOldData()

    #11. RUN SAMPLE URLs
    # for url in listURLs:
    #     print(getMetaTagsOnly(url))


    print('********************End automation.')
    driver.quit()

