
# coding: utf-8

# Assignment_02

# **- Library**

# In[1]:


from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import random
import time
from selenium.webdriver.common.keys import Keys
import requests
import bs4
import pandas as pd
from pandas import DataFrame
import warnings
warnings.filterwarnings("ignore")
import string
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json


# **- Function**

# In[2]:


def open_website(URL='http://www.mlb.com'):
    #driver = webdriver.Firefox(executable_path='./geckodriver')
    #driver.close()
    driver = webdriver.Chrome(executable_path='./chromedriver')
    driver.get(URL)
    return driver


# In[3]:


def delay_move_to_header(driver, target_text='megamenu-navbar-overflow__menu-item--stats'):
    wait = WebDriverWait(driver, 10)
    target = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, target_text)))
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    ActionChains(driver).move_to_element(target).perform()
    print('Like human')
    return target


# In[4]:


def delay_select_item_with_header(driver, header_bar,target_text='2017 Regular Season Stats'):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    elements_list = header_bar.find_elements_by_tag_name('li') 
    for e in elements_list:
        if e.text == target_text:
            target = e
    ActionChains(driver).move_to_element(target).click().perform()
    print('Like human')
    return driver


# In[5]:


def select_season(driver, season_text='2015'):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    hit_element = driver.find_element_by_id('sp_hitting_season')
    select_element = Select(hit_element)
    select_element.select_by_value(season_text)
    print('Like human')
    return driver


# In[6]:


def one_click_to_season(season):
    driver=open_website()
    header_bar = delay_move_to_header(driver)
    driver = delay_select_item_with_header(driver, header_bar)
    driver = select_season(driver,season)
    print('Like human')
    return driver


# In[7]:


def select_game_type(driver,game_type_text='Regular Season', type_id = 'st_hitting_game_type'):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    hit_game_type = driver.find_element_by_id(type_id)
    select_element = Select(hit_game_type)
    select_element.select_by_visible_text(game_type_text)
    print('Like human')
    return driver


# In[8]:


def select_team(driver):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    hit_team = driver.find_element_by_id('st_parent')
    data_element = hit_team.click()
    print('Like human')
    return driver


# In[9]:


def select_player(driver):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    hit_player = driver.find_element_by_id('sp_parent')
    data_element = hit_team.click()
    print('Like human')
    return driver


# In[10]:


def select_splits(driver,splits_text='First Inning'):
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    hit_splits = driver.find_element_by_id('st_hitting_hitting_splits')
    select_element = Select(hit_splits)
    select_element.select_by_visible_text(splits_text)
    print('Like human')
    return driver


# In[11]:


def extract_team_from_html(driver):
    data_element = driver.find_element_by_id('datagrid')
    data_html = data_element.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html,'html5lib')
    table_trs = soup.find_all('tr')
    col_n = []
    col = soup.find_all('th')
    for head in col:
        if head.string is not None:
            col_n.append(head.string)
    col = soup.find_all('abbr')
    for head in col:
        col_n.append(head.string)
    col_n.insert(2,"dg-file_code")
    col_n.pop(4)
    ulist = []
    for tr in table_trs:
        ui = []
        for td in tr:
            ui.append(td.string)
        ulist.append(ui)
    ulist.pop(0)
    ulist.insert(0, col_n)
    return ulist


# In[12]:


def extract_player_from_html(driver):
    data_element = driver.find_element_by_id('datagrid')
    data_html = data_element.get_attribute('innerHTML')
    soup = bs4.BeautifulSoup(data_html,'html5lib')
    table_trs = soup.find_all('tr')
    col_n = []
    col = soup.find_all('th')
    for head in col:
        if head.string is not None:
            col_n.append(head.string)
    col = soup.find_all('abbr')
    for head in col:
        col_n.append(head.string)
    col_n.remove('▲')
    col_n.insert(3, 'player_id')
    col_n.pop(5)
    ulist = []
    for tr in table_trs:
        ui = []
        for td in tr:
            for a in td:
                ui.append(a.string)
        ulist.append(ui)
    ulist.pop(0)
    for i in ulist:
        i.remove('\xa0')
    for i in ulist:
        i.remove('\xa0')
    ulist.insert(0, col_n)
    return ulist


# In[13]:


def store_data_to_csv(ulist, file_name):
    dataframe = pd.DataFrame(ulist[1:], columns=ulist[0])
    dataframe.to_csv(file_name, index=False)


# In[14]:


def select_all_players(driver):
    target = driver.find_element_by_id('sp_hitting_playerType_alltime')
    ActionChains(driver).move_to_element(target).click().perform()
    return driver


# In[15]:


def click_next_page(driver):
    target = driver.find_element_by_class_name('paginationWidget-next')
    ActionChains(driver).move_to_element(target).click().perform()
    return driver


# In[16]:


def click_next_extract_store(driver, file_name = 'Question_3.csv', page_no = 24):
    global ulist, df
    df = None
    ulist = None
    normal_delay = random.normalvariate(2, 0.5)
    time.sleep(normal_delay)
    print('Like Human.')
    count = 1
    while count < page_no:
        driver = click_next_page(driver)
        ulist = extract_player_from_html(driver)
        normal_delay = random.normalvariate(2, 0.5)
        time.sleep(normal_delay)
        df = DataFrame(ulist[1:])
        normal_delay = random.normalvariate(2, 0.5)
        time.sleep(normal_delay)
        with open(file_name, 'a') as infile:
            df.to_csv(infile, index=False, header=False)
        count +=1
    return driver


# In[17]:


def select_AL(driver):
    target = driver.find_element_by_id('sp_hitting_league_code_al')
    ActionChains(driver).move_to_element(target).click().perform()
    return driver


# In[18]:


def print_player_full_name(player_id):
    URL='http://mlb.mlb.com/team/player.jsp?player_id='+player_id
    driver = open_website(URL)
    target = driver.find_element_by_class_name('full-name')
    player_full_name = target.text
    driver.close()
    return player_full_name


# In[19]:


def print_team_full_name(player_id):
    URL='http://mlb.mlb.com/team/player.jsp?player_id='+player_id
    driver = open_website(URL)
    target = driver.find_element_by_class_name('languagebar__title')
    team_full_name = target.text
    team_full_name = team_full_name.replace('THE OFFICIAL SITE OF THE ', '')
    driver.close()
    return team_full_name


# In[20]:


def print_born_country(player_id):
    URL='http://mlb.mlb.com/team/player.jsp?player_id='+player_id
    driver = open_website(URL)
    idx = [2,3,4]
    for i in idx:
        target = driver.find_element_by_xpath("""//*[@id="quick-stats"]/div[2]/ul[1]/li[{}]""".format(str(i)))
        if 'Born:' in target.text:
            born = target.text
            born_str = ' '
            born_str = born_str.join(born.split()[0:3])
            born_country = born.replace(born_str, '')
            born_country = born_country.strip()
    driver.close()
    return born_country


# In[21]:


def call_mlb_api(URL):
    headers = {'Ocp-Apim-Subscription-Key': 'e6c835cafcca4a478215acfae764b336',}

    try:
        conn = http.client.HTTPSConnection('api.fantasydata.net')
        conn.request("GET", URL, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        print('Success!')
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        
    return data


# In[22]:


def transcode_b_to_json(data, file_name):
    json_data = data.decode('utf8')
    output_data = json.loads(json_data)
    with open(file_name,"w") as outfile:
        json.dump(output_data,outfile)
    return None


# **1. Which team had the most homeruns in the regular season of 2015? Print the full team name.**

# - 2015
# - team
# - regular season
# - HR

# In[23]:


driver = one_click_to_season('2015')
driver = select_team(driver)
driver = select_game_type(driver,'Regular Season')


# In[24]:


ulist = extract_team_from_html(driver)
store_data_to_csv(ulist, 'Question_1.csv')


# In[25]:


df = pd.read_csv('Question_1.csv')


# In[26]:


q1 = df[['Team','HR']].sort_values(by='HR', ascending=False)
q1.iloc[0,:]


# In[27]:


driver.close()


# **2. Which league (AL or NL) had the greatest average number of homeruns…  **

# a) in the regular season of 2015? Please give the league name and the average number of homeruns.  
# - season-2015
# - team
# - regular season
# - HR

# In[28]:


driver = one_click_to_season('2015')
driver = select_team(driver)
driver = select_game_type(driver,'Regular Season')


# In[29]:


ulist = extract_team_from_html(driver)
store_data_to_csv(ulist, 'Question_2_a.csv')


# In[30]:


driver.close()


# In[31]:


df = pd.read_csv('Question_2_a.csv')


# In[32]:


q2_a = df[['League','HR']].groupby('League', as_index=False)['HR'].mean()
q2_a


#  b) in the regular season of 2015 in the first inning? Please give the league name and the average number of homeruns.  
# - season-2015
# - team
# - regular season
# - first inning

# In[33]:


driver = one_click_to_season('2015')
driver = select_team(driver)
driver = select_game_type(driver,'Regular Season')


# In[34]:


driver = select_splits(driver,'First Inning')


# In[35]:


ulist = extract_team_from_html(driver)
store_data_to_csv(ulist, 'Question_2_b.csv')


# In[36]:


driver.close()


# In[37]:


df = pd.read_csv('Question_2_b.csv')


# In[38]:


q2_b = df[['League', 'HR']].groupby('League', as_index=False)['HR'].mean()
q2_b


# 3. What is the name of the player with the best overall batting average in the 2017 regular season that played for the New York Yankees,who  
#     a) had at least 30 at bats? Please give his full name and position.  

# - 2017
# - all players
# - regular season
# - AVG
# - Full Name

# In[39]:


driver = one_click_to_season('2017')
driver = select_game_type(driver,'Regular Season', 'sp_hitting_game_type')


# In[40]:


driver = select_all_players(driver)


# page1

# In[41]:


ulist_1 =extract_player_from_html(driver)
store_data_to_csv(ulist_1, 'Question_3.csv')


# page2-25

# In[42]:


driver = click_next_extract_store(driver,'Question_3.csv', 25)


# In[43]:


driver.close()


# In[44]:


df = pd.read_csv('Question_3.csv')


# In[45]:


q3_a = df[['Player','player_id' ,'Pos','AVG']][(df['Team']=='NYY')&(df['AB']>30)].sort_values(by='AVG', ascending=False)
answer = q3_a.iloc[0,:]


# In[46]:


player_id = str(answer[1])


# In[47]:


full_name = print_player_full_name(player_id)
answer[0]= full_name
print(answer)


# b) played in the outfield (RF, CF, LF)? Please give his full name and position.

# In[48]:


df = pd.read_csv('Question_3.csv')


# In[49]:


q3_b = df[['Player','player_id','Pos','AVG']][(df.Team=='NYY')& ((df.Pos=='RF')|(df.Pos=='CF')|(df.Pos=='LF'))].sort_values(by='AVG', ascending=False)
answer = q3_b.iloc[0,:]


# In[50]:


player_id = str(answer[1])


# In[51]:


full_name = print_player_full_name(player_id)
answer[0]= full_name
print(answer)


# **4. Which player in the American League had the most at bats in the 2015 regular season? Please give his full name, full team name, and position.** 
# 
# - AL
# - 2015
# - Regular Season
# - player

# In[52]:


driver = one_click_to_season('2015')
driver = select_game_type(driver,'Regular Season', 'sp_hitting_game_type')


# In[53]:


driver = select_all_players(driver)


# In[54]:


driver = select_AL(driver)


# Page 1

# In[55]:


ulist_1 =extract_player_from_html(driver)
store_data_to_csv(ulist_1, 'Question_4.csv')


# Page 12

# In[56]:


driver = click_next_extract_store(driver,'Question_4.csv', 12)


# In[57]:


driver.close()


# In[58]:


df=pd.read_csv('Question_4.csv')


# In[59]:


q4 = df[['Player','player_id','Team','Pos','AB']].sort_values(by='AB', ascending=False)
answer = q4.iloc[0, :]


# In[60]:


player_id = str(answer[1])


# In[61]:


full_name = print_player_full_name(player_id)
answer[0]= full_name


# In[62]:


team_full_name = print_team_full_name(player_id)
answer[2]=team_full_name
print(answer)


# **5. Which players from the 2014 All-star game were born in Latin America (google a country list)? Please give their full name and the full name of the team they play for.**

# - 2014
# - all-star game
# - player

# In[64]:


driver = one_click_to_season('2014')
driver = select_game_type(driver,'All-Star Game', 'sp_hitting_game_type')


# page 1

# In[65]:


ulist_1 =extract_player_from_html(driver)
store_data_to_csv(ulist_1, 'Question_5.csv')


# In[66]:


df = pd.read_csv('Question_5.csv')
Latin_A_list=["Argentina", 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominican Republic', 'Ecuador' ,'El Salvador', 'French Guiana', 'Guadeloupe', 'Guatemala', 'Haiti', 'Honduras', 'Martinique', 'Mexico','Nicaragua', 'Panama', 'Paraguay','Peru','Puerto Rico', 'Saint Barthélemy', 'Saint Martin', 'Uruguay', 'Venezuela']


# In[67]:


player_country_list = []
for i in df['player_id']:
    player_id = str(i)
    player_born_country = print_born_country(player_id)
    player_country_list.append(player_born_country)    
df['Country'] = player_country_list


# In[68]:


match_list = []
for i in Latin_A_list:
    for j in df.Country:
        if i in j:
            match_list.append(j)
match_list = list(set(match_list))


# In[69]:


q5 = df[['Player', 'Team', 'Country']][df.Country.isin(match_list)]
q5


# **6. Please print the 2016 regular season schedule for the Houston Astros in chronological order. Each line printed to the screen should be in the following format:**
#    

# In[70]:


""" <opponent Team Name> <game date> <stadium name> <city>, <state>"""


# In[71]:


data_schedule = call_mlb_api("/v3/mlb/scores/JSON/Games/2016")
transcode_b_to_json(data_schedule,"Question_6_Schedules.json")
df = pd.read_json("Question_6_Schedules.json")


# In[72]:


q6_main = df[['HomeTeam','AwayTeam','DateTime', 'StadiumID']][(df['HomeTeam'] == 'HOU')|(df['AwayTeam']=='HOU')]


# In[73]:


opponent_Team_Name = []
for i in range(len(q6_main['HomeTeam'])):
    if q6_main.iloc[i, 0] == 'HOU':
        opponent_Team_Name.append(q6_main.iloc[i,1])
    elif q6_main.iloc[i, 1] == 'HOU':
        opponent_Team_Name.append(q6_main.iloc[i,0])
    else:
        print('Last Step Error')
q6_main['Opponent'] = opponent_Team_Name


# In[80]:


data_team = call_mlb_api("https://api.fantasydata.net/v3/mlb/scores/JSON/AllTeams")
transcode_b_to_json(data_team,"Question_6_all_teams.json")
q6_team = pd.read_json("Question_6_all_teams.json")


# In[81]:


q6_team = q6_team[['Key', 'City','Name']]


# In[82]:


city_name_list = []
team_name_list = []
for i in q6_main['Opponent']:
    for j in q6_team['City'][q6_team['Key']==i]:
        city_name = j 
        city_name_list.append(city_name)
    for k in q6_team['Name'][q6_team['Key']==i]:
        team_name = k
        team_name_list.append(team_name)
q6_main['City'] = city_name_list
q6_main['Team'] = team_name_list


# In[90]:


data_stadiums = call_mlb_api("/v3/mlb/scores/JSON/Stadiums")
transcode_b_to_json(data_stadiums,"Question_6_stadiums.json")
q6_stadiums = pd.read_json("Question_6_stadiums.json")


# In[92]:


q6_stadiums = q6_stadiums[['StadiumID', 'Name', 'City','State']]


# In[93]:


stadium_name_list = []
state_list = []
for i in q6_main['StadiumID']:
    for j in q6_stadiums['Name'][q6_stadiums['StadiumID']==i]:
        stadium_name = j
        stadium_name_list.append(stadium_name)
    for k in q6_stadiums['State'][q6_stadiums['StadiumID'] ==i]:
        state = k
        state_list.append(state)


q6_main['Stadium'] = stadium_name_list
q6_main['State'] = state_list


# In[94]:


q6_main['Opponent Name'] = q6_main[['City', 'Team']].apply(lambda x: ' '.join(str(value) for value in x), axis=1)


# In[95]:


q6_main[['Opponent Name', 'DateTime', 'Stadium', 'City', 'State']]

