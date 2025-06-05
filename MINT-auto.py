from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.webdriver.support.ui import Select
import json

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
MY_SPREADSHEET_ID = "19rWkNQf5PuV526-Jom6TjnIKV-8vyl1aDvjMG7GAF2M" #sheet name: SEO metatags request
SHEET_GET_USP_URL = "USP!A2:A" #tab USP
SHEET_GET_USP_TEXT = "USP!B2:B" #tab USP
SHEET_GET_ICON_URL = "Icon List!A2:A" #tab Icon List
SHEET_GET_ICON_TEXT = "Icon List!B2:B" #tab Icon List
SHEET_GET_ALTTEXT_URL = "Feature PDP Alt text!B1" #tab Feature PDP Alt text
SHEET_GET_ALTTEXT_RESULTS = "Feature PDP Alt text!A5:C" #tab Feature PDP Alt text
SHEET_GET_METATAGS = "Metatags!A2:A" #tab Metatags
SHEET_GET_METATAGS_RESULTS = "Metatags!B2:K" #tab Metatags
SHEET_GET_GALLERY_ALTTEXT_URL = "Gallery Alt text!B1" #tab Gallery Alt text
SHEET_GET_GALLERY_ALTTEXT_RESULTS = "Gallery Alt text!A5:C" #tab Gallery Alt text
SHEET_LIST_GALLERY_URLS = "List of galleries alt text!A2:A" #tab List of galleries alt text
SHEET_LIST_GALLERY_FILES = "List of galleries alt text!B2:C" #tab List of galleries alt text
SHEET_LIST_GALLERY_SKUs = "Galleries from SKU!A2:A" #tab Galleries from SKU
SHEET_LIST_GALLERY_SKU_FILES = "Galleries from SKU!B2:C" #tab Galleries from SKU
SHEET_LIST_SKU_URLS = "Get SKUs!A2:A" #tab Get SKUs
SHEET_LIST_SKU_RESULTS = "Get SKUs!B2:C" #tab Get SKUs
SHEET_REG_SKU_URLS = "Get URL from SKU!A2:A" #tab Get URL from SKU
SHEET_REG_SKU_RESULTS = "Get URL from SKU!B2:C" #tab Get URL from SKU
SHEET_SPECS_URLS = "Specs!A2:A" #tab Get URL from SKU
SHEET_SPECS_RESULTS = "Specs!B2:G" #tab Get URL from SKU
SHEET_SPECS_ACACP_RESULTS = "Specs!B2:O" #tab Get URL from SKU
SHEET_TOPFLAG = "Top Flag!A2:F" #Get info for SKUs, Type, Text & Date, AEM username
SHEET_TOPFLAG_RESULTS = "Top Flag!G2:I" #Results for Top Flag implementation

####################### CHECKLIST#####################################
cookie_loggin = {
                "name": "JSESSIONID",
                "value": "D2163C5F71172712DFEFA4671A17CC4C"
                }
####################### end CHECKLIST##################################
WMC = 'https://wds.samsung.com/'
WMC_LoggedIn_Succeed = 'https://wds.samsung.com/wds/sso/login/ssoLoginSuccess.do'
SITECODE = 'vn'
FLATFORM = 'B2C'
PIM_B2C_URL = 'https://p6-ap-author.samsung.com/pim/b2c/product/detail/main/page/list'
PIM_B2B_URL = 'https://p6-ap-author.samsung.com/bim/b2b/product/detail/main/page/list'

SMARTDEVICES_CHARS = '-sm-'
driver = webdriver.Chrome()

######################## DEFINE FUNCTIONS #############################
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

def openQAauthentication():
    QA_authen_link = driver.find_element(By.CSS_SELECTOR, '.wcmMenuTopWrap .wcmMenuTop dl:nth-of-type(4) dd:first-of-type a')
    if (QA_authen_link.text == 'QA'):
        QA_authen_link.click()
        time.sleep(5)
        return True
    else:
        print('QA authentication link is not found on AEM.')
        return False

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

def updateToGoogleSheet(sheetRange, values):
    creds = getGoogleSheetCredential() #get credential
    try:
        print('Writing to google sheet...')
        service = build("sheets", "v4", credentials=creds)
        body = {"values": values}
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=MY_SPREADSHEET_ID,
                range=sheetRange,
                valueInputOption='USER_ENTERED',
                body=body
            )
            .execute()
        )
        print('Done writing to google sheet.')

    except HttpError as error:
        print(f"Writing to google sheet got errors: {error}")
        return error

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


def goGetUSPtext(url):
   driver.get(url)
   USPlist = driver.find_elements(By.CSS_SELECTOR, '.dot-list .dot-list__item')
   if (len(USPlist) > 0):
        resutls = []
        for item in USPlist:
                resutls.append(item.text)
        return ["\n".join(resutls)]
   else:
        return ['N/A']

def getUSP():
    print('Start getting USP text...')
    sheetdata = openGSheetTab(SHEET_GET_USP_URL)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            results = []
            for row in sheetdata:
               url = row[0]
               uspText = goGetUSPtext(url)
               results.append(uspText)
               print(uspText)
               updateToGoogleSheet(SHEET_GET_USP_TEXT, results)
               print(f'Done getting USP for {url}')

    print('Done getting USP text')

def goGetIcontext(url):
    driver.get(url)
    iconlist = driver.find_elements(By.CSS_SELECTOR, '.product-summary__list-item-text span')
    if (len(iconlist) > 0):
        resutls = []
        for item in iconlist:
                resutls.append(item.text)
        return ["\n".join(resutls)]
    else:
        return ['N/A']

def getIconText():
    print('Start getting Icon text...')
    sheetdata = openGSheetTab(SHEET_GET_ICON_URL)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            results = []
            for row in sheetdata:
               url = row[0]
               iconText = goGetIcontext(url)
               results.append(iconText)
               print(iconText)
               updateToGoogleSheet(SHEET_GET_ICON_TEXT, results)
               print(f'Done getting Icon text for {url}')

    print('Done getting Icon text')

def scrollToBottom():
    driver.execute_script("window.scrollTo(0, 0);") #Go to top of page
    SCROLL_PAUSE_TIME = 6 #How long to wait between scrolls
    while True:
        previous_scrollY = driver.execute_script('return window.scrollY')
        driver.execute_script('window.scrollBy( 0, 400 )' ) #Alternative scroll, a bit slower but reliable
        html = driver.find_element(By.TAG_NAME, 'html')
        html.send_keys(Keys.PAGE_DOWN)
        html.send_keys(Keys.PAGE_DOWN)
        html.send_keys(Keys.PAGE_DOWN) #Faster scroll, inelegant but works (Could translate to value scroll like above)
        time.sleep(SCROLL_PAUSE_TIME) #Give images a bit of time to load by waiting

        # Calculate new scroll height and compare with last scroll height
        if previous_scrollY == driver.execute_script('return window.scrollY'):
            time.sleep(SCROLL_PAUSE_TIME) #Give images a bit of time to load by waiting
            break

def getAltinList(imgList):
    results = []
    if len(imgList):
        for img in imgList:
            imgItem = []
            src = img.get_attribute('src')
            if src:
                alttext = img.get_attribute('alt')
                imgFullURL = src.split('?')
                imgURL = imgFullURL[0]
                imgItem.append(imgURL)
                imgItem.append(alttext)
                imgPreview = f"=HYPERLINK(\"{imgURL}\",IMAGE(\"{imgURL}\"))"
                imgItem.append(imgPreview)
                results.append(imgItem)

    return results


def goGetAltText(url):
    driver.get(url)
    time.sleep(2)
    scrollToBottom()
    time.sleep(5)
    results = []
    imageList1 = driver.find_elements(By.CSS_SELECTOR, ".product-summary__list-item img.image__main")
    imageList2 = driver.find_elements(By.CSS_SELECTOR, ".ftd14-key-feature-icon__column img:first-child")
    imageList3 = driver.find_elements(By.CSS_SELECTOR, "div[class^='feature-benefit'] img:first-child")
    imageList4 = driver.find_elements(By.CSS_SELECTOR, ".ftd16-interactive-multi-feature img:first-child")
    imageList5 = driver.find_elements(By.CSS_SELECTOR, ".three-column-carousel img.image__main")
    imageList6 = driver.find_elements(By.CSS_SELECTOR, ".two-column img:first-child")
    imageList7 = driver.find_elements(By.CSS_SELECTOR, ".ftd15-interactive-single-feature img:first-child")

    rs1 = getAltinList(imageList1)
    rs2 = getAltinList(imageList2)
    rs3 = getAltinList(imageList3)
    rs4 = getAltinList(imageList4)
    rs5 = getAltinList(imageList5)
    rs6 = getAltinList(imageList6)
    rs7 = getAltinList(imageList7)
    results = rs1 + rs2 + rs3 + rs4 + rs5 + rs6 + rs7

    finalRs = []
    [finalRs.append(x) for x in results if x not in finalRs]
    print(f'Number of images: {len(finalRs)}')

    if len(finalRs) == 0: #Neu khong co images nao`
        finalRs.append([0, 0, 0])

    return finalRs

def getAltText():
    print('Start getting Alt text...')
    sheetdata = openGSheetTab(SHEET_GET_ALTTEXT_URL)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            url = sheetdata[0][0] # Chi lay co 1 cell thoi
            results = goGetAltText(url)
            updateToGoogleSheet(SHEET_GET_ALTTEXT_RESULTS, results)
            print('Done getting Alt text...')

def goGetMetatags(url):
    driver.get(url)
    time.sleep(3)
    titleElement = driver.find_element(By.XPATH, "//meta[@name='title']")
    descElement = driver.find_element(By.XPATH, "//meta[@name='description']")
    twitterCard= driver.find_element(By.XPATH, "//meta[@name='twitter:card']")
    twitterSite= driver.find_element(By.XPATH, "//meta[@name='twitter:site']")
    twitterCreator= driver.find_element(By.XPATH, "//meta[@name='twitter:creator']")
    twitterTitle= driver.find_element(By.XPATH, "//meta[@name='twitter:title']")
    twitterDesc= driver.find_element(By.XPATH, "//meta[@name='twitter:description']")
    ogTitle = driver.find_element(By.XPATH, "//meta[@property='og:title']")
    ogDesc = driver.find_element(By.XPATH, "//meta[@property='og:description']")
    kw = driver.find_element(By.XPATH, "//meta[@name='keywords']")
    pageMetaTags = {

        'title' : titleElement.get_attribute('content'),
        'description' : descElement.get_attribute('content'),
        'twitterCard' : twitterCard.get_attribute('content'),
        'twitterSite' : twitterSite.get_attribute('content'),
        'twitterCreator' : twitterCreator.get_attribute('content'),
        'twitterTitle' : twitterTitle.get_attribute('content'),
        'twitterDesc' : twitterDesc.get_attribute('content'),
        'ogTitle' : ogTitle.get_attribute('content'),
        'ogDesc' : ogDesc.get_attribute('content'),
        'kw' : kw.get_attribute('content')
    }

    return pageMetaTags

def getMetatags():
    print('Start getting meta tags...')
    sheetdata = openGSheetTab(SHEET_GET_METATAGS)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            results = []
            for row in sheetdata:
               url = row[0]
               metatags = goGetMetatags(url)
               title = metatags['title']
               description = metatags['description']
               twitterCard = metatags['twitterCard']
               twitterSite = metatags['twitterSite']
               twitterCreator = metatags['twitterCreator']
               twitterTitle = metatags['twitterTitle']
               twitterDesc = metatags['twitterDesc']
               ogTitle = metatags['ogTitle']
               ogDesc = metatags['ogDesc']
               kw = metatags['kw']

               results.append([title, description, twitterCard, twitterSite, twitterCreator, twitterTitle, twitterDesc, ogTitle, ogDesc, kw])
               updateToGoogleSheet(SHEET_GET_METATAGS_RESULTS, results)
               print(f'Done getting meta tags for {url}')

    print('Done getting meta tags.')

def goGetGalleryAltText(url):
    driver.get(url)
    time.sleep(3)

    iList1 = driver.find_elements(By.CSS_SELECTOR, '.pd-header-gallery__thumbnail-item .image') #div.image
    iList2 = driver.find_elements(By.CSS_SELECTOR, '.pdd-header-gallery__item>div:first-child') #for B2B url
    iList = iList1 + iList2
    print(f"Number of images: {len(iList)}")
    myImages = []
    if len(iList): #Neu co images trong Gallery
        httpString = 'https:'
        for i in iList:
            imgItem = []
            child = i.find_element(By.CSS_SELECTOR, 'img:first-child')
            alt = child.get_attribute('data-alt') or child.get_attribute('alt')
            src = child.get_attribute('data-src') or child.get_attribute('src') or child.get_attribute('srcset') #srcset: B2B url
            print(src)
            if not src.startswith(httpString):
                src = httpString + src
            imgFullURL = src.split('?')
            imgURL = imgFullURL[0]

            imgItem.append(imgURL)
            imgItem.append(alt)
            imgPreview = f"=HYPERLINK(\"{imgURL}\",IMAGE(\"{imgURL}\"))"
            imgItem.append(imgPreview)

            myImages.append(imgItem)

    else: #Neu KHONG CO images trong Gallery
        myImages.append([0, 0, 0])

    return myImages

def goToGetGalleryAltText(url): #co them column SKU
    driver.get(url)
    time.sleep(3)
    skuEl = driver.find_element(By.CLASS_NAME,'pd-info__sku-code')
    sku = skuEl.text
    iList1 = driver.find_elements(By.CSS_SELECTOR, '.pd-header-gallery__thumbnail-item .image') #div.image
    iList2 = driver.find_elements(By.CSS_SELECTOR, '.pdd-header-gallery__item>div:first-child') #for B2B url
    iList = iList1 + iList2
    print(f"Number of images: {len(iList)}")
    myImages = []
    if len(iList): #Neu co images trong Gallery
        httpString = 'https:'
        for i in iList:
            imgItem = []
            child = i.find_element(By.CSS_SELECTOR, 'img:first-child')
            alt = child.get_attribute('data-alt') or child.get_attribute('alt')
            src = child.get_attribute('data-src') or child.get_attribute('src') or child.get_attribute('srcset') #srcset: B2B url
            # print(src)
            if not src.startswith(httpString):
                src = httpString + src
            imgFullURL = src.split('?')
            imgURL = imgFullURL[0]

            imgItem.append(imgURL)
            imgItem.append(alt)
            imgItem.append(sku)

            myImages.append(imgItem)


    else: #Neu KHONG CO images trong Gallery
        myImages.append([0, 0, 0])

    return myImages


def getGalleryAltText():
    print('Start getting Gallery Alt text...')
    sheetdata = openGSheetTab(SHEET_GET_GALLERY_ALTTEXT_URL)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            url = sheetdata[0][0] # Chi lay co 1 cell thoi
            results = goGetGalleryAltText(url)
            # print(results)
            updateToGoogleSheet(SHEET_GET_GALLERY_ALTTEXT_RESULTS, results)
            print('Done getting Gallery Alt text...')

def saveDataToFile(altData, name):
    print('Start saving data to file...')
    df = pd.DataFrame(altData)
    df.columns = ["Image URL", "Alt text", "Image preview"]
    name = name.replace('/','-')
    df.to_excel(f"./export files/{name}.xlsx", columns=['Image URL', 'Alt text'] , index=False)
    print('Saved successfully!')

def saveDataToFileExcel(altData, name): # this is only a request from Leo (added column SKU)
    print('Start saving data to file...')
    df = pd.DataFrame(altData)
    df.columns = ["Image URL", "Alt text", "SKU"]
    filepath= f"./export files/{name}.xlsx"

    isFileExist = os.path.isfile(filepath)
    if isFileExist:
        df_existing = pd.read_excel(filepath)
        df_combined = pd.concat([df_existing, df]) # dung concat, khong dung append
        with pd.ExcelWriter(filepath, mode='a', if_sheet_exists='replace') as writer:
            df_combined.to_excel(writer, sheet_name = 'Sheet1', index=False)

    else:
        df.to_excel(filepath, index=False)

    print('Saved successfully!')

def getSKUFeaturePage(url):
    try:
        driver.get(url)
        time.sleep(3)
        sku = driver.find_element(By.CLASS_NAME, 'pd-info__sku-code').text
    except Exception as e:
        sku = 'N/A'
    return sku

def listOfGalleries():
    print('Start getting List of Gallery Alt text...')
    sheetdata = openGSheetTab(SHEET_LIST_GALLERY_URLS)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            fileNames = []
            for row in sheetdata:
                url = row[0]
                sku = getSKUFeaturePage(url)
                if (sku != 'N/A'):
                    results = goGetGalleryAltText(url)
                    saveDataToFile(results, sku)
                    file = sku.replace('/', '-') + '.xlsx'
                    fileNames.append([sku, file])
                else: #sku = 'N/A' if not found
                    fileNames.append([sku, sku])
                    print("This page doesn't have SKU")

                updateToGoogleSheet(SHEET_LIST_GALLERY_FILES, fileNames)

            print('Done getting List of Gallery Alt text...')

def isSmartDevices(pageURL):
    return SMARTDEVICES_CHARS in pageURL

def isBuyPage(pageURL):
    if ('/buy/' in pageURL):
        return True
    return False

def listOfSKUs():
    print('Start getting SKUs...')
    sheetdata = openGSheetTab(SHEET_LIST_SKU_URLS)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
       canOpenQA = openQAauthentication()
       if canOpenQA:
            driver.switch_to.new_window('tab')
            time.sleep(1)
            skuList = []
            sku = ''
            isBuyPg = None
            for row in sheetdata:
                url = row[0]

                if (isSmartDevices(url)):
                    skuText = url.split(SMARTDEVICES_CHARS)[1]
                    sku = skuText[:11] #Lay 11 ki tu
                    sku = 'SM-' + sku.upper()
                    if (isBuyPage(url)):
                        isBuyPg = 'Buy page'
                    else:
                        isBuyPg = None

                else:
                    sku = getSKUFeaturePage(url)

                skuList.append([sku, isBuyPg])
                updateToGoogleSheet(SHEET_LIST_SKU_RESULTS, skuList)

            print('Done getting SKUs.')

def isB2C():
    if FLATFORM == 'B2C':
        return True
    else:
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

def getQAlink(sku):
    if (isB2C()): #B2C flatform
        driver.get(PIM_B2C_URL)
    else: #B2B flatform
        driver.get(PIM_B2B_URL)

    time.sleep(3)

    #set Sitecode value
    siteCode_dropdown = Select(driver.find_element(By.ID, 'searchSiteCodeList'))
    siteCode_dropdown.select_by_value(SITECODE)

    #reset Date
    btnReset = driver.find_element(By.ID, 'btnDateReset')
    btnReset.click()

    #click Model
    model_toggle = driver.find_element(By.ID, 'headingModel')
    model_toggle.click()

    # Setup wait for later
    wait = WebDriverWait(driver, 5)

    #input SKU to search
    skuElement = wait.until(EC.visibility_of_element_located((By.ID, 'txtInquiryModel')))
    skuElement.send_keys(sku)

    #hit Search button
    searchBtn = driver.find_element(By.ID, 'btnSearch')
    searchBtn.click()
    print('hit Search done')

    time.sleep(3)

    # SHOULD CHECK IF SKU IS NOT FOUND IN RESULTS

    #click on Family Name
    btnFamilyName = driver.find_element(By.CLASS_NAME, 'btnFamilyName')
    ActionChains(driver).move_to_element(btnFamilyName).perform()

    #click View
    btnFamilyDetail = driver.find_element(By.CLASS_NAME, 'btnFamilyDetail')
    btnFamilyDetail.click()

    time.sleep(3)

    html = driver.find_element(By.TAG_NAME, 'html')
    html.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)

    #table results
    tableModelUrlList = driver.find_elements(By.CSS_SELECTOR, '#tableModelUrlList tr')
    numberProducts = len(tableModelUrlList)
    familyURLs = {}

    for row in tableModelUrlList:
        modelCodeEl = row.find_element(By.ID, 'modelCode')
        skuCode = modelCodeEl.text
        if (skuCode.endswith('Rep.')):
            skuCode = skuCode.replace('Rep.', '')

        modelUrlEl = row.find_element(By.ID, 'modelUrl')
        linkFound = modelUrlEl.text
        qaLink = 'https://p6-qa.samsung.com' + linkFound
        familyURLs[skuCode] = qaLink

    results = []
    sku = sku.upper()
    itemQaLink = familyURLs[sku]
    if numberProducts == 1:
        results.append([f'{itemQaLink}', 'N/A'])
    else:
        listFamily = []
        for x in familyURLs.values():
            if (x != itemQaLink):
                listFamily.append(x)

        familyURLsValues = "\n".join(listFamily)
        results.append([f'{itemQaLink}', f'{familyURLsValues}'])

    return results

def getQAlinkFromSKU():
    print('Start getting QA link from SKU...')
    sheetdata = openGSheetTab(SHEET_REG_SKU_URLS)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()

    if canStartAutomation:
       canOpenQA = openQAauthentication()
       driver.switch_to.window(driver.window_handles[1]) # tab WMC
       time.sleep(2)
       canOpenSiteAuthen = openSitesauthentication()

       if (canOpenQA and canOpenSiteAuthen):
            driver.switch_to.new_window('tab')
            time.sleep(1)
            results = []
            for row in sheetdata:
                sku = row[0]
                qaLinkSet = getQAlink(sku)
                results.append(qaLinkSet[0])

                print(results)
                print('----')
                updateToGoogleSheet(SHEET_REG_SKU_RESULTS, results)

            print('End getting QA link from SKU.')

def getPDPurlFromSKU(sku):
    import requests

    url = f"https://searchapi.samsung.com/v6/front/b2c/product/card/detail/global?siteCode=vn&modelList={sku}&saleSkuYN=N&onlyRequestSkuYN=N&keySummaryYN=N&keySpecYN=N&quicklookYN=N"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    responseData = json.loads(response.text)
    resultData = responseData['response']['resultData']
    productList = resultData['productList']
    modelList = productList[0]['modelList']
    for item in modelList:
        if (item['modelCode'] == sku):
            originPdpUrl = item['originPdpUrl']
            if (SMARTDEVICES_CHARS in originPdpUrl):
                return 'https://www.samsung.com' + originPdpUrl + 'buy/'
            else:
                return 'https://www.samsung.com' + originPdpUrl


def getGalleriesFromSKU(category): #category = excel filename
    print('Start getting Galleries from SKU...')
    sheetdata = openGSheetTab(SHEET_LIST_GALLERY_SKUs)
    fileNames = []
    for row in sheetdata:
        sku = row[0]
        originPdpUrl = getPDPurlFromSKU(sku)
        results = goToGetGalleryAltText(originPdpUrl)
        saveDataToFileExcel(results, category)
        file = f'{category}.xlsx' # file name
        fileNames.append([originPdpUrl, file])

        updateToGoogleSheet(SHEET_LIST_GALLERY_SKU_FILES, fileNames)


    print('End getting Galleries from SKU.')

def addValueToSpec():
    print('ok')

def goGetSpecsInfo(productType, url):
    driver.get(url)
    time.sleep(2)
    specAnchor = driver.find_element(By.CSS_SELECTOR, '#anchor_pd-g-product-specs a')
    specAnchor.click()
    viewMoreBtn = driver.find_element(By.CSS_SELECTOR, '.spec-highlight__button')
    viewMoreBtn.click()
    time.sleep(1)
    specContainer = driver.find_element(By.CSS_SELECTOR, '.spec-highlight__container')
    specItems = specContainer.find_elements(By.CSS_SELECTOR, '.spec-highlight__list .spec-highlight__item')
    tempDict = {}

    for item in specItems:
        itemTitle = item.find_elements(By.CSS_SELECTOR, '.spec-highlight__title')
        if(itemTitle != []):
            itemTitle = item.find_element(By.CSS_SELECTOR, '.spec-highlight__title')
            # print(itemTitle.text)
            itemValue = item.find_element(By.CSS_SELECTOR, '.spec-highlight__value')
            # print(itemValue.text)
            tempDict[itemTitle.text] = itemValue.text

        else:
            continue

    tvCollection = ['Resolution', 'Refresh Rate', 'Anti Reflection', 'Picture Engine', 'Dolby Atmos', 'Design'] #6 labels
    monitorsCollection = ['Screen Size (Class)', 'Resolution', 'Frame Rate', 'HDMI', 'USB-C', 'HAS(Height Adjustable Stand)'] #6 labels
    acacpCollection = ['CADR (㎥/h)', 'Cooling [Btu/h]', 'Capacity (Cooling, Btu/hr)','Net Dimension', 'Net Dimension (WxHxD, ㎜*㎜*㎜)', 'Net Dimension (Indoor, WxHxD, ㎜*㎜*㎜)','Net Dimensions (WxHxD) (mm)','Indicator (Cleanliness)', 'Mode (WindFree™)', 'Power Consumption(W)', 'Power Consumption(Cooling, W)','Power Consumption','SmartThings App Support', 'SmartThings'] #14 labels
    refCollection = ['Net Total(Liter)', 'Cooling Type', 'Number of Shelf (Total)',	'Compressor']
    vcCollection = ['Number of Cleaning Modes', 'Water Tank Capacity', 'Dust Capacity', 'Consumption Power', 'Max Consumption Power', 'Wi-fi Control', 'LiDAR Sensor']
    cookingAppCollection = ['Product Type','Oven Capacity','Output Power (Microwave)','Power Consumption (Grill)','Various Cooking Mode','Quick Guide Label']
    wmCollection = ['Washing Capacity (kg)','Drying Capacity (kg)','Spin Speed','Smart Control','AI Control','Net Dimension (WxHxD)']


    # print(tempDict)

    if(productType == 'TV'):
        return getSpecValues(tvCollection, tempDict)
    elif (productType == 'MONITOR'):
        return getSpecValues(monitorsCollection, tempDict)
    elif (productType == 'ACACP'):
        return getSpecValues(acacpCollection, tempDict)
    elif (productType == 'REF'):
        return getSpecValues(refCollection, tempDict)
    elif (productType == 'VCs'):
        return getSpecValues(vcCollection, tempDict)
    elif (productType == 'CookingApp'):
        return getSpecValues(cookingAppCollection, tempDict)
    elif (productType == 'WMs'):
        return getSpecValues(wmCollection, tempDict)

def getSpecValues(collection, valueDict):
    results = []
    for val in collection:
        valSpec = valueDict.get(val)
        if(valSpec):
            results.append(valSpec)
        else:
            results.append('N/A')
    return results

def listPDspecs(productType):
    print('Start getting Specs info...')
    sheetdata = openGSheetTab(SHEET_SPECS_URLS)
    driver.switch_to.new_window('tab')
    time.sleep(1)

    results = []
    for row in sheetdata:
        url = row[0]
        specsInfoRslt = goGetSpecsInfo(productType, url)
        results.append(specsInfoRslt)
        if (productType == 'ACACP'):
            updateToGoogleSheet(SHEET_SPECS_ACACP_RESULTS, results)
        else:
            updateToGoogleSheet(SHEET_SPECS_RESULTS, results)
        print(f'Done getting specs for {url}')

    print('Done getting Specs info.')

def searchSKUinPIM(firstRow, sku):
    if (isB2C()): #B2C flatform
        driver.get(PIM_B2C_URL)
    else: #B2B flatform
        driver.get(PIM_B2B_URL)

    time.sleep(3)

    #set Sitecode value
    siteCode_dropdown = Select(driver.find_element(By.ID, 'searchSiteCodeList'))
    siteCode_dropdown.select_by_value(SITECODE)
    time.sleep(2)

    # Setup wait for later
    wait = WebDriverWait(driver, 5)

    #reset Date
    btnDateReset = driver.find_element(By.ID, 'btnDateReset')
    btnDateReset.click()
    # ActionChains(driver).move_to_element(btnDateReset).click().perform()
    time.sleep(2)

    #click Model
    model_toggle = driver.find_element(By.ID, 'headingModel')
    model_toggle.click()
    time.sleep(2)

    #input SKU to search
    # skuElement = wait.until(EC.visibility_of_element_located((By.ID, 'txtInquiryModel')))
    skuElement = driver.find_element(By.ID, 'txtInquiryModel')
    skuElement.send_keys(sku)
    time.sleep(2)

    #hit Search button
    searchBtn = driver.find_element(By.ID, 'btnSearch')
    searchBtn.click()
    # ActionChains(driver).move_to_element(searchBtn).click().perform()
    time.sleep(5)

    if (firstRow):
        btnDateReset = driver.find_element(By.ID, 'btnDateReset')
        ActionChains(driver).move_to_element(btnDateReset).click().perform()
        time.sleep(2)

        searchBtn = driver.find_element(By.ID, 'btnSearch')
        ActionChains(driver).move_to_element(searchBtn).click().perform()
        searchBtn.click()

        time.sleep(5)

    print('hit Search done')


def doDirectUpdate(sku, topFlagType, customText, AstartDate, BendDate):
    print('doing Direct update...')
    # Store the ID of the original window
    original_window = driver.current_window_handle

    # Store the number of windows currently open
    windows_before = driver.window_handles

    btnFamilyName = driver.find_element(By.CLASS_NAME, 'btnFamilyName')
    ActionChains(driver).move_to_element(btnFamilyName).perform()
    btnDirectUpdate = driver.find_element(By.CLASS_NAME, 'btnDirectUpdate')
    ActionChains(driver).key_down(Keys.CONTROL).click(btnDirectUpdate).key_up(Keys.CONTROL).perform()

    # # Wait for the new window/popup to appear
    # timeout = 5
    # start_time = time.time()
    # while len(driver.window_handles) == len(windows_before):
    #     if time.time() - start_time > timeout:
    #         raise Exception("Popup window did not appear!")
    #     time.sleep(0.1)

    # # Switch to the new window
    # new_window = [window for window in driver.window_handles if window != original_window][0]
    # driver.switch_to.window(new_window)

    # Now handle the new tab
    # Wait for the new tab to open
    wait = WebDriverWait(driver, 5)
    wait.until(lambda d: len(d.window_handles) > 1)

    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[5])

    time.sleep(3)

    #input request title
    requestTitle = driver.find_element(By.ID, 'requestTitle')
    requestTitle.click()

    #input request description
    requestContent = driver.find_element(By.ID, 'requestContent')
    requestContent.send_keys('Implement Top Flag')

    time.sleep(2)

    #btnRequest
    btnRequest = driver.find_element(By.ID, 'btnRequest')
    btnRequest.click()

    time.sleep(20)
    # When done with the popup, close it and switch back
    # driver.close()
    # driver.switch_to.window(original_window)

    # Switch to the PIM tab
    driver.switch_to.window(driver.window_handles[4])
    time.sleep(10)

    executeTopFlag(sku, topFlagType, customText, AstartDate, BendDate)

def scrollToBottomPage():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def executeTopFlag(sku, topFlagType, customText, AstartDate, BendDate):
    print('implementing top flag...')
    print(f"current window title is {driver.title}")

    tabModelManagement = driver.find_element(By.CSS_SELECTOR, 'div#TABS li:nth-of-type(4) a')
    tabModelManagement.click()

    # Wait for the alert to be present (timeout after 10 seconds)
    wait = WebDriverWait(driver, 10)
    alert = wait.until(EC.alert_is_present())
    time.sleep(1)

    # Now you can interact with the alert:
    alert.dismiss() #hit Cancel

    time.sleep(5)

    print(f"current windown title is {driver.title}")

    html = driver.find_element(By.TAG_NAME,'html')
    html.send_keys(Keys.END)
    # scrollToBottomPage()
    # from selenium.common.exceptions import TimeoutException
    # try:
    #     searchInput = wait.until(EC.visibility_of_element_located((By.ID, "searchInput")))
    #     print('element found')
    # except TimeoutException:
    #     print("Element not found within timeout period!")

    #search sku
    time.sleep(2)
    # searchInput = driver.find_element(By.ID, 'searchInput')
    # searchInput.send_keys(sku)

    #
    # driver.execute_script("arguments[0].scrollIntoView(true);", searchInput)
    # Add a small wait to ensure it's ready after scrolling
    # time.sleep(0.5)
    # searchInput = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "searchInput")))
    # ActionChains(driver).move_to_element(searchInput).perform()
    # ActionChains(driver).move_to_element(searchInput).send_keys(sku).perform()
    skuModels = driver.find_elements(By.CSS_SELECTOR, '#gridmodelCode > span:first-child')
    for x in skuModels:
        if (x.text == sku):
            x.click()


    # testCategory = driver.find_element(By.CSS_SELECTOR, '.drop-category > p:first-child')
    # testCategory.click()

    # searchInput.send_keys(sku)
    time.sleep(1)

    # btnSearch = driver.find_element(By.ID, 'btnSearch')
    # btnSearch.click()
    # time.sleep(5)

    #click sku in new tab
    # modelCode = driver.find_element(By.CSS_SELECTOR, '#gridmodelCode span:first-child')
    # ActionChains(driver).key_down(Keys.CONTROL).click(modelCode).key_up(Keys.CONTROL).perform()
    # time.sleep(5)

    #switch to new tab
    # driver.switch_to.window(driver.window_handles[5])
    # time.sleep(10)
    # print(f"current window title is {driver.title}")
    time.sleep(50)
    #hit Additional Info



    #Fill top flag area

    #Hit Save

    #close current window

    # close driver


def doMyDirectUpdate(sku, topFlagType, customText, AstartDate, BendDate):
    print('doing my own workflow')
    btnFamilyName = driver.find_element(By.CLASS_NAME, 'btnFamilyName')
    ActionChains(driver).move_to_element(btnFamilyName).perform()
    btnDirectUpdate = driver.find_element(By.CLASS_NAME, 'btnDirectUpdate')
    btnDirectUpdate.click()

    time.sleep(10)

    executeTopFlag(sku, topFlagType, customText, AstartDate, BendDate)

def implementTopFlag(firstRow, sku, topFlagType, customText, AstartDate, BendDate, aemUsername):
    #1. search SKU
    searchSKUinPIM(firstRow, sku)

    tblResult = driver.find_element(By.CLASS_NAME, 'table-sortable')
    rows = tblResult.find_elements(By.TAG_NAME, 'tr')
    rows_count = len(rows)
    results = []
    if rows_count <= 1:
        #1.1 if not found
        results.extend(['N/A', 'N/A', 'SKU not found'])
    else:
        #1.2 if found
        if (rows_count <= 3): #chi tim duoc 1 hoac 2 SKU (va 1 row hidden)
            dataResults = tblResult.find_elements(By.CSS_SELECTOR, '#table-sortable tr:nth-of-type(2) td')
            skuRequestBy = skuWorkflow = skuDisplay = ''
            for td in dataResults:
                skuAttribute = td.get_attribute('aria-describedby')

                if (skuAttribute == 'table-sortable_Family Display'):
                    skuDisplay = td.text
                    if (skuDisplay == 'N'):
                        #display No
                        results.extend(['N/A', 'N/A', 'SKU is displaying as No'])
                        break

                elif (skuAttribute == 'table-sortable_lastWorkValue'):
                    skuWorkflow = td.text

                elif (skuAttribute == 'table-sortable_Request By'):
                    skuRequestBy = td.text

            if (skuWorkflow == 'Completed' and skuDisplay == 'Y'):
                #workflow completed. We can start Direct update
                doDirectUpdate(sku, topFlagType, customText, AstartDate, BendDate)

            elif (skuWorkflow == 'In Progress'):
                if(skuRequestBy == aemUsername):
                    #workflow of myself
                    doMyDirectUpdate(sku,topFlagType, customText, AstartDate, BendDate)
                else:
                    #workflow in progress by someone
                    results.extend(['N/A', 'N/A', f'Workflow is In Progress by {skuRequestBy}'])

        else:
            #tim duoc nhieu results
            results.extend(['N/A', 'N/A', 'Many SKUs found'])

    return results

def doTopFlag():
    print('Start doing Top Flag...')
    sheetdata = openGSheetTab(SHEET_TOPFLAG)
    driver.switch_to.new_window('tab')
    time.sleep(1)
    canStartAutomation = openAEM()
    if canStartAutomation:
        canOpenQA = openQAauthentication()
        driver.switch_to.window(driver.window_handles[1]) # tab WMC
        time.sleep(2)
        canOpenSiteAuthen = openSitesauthentication()

        if (canOpenQA and canOpenSiteAuthen):
            driver.switch_to.new_window('tab')
            time.sleep(1)
            results = []

            for index, row in enumerate(sheetdata):
                firstRow = False
                # if( index == 0): firstRow = True
                print(f"is firstRow: {firstRow}")
                sku = row[0]
                topFlagType = row[1]
                customText = row[2]
                startDate = row[3]
                endDate = row[4]
                aemUsername = row[5]
                skuImplementStatus = implementTopFlag(firstRow, sku, topFlagType, customText, startDate, endDate, aemUsername)
                print(f"skuImplementStatus: {skuImplementStatus}")
                results.append(skuImplementStatus)
                updateToGoogleSheet(SHEET_TOPFLAG_RESULTS, results)

    print('End doing Top Flag.')

######################## end DEFINE FUNCTIONS #############################

if __name__ == '__main__':
    # getUSP()
    # getIconText()
    # getAltText() #Alt text of Feature images
    getMetatags()
    # getGalleryAltText() #gallery for just 1 page
    # listOfGalleries() #galleries for many pages and save to Excel files
    # listOfSKUs() #get SKU for list of pages
    # getQAlinkFromSKU() #get QA link (and its family) from SKU. Check Sitecode and Platform before running.
    # getGalleriesFromSKU('CE') #get Galleries from SKU list. All images urls are put in the same file with different SKU column.
    # listPDspecs('WMs') #TV, MONITOR, ACACP, REF, VCs, CookingApp, WMs
    # doTopFlag() #implement top flag

    print('********************End automation.')
    driver.quit()