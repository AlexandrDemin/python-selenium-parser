from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import date
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


driver = webdriver.Chrome()
driver.get("http://www.zakupki.rosatom.ru/Web.aspx?node=currentorders&ostate=P")

#ищу ссылку для открытия формы фильтрации
elem = driver.find_element_by_id("control-filter-lots")
elem.click()

#fieldPriceMin = driver.find_element_by_id("price-min")
#fieldPriceMin.send_keys("100000000")

#определяю текущую дату
dtnow = date.today().strftime("%d.%m.%Y")
dtnow = "25.03.2019" #тестовая дата

#заполняю дату
fieldDate = driver.find_element_by_name("ctl09$ctl06$ctl02$dps$txtDate")
fieldDate.send_keys(dtnow)

#нажимаю поиск
btnSearch = driver.find_element_by_name("ctl09$ctl06$ctl02$bSearch")
btnSearch.click()

page=1
curString=1

#бегаем по всем страницам
#if page==1 : 

#выбираем все строки на странице
#field1 = driver.find_element_by_xpath("/html/body/form[@id='form1']/div[@class='wrapper']/div[@class='body body-inner']/div[@class='body-column body-column-right content']/div[@id='table-lots-list']/table/tbody/tr[@class='even'][1]/td[@class='description']/p[2]/a") #
btns = driver.find_elements_by_xpath("//td[@class='control']/img[@class='btm']")
for t in range(len(btns)):
    btns[t].click()

nums = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='description']/p[1]")
links = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='description']/p[2]/a")
prices = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='price text-right']/p[1]")
customers = driver.find_elements_by_xpath("//table/tbody/tr[((contains(@class,'odd') or contains(@class,'even')) and not (contains(@class,'description')))]/td[5]/p")
types = driver.find_elements_by_xpath("//div[@class='description']/p[2]/strong")

#print(field1.get_attribute('href')) #содержимое элемента
print(len(customers)) #длинна массива элемента
myArr=[['']*6 for i in range(len(links))]

for i in range(len(links)):
    myArr[i][0]=nums[i].text    
    myArr[i][1]=links[i].text
    myArr[i][2]=links[i].get_attribute('href')
    myArr[i][3]=prices[i].text.replace(" ", "").replace(",", ".")
    myArr[i][4]=customers[i].text
    myArr[i][5]=types[i].text
    print(myArr[i][0]+'||'+myArr[i][1]+'||'+myArr[i][3]+'||'+myArr[i][4]+'||'+myArr[i][5])
    
while True:
    try:
        nextPage = driver.find_element_by_xpath("//div[@class='tbl pages-list'][1]/div[@class='cell cell-left list']/ul[@class='clean horizontal']/li[@class='control'][3]/p/a")
        nextPage.click()
        #nextPage = driver.find_elements_by_xpath("/html/body/form[@id='form1']/div[@class='wrapper']/div[@class='body body-inner']/div[@class='body-column body-column-right content']/div[@class='tbl pages-list'][1]/div[@class='cell cell-left list']/ul[@class='clean horizontal']/li[@class='control'][3]/p/a")
        page=page+1
        btns = driver.find_elements_by_xpath("//td[@class='control']/img[@class='btm']")
        for t in range(len(btns)):
            btns[t].click()
        nums = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='description']/p[1]")
        links = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='description']/p[2]/a")
        prices = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='price text-right']/p[1]")
        customers = driver.find_elements_by_xpath("//table/tbody/tr[((contains(@class,'odd') or contains(@class,'even')) and not (contains(@class,'description')))]/td[5]/p")
        types = driver.find_elements_by_xpath("//table/tbody/tr/td[@class='description']/div[@class='description']/p[2]/strong")
                
        #print(len(myArr))
        
        k=0
        endOfCicle=i+len(links)
        #print(endOfCicle)
        while i < endOfCicle:
            myArr.append(['','','','','',''])
            #print(len(myArr))
            i=i+1
            myArr[i][0]=nums[k].text    
            myArr[i][1]=links[k].text
            myArr[i][2]=links[k].get_attribute('href')
            myArr[i][3]=prices[k].text.replace(" ", "").replace(",", ".")
            myArr[i][4]=customers[k].text
            myArr[i][5]=types[k].text
            print(myArr[i][0]+'||'+myArr[i][1]+'||'+myArr[i][3]+'||'+myArr[i][4]+'||'+myArr[i][5])
            k=k+1    
        #if page==2: #отладочный останов на 2 странице
        #    break
    except NoSuchElementException:
        print("Oops!  That was no Next link.  It seems that it is finish...")
        break

print(len(myArr))        
        
driver.close()

#функция фильтрации данных
def myTendFilter(myArr, minPrice, maxPrice,keyWords,keyTenderTypes,customer):
    resArr=[['']*6]
    k=0
    for i in range(len(myArr)):
        pr=float(myArr[i][3])
        minPrice=float(minPrice)
        flag=0        
        if customer!='':    #если установлен заказчик        
            if myArr[i][4].find(customer)>=0:    #если заказчик соответствует
                if len(keyWords)>0:                #если помимо заказчика есть ключевые слова
                    for n in range(len(keyWords)):
                        if myArr[i][1].find(keyWords[n])>=0:
                            #print(myArr[i][1]+'=='+keyWords[n])
                            flag=1            
                else:                            #если нет ключевых слов
                    flag=1
        else:                #если заказчик не установлен
            for n in range(len(keyWords)):
                if myArr[i][1].find(keyWords[n])>=0:
                    #print(myArr[i][1]+'=='+keyWords[n])
                    flag=1
        
        if pr>=minPrice and flag==1:
            resArr.append(['','','','','',''])
            resArr[k][0]=myArr[i][0]    
            resArr[k][1]=myArr[i][1]
            resArr[k][2]=myArr[i][2]
            resArr[k][3]=myArr[i][3]
            resArr[k][4]=myArr[i][4]
            resArr[k][5]=myArr[i][5]
            #print(resArr[k][0]+'||'+resArr[k][1]+'||'+resArr[k][3]+'\n')
            k=k+1
    return resArr



#подготовка текста сообщения
def MailMessage(myArr,filterName,keyWords,guid):
    resKeyWords=''
    for s in range(len(keyWords)):
        resKeyWords=resKeyWords+'|'+keyWords[s]
        eMessage='<BR><BR><B>Выборка по фильтру:'+filterName+'</B> [ключевые слова:<i>'+resKeyWords+'</i>]<BR><table><tr><td>Номер закупки</td><td>Ссылка</td><td>Цена</td><td>Тип</td><td>Организатор</td><td>Варианты действий</td></tr>'
    for i in range(len(myArr)-1):        
        if i % 2 == 0:
            eMessage=eMessage+'<tr bgcolor="Gainsboro">'
        else:
            eMessage=eMessage+'<tr>'
        eMessage=eMessage+'<td>'+myArr[i][0]+'</td>'
        eMessage=eMessage+'<td><a href='+myArr[i][2]+'>'+myArr[i][1]+'</a></td>'
        eMessage=eMessage+'<td>'+str(myArr[i][3])+'</td>'        
        eMessage=eMessage+'<td>'+str(myArr[i][5])+'</td>'
        eMessage=eMessage+'<td>'+str(myArr[i][4])+'</td>'
        eMessage=eMessage+'<td><a href="http://smartchein.ru/bots/pyhello.php?user='+guid+'&show=tenders&action=mon&tenderid='+myArr[i][0].replace('/','')+'&desc='+myArr[i][1][0:150]+'">Отслеживать</a></td>'
        eMessage=eMessage+'</tr>'
    eMessage=eMessage+'</table><BR><b><a href="http://smartchein.ru/bots/pyhello.php?user='+guid+'&show=tenders">Список отслеживаемых тендеров</a><br><p color="red">ВНИМАНИЕ!!! ССЫЛКИ НА ОТСЛЕЖИВАНИЕ ЯВЛЯЮТСЯ ПЕРСОНАЛЬНЫМИ!!! НЕ ПЕРЕСЫЛАЙТЕ ДАННОЕ СООБЩЕНИЕ КОМУ-ЛИБО ВО ИЗБЕЖАНИЕ НЕСАНКЦИОНИРОВАННОГО ДОСТУПА К ПЕРЕЧНЮ ВАШИХ ТЕНДЕРОВ</p></b>'
    return eMessage

#sending mail function
def SendMail(to,subject,eMessage,msg):
    HOST = "mail.smartchein.ru"
    fro = "info@smartchein.ru"
        
    msg['Subject'] = subject
    msg['From'] = fro
    msg['To'] = to

    # Create the body of the message (a plain-text and an HTML version).
    #text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
    html = eMessage
    
    #part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    #msg.attach(part1)
    msg.attach(part2)
     
    #connect to server
    server = smtplib.SMTP(HOST,587)
    #login to mailbox
    server.login('info@smartchein.ru','scinfo_76589')
    server.sendmail(fro, to, msg.as_string())
    server.quit()
    return 1

#numerical filters section start =================================

#filters 
myFilters={'asu' : (15000000,' Системы контроля и управления с ценой > 15 000 000',['СКУ','АСУ','систем','автомати', 'шкаф', 'мпу', 'мщу', 'панел','измерит','оборуд','комплек'],''),
           'proj' : (350000,' Проектирование > 450 000',['проект','документ','разраб'],''),
           'rasu' : (3000000,' РАСУ > 3 000 000',[''],'Русатом Автоматизированные системы управления'),
           'oditz' : (8000000,' ОДИЦ > 8 000 000',[''],'пытно-демонстрационный'),
           'uemz' : (10000000,' УЭМЗ > 10 000 000',[''],'Уральский электромеханический завод'),
           'sniip' : (6000000,' СНИИП > 6 000 000',[''],'Институт приборостроения'),
           'electro' : (4000000,' Электрика > 4 000 000',['РЗ','релейн', 'КРУ', 'вольт', 'НКУ', ' напряжен', ' ток'],''),
           'ekra' : (400000,' Продукция ЭКРА > 400 000',['РЗ', 'релейн', 'ПА', 'противоавар', 'ЩПТ', 'постоянн', 'беспереб','НКУ', 'КРУ', 'ЭКРА', 'инвертор', 'выпрямител'],''),
           'svyaz' : (400000,' ВЧ связь > 400 000',['связь', 'ВЧ', 'фильтр', 'загради'],''),
           'bdk_nasos' : (1000000,' Насосное оборудование > 1 000 000',['насос', 'агрегат', 'запасн', 'запчасти', 'комплектующ','торц','уплотн'],''), 
           'bdk_baki' : (5000000,' Емкости и баки > 5 000 000',['бак', 'гидроемкост', 'емкост'],''), 
           'bdk_disel' : (10000000,' Дизель > 10 000 000',['САУ', 'ДГУ', 'дизел'],''),
           'bdk_asu' : (20000000,' АСУ > 20 000 000',['ПТК', 'АСУ', 'СНЭ', 'СКУ', 'ХВО', 'САР ТО', 'САОЗ', 'ESMI'],''), 
           #титан:
           'titan1' : (1000000,'НКУ с ценой > 1 млн.',['РУНН','НКУ','ГРЩ','ЩРГ','ЩПТ','Низковольт','КРАУ','РТЗО','КТПСН','распределительн'],''),
           'titan2' : (1000000,'IT с ценой > 1 млн.',['ЦОД','Дата центр','центр обработки данных'],''),
           'titan3' : (1000000,'АСУ с ценой > 1 млн.',['РЗА','мониторинг','СКУ','ПЗ','АИИСКУЭ','АСУТП','АСУ','автоматизирован','управления'],''),
           #кип
           'kip' : (4000000,'КИП с ценой > 4 млн.',['КИП', 'расход', 'ультразву', 'измер','уровн','давлен','метр','датчи','контрол','РОС','РИС','СУЭ ДАС','СПС','СУРГ'],''),
           #НИОКР
           'niokr' : (7000000,'НИОКР с ценой > 7 млн.',['НИОКР','ОКР','опыт','конструторск','исследоват'],''),
           #поковки
           'pokovki' : (2500000,'Поковки с ценой > 2,5 млн.',['поков','бандаж','обечай','обойм','седл','корпус','флан','кольц','сектор','рельс','колес','патруб'],'')
           
           }
#users
myUsers={'Alexey1' : ('Алексей','avkuryatov@yandex.ru',' Бот: Закупки Росатома: для Алексея','eRtm!5hdz1'),
         #'GOL' : ('Евгений','evgeny.golovanov99@gmail.com',' Бот: Закупки Росатома: для Евгения','eR!5HdZ_1'),
         'GOL' : ('Евгений','evsgolovanov@gmail.com',' Бот: Закупки Росатома: для Евгения','eR!5HdZ_1'),
         'BDK' : ('Ярослав','bdk@tehnab.ru',' Бот: Закупки Росатома: для Ярослава','wGhj5!420iRt'),
         'UPA' : ('Павел','upa@tehnab.ru',' Бот: Закупки Росатома: для Павла','vuT6eRW!po0'),
         'BAN' : ('Алексей','ban@tehnab.ru',' Бот: Закупки Росатома: для Алексея Богатова','vdcE!po06yH'),
         'KEY' : ('Валерияэ','key@tehnab.ru',' Бот: Закупки Росатома: для Валерии Ковалевой', 'BV3d6Taldx!_65F'),
         #ПАМ
         'PiterAM' : ('Питератоммаш','piteratommash@mail.ru',' Бот: Закупки Росатома: для Питератоммаш','sKn3shg9!6B'),
         #АГАТ-КИП
         'Agat' : ('Константин', 'agat-kip.market@yandex.ru',' Бот: Закупки Росатома: для АГАТ-КИП','fg!7tEWaqloX'),
         #титан:
         'Chagin' : ('Денис Чагин','dionis-spb@yandex.ru',' Бот: Закупки Росатома: для Чагина','bUf1r!_YhS'),
         'Toropov' : ('Александр Торопов','toropov.aa@szte.ru',' Бот: Закупки Росатома: для Торопова','nohG6!gR7'),
         'Bessonov' : ('Павел Бессонов','Bessonov.pe@mail.ru',' Бот: Закупки Росатома: для Бессонова','FQapod856dY!v'),
         'Apanuk' : ('Екатерина Апанюк', 'apanuk.es@szte.ru','Бот: Закупки Росатома: для Апанюк','FQapod856dY!v')     
         }
#filers for users
userFiltersDict={
                'Alexey1' : ['asu','proj','electro','rasu','uemz','sniip','pokovki'], 
                'BAN' : ['asu','proj','electro','kip','ekra','rasu','uemz','sniip','pokovki','bdk_nasos','bdk_baki','bdk_asu','bdk_disel','svyaz','oditz'], 
                'KEY' : ['asu','proj','electro','kip','ekra','rasu','uemz','sniip','pokovki','bdk_nasos','bdk_baki','bdk_asu','bdk_disel','svyaz','oditz'], 
                'GOL' : ['kip','rasu','sniip'], 
                'BDK' : ['bdk_nasos','bdk_baki','bdk_asu','bdk_disel'], 
                'PiterAM' : ['bdk_nasos','bdk_baki'], 
                'Agat' : ['kip','rasu','sniip'], 
                'UPA' : ['ekra','svyaz'],
                'Chagin' : ['titan1','titan2', 'titan3'], 
                'Bessonov' : ['titan1','titan2', 'titan3'],
                'Toropov' : ['titan1','titan2', 'titan3'],
                'Apanuk' : ['titan1','titan2', 'titan3']
                }
#userFiltersDict={'GOL' : ['kip','rasu','sniip']}




maxPrice=''
keyTenderTypes=''
eMessage=''
for key, value in userFiltersDict.items():
    #адресат 1
    fio = myUsers[key][0]
    emailto=myUsers[key][1]
    MessageName=dtnow+':'+myUsers[key][2]
    guid=myUsers[key][3]
    #print(MessageName)
    
    #filter
    for num in range(len(value)):        
        filterId = value[num]
        minPrice = myFilters[filterId][0]
        filterName = myFilters[filterId][1]
        keyWords = myFilters[filterId][2]
        customer = myFilters[filterId][3]
        #print(keyWords)
        #start filtering
        resArr=myTendFilter(myArr, minPrice, maxPrice,keyWords,keyTenderTypes,customer)
        #create message table    
        eMessage=eMessage+MailMessage(resArr,filterName,keyWords,guid)
    
    #sending mail to person
    #sending message    
    msg = MIMEMultipart('alternative')
    SendMail(emailto,MessageName,eMessage,msg)
    eMessage=''

#numerical filters section end =================================
    
#print(eMessage)
    
#print(len(resArr))
            