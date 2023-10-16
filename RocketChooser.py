from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from selenium.webdriver.common.keys import Keys #引入keys类操作
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import datetime
import time
import schedule


#executeType = "Debug"
executeType = "Official"
teachers = ["Lovely","Ninja","Dahlia", "Del", "Kimberly", "Courtney"]  #Angelica
#weekdays = [6, 1, 3]    #Monday = 0, Sunday = 6
#weekdays = [1, 3, 6]
weekdays = [3, 1, 6] 
#weekdays = [3, 5, 0]    #選1 4 6
classType = ["L"]
classTime = [" 22:00~22:50"," 21:00~21:50"," 23:00~23:50"]


#一天只會選一堂課

#選課順序:
#1. 老師 => Lovely -> Ninja -> Angelica
#2. 時間 => 22:00 -> 21:00 -> 23:00
#3. 專案 => F -> G -> D
#4. 星期 => 二 -> 四 -> 日

def main():

    if executeType == "Debug":
        StartProcess()
    elif executeType == "Official":        
        schedule.every().friday.at("21:25").do(StartProcess)
        schedule.every().saturday.at("21:25").do(StartProcess)
        
        
def StartProcess():
    print('Start Process')
    weekdayAndDayCountMapping = {0:31, 1:32, 2:33, 3:34, 4:35, 5:29, 6:30}
    courseId = {"D":"233446", "F":"239907","G":"239908", "H":"239909", "I":"240613", "J":"244352", "L":"259603"}            

    if executeType == "Debug":
        dayCounts = [25,29,31]
    elif executeType == "Official":
        dayCounts = GetDayCount(weekdays, weekdayAndDayCountMapping)
        print(dayCounts)

    browser = Login()

    #print('岸上一個月')
    #browser.find_element_by_link_text('下一個月').click()
    #print('岸上一個月結束')
    
    if executeType == "Debug":
        a=""
    elif executeType == "Official":
        CheckIfNotice(browser)
    
    
    
    for dayCount in dayCounts:
        ymd = 'scc' + GetYearMonthDay(dayCount)
        
        print(dayCount)
        clarifyNextMonth(browser, ymd)
        
        if executeType == "Debug":
            a=""
        elif executeType == "Official": 
            CheckTimeToStart()

        if CheckCurrentDayHadBeenChoosen(browser, ymd) == False:
            StartChooseTeacher(browser, ymd, courseId, teachers, classType, classTime, dayCount)

        else:
            print('==========Select next week day==========')
            continue

        print('==========Select next week day==========')

    print('Process end, wait for next trigger')
    

def GetDayCount(weekdays, weekdayAndDayCountMapping):
    print('GetDayCount Start')
    dayCounts = []
    
    if executeType == "Debug":
        currentDay = 4
    elif executeType == "Official":
        currentDay = datetime.date.today().weekday()
    
    for index in range(len(weekdays)):
        if currentDay == 4:
            dayCounts.append(weekdayAndDayCountMapping[weekdays[index]])
        elif currentDay == 5:
            dayCounts.append(weekdayAndDayCountMapping[weekdays[index]] - 1)            

    print('GetDayCount End')
    return dayCounts


def Login():
    print('Login Start')
    browser = webdriver.Chrome()
    browser.get('http://login.hitutor.com.tw/')
    browser.find_element_by_id("t101_email").clear()
    browser.find_element_by_id("t101_email").send_keys("input your account email")
    browser.find_element_by_id("password").clear()
    browser.find_element_by_id("password").send_keys("input your account password")    
    browser.find_element_by_id('login_button').click()
    print('Login End')
    
    time.sleep(25)
    return browser

    
def GetYearMonthDay(dayCount):
    print('GetYearMonthDay Start')
    now = datetime.datetime.now()
    date = now + datetime.timedelta(days = dayCount)
    
    dateString = str(date.date())
    ymd = dateString.split("-")
    year = (ymd[0])[2:4]
    month = ymd[1]
    day = ymd[2]
    print('GetYearMonthDay End')
    
    return year + month + day


def CheckTimeToStart():
    print('CheckTimeToStart Start')

    while True:
        now = datetime.datetime.now()
        startChooseTime = now.replace(hour=21, minute=30, second=15, microsecond=0)

        if now > startChooseTime:
            break

        print('Wait to select class')
        time.sleep(1)
        
    print('CheckTimeToStart End')


def clarifyNextMonth(browser, ymd):
    print('clarifyNextMonth Start')
    
    try:        
        aaa= browser.find_element_by_id(ymd)
        
        print("Element found")
    except NoSuchElementException:        
        browser.find_element_by_link_text('下一個月').click()
        print("No element found, clikc next month")
        time.sleep(20)

    print('clarifyNextMonth End')
    
def CheckCurrentDayHadBeenChoosen(browser, ymd):
    div = browser.find_element_by_id(ymd)
    #print(div.get_attribute('innerHTML'))
    #print(div.get_attribute('textContent'))

    if "取消課程" in div.get_attribute('textContent'):
        print("Current day already had choosen teacher")
        return True
    else:
        return False



def StartChooseTeacher(browser, ymd, courseId, teachers, classType, classTime, dayCount):
    #print(courseId[classType])
    print('StartChooseTeacher Process Start')
    print('Date: ' + ymd)

    isChangeOtherWeekay = False

    
    for cType in classType:
        
        if isChangeOtherWeekay == False:
        
            for cTime in classTime:
                if isChangeOtherWeekay == False:
                
                    s1 = Select(browser.find_element_by_id(ymd + courseId[cType]))
                    s1.select_by_visible_text(cType + cTime)  # 选择text="o3"的值，即在下拉时我们可以看到的文本
                    print('Choose class type: ' + cType + ' and time:' + cTime)
                    time.sleep(1)
                    
                    for teacher in teachers:                        
                        if (teacher == "Del" or teacher == "Courtney" or teacher == "Kimberly" or teacher == "Bridget") and (dayCount == 1 or dayCount == 3):  #只會在禮拜天選擇Del或Courtney，Del和Courtney不會在其他天被選中，若不想加條件可以把這個if刪掉
                            continue
                        else:
                            try:
                                print(teacher)
                                teacherElementName = (browser.find_element_by_link_text(teacher)).get_property("name")
                                browser.find_element_by_link_text(teacher).click()

                                isBlueLinkOrNot = True

                                if "@1" in teacherElementName:
                                    isBlueLinkOrNot = True
                                    time.sleep(1)
                                    browser.find_element_by_class_name("swal2-cancel").click()
                                    time.sleep(1)
                                    alert = browser.switch_to_alert()
                                    time.sleep(1)
                                    
                                    if executeType == "Debug":                            
                                        alert.dismiss()
                                    elif executeType == "Official":
                                        alert.accept()                                        
                                    
                                    #print('Blue and choose ' + teacher)                
                                else:
                                    isBlueLinkOrNot = False
                                    time.sleep(1)    
                                    alert = browser.switch_to_alert()
                                    time.sleep(1)
                                    
                                    if executeType == "Debug":                            
                                        alert.dismiss()
                                    elif executeType == "Official":
                                        alert.accept()
                                        
                                        
                                    #print('Gray and choose ' + teacher)
                                time.sleep(5)
                                
                                print('You choose teacher : ' + teacher + '!!!')
                                isChangeOtherWeekay = True
                                break
                            
                            except NoSuchElementException:
                                print(teacher + " has been choosen, change to next one")
                                continue           
        
    print('StartChooseTeacher Process End')


def CheckIfNotice(browser):    
    print('CheckIfNotice Process Start')
    print('You are now at: ' + browser.current_url)
    
    if "notice" in browser.current_url:        
        python_button = browser.find_elements_by_xpath("//input[@value='確認']")[0]
        python_button.click()

    time.sleep(25)
    print('CheckIfNotice Process End')


main()

if executeType == "Official":
    while True:
        print("Wait to start whole process")
        schedule.run_pending()
        time.sleep(1)


