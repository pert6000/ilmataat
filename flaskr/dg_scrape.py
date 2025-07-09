

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime
from flaskr.yr_api import weather_data


def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def tee_supp(driver, link):

    print(link)
    driver.get(link)

    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")


    return soup


# paneb raja nime discordi
# kui otsingule tuleb rohkem kui 1 vaste siis peab täpsustama
# kui täpsustatud või tuli 1 vaste siis leitakse koordinaadid ja vastav ilm
# avab metrixi lingi ja käib läbi kõik selle raja layoutid ja vaatab kas seal võistlusi

def otsi_rada(raja_nimi):
    resp = requests.get(
        "https://www.discgolfirajad.ee/wp-json/wp/v2/park?search=" + raja_nimi
    )

    # kirjuta sisse loogika mis valib leitud radade hulgast selle mida vaja

    rajad = []
    for rada in resp.json():
        rajad.append([rada["title"]["rendered"], rada["link"]])

    #print(resp.json()[0]["title"]["rendered"])
    #print(resp.json()[0]["link"])
    #info = raja_info(resp.json()[0]["link"])
    #print(info)

    return rajad

    #leia_layoutid(info[1])



def raja_info(driver, raja_link):
    soup = tee_supp(driver, raja_link)

    #koordinaat = soup.find("div.b-single_location-button")

    nupp = soup.select_one("div.b-single_location-button")

    link =  nupp.find('a', href=True)['href']

    koordinaadid = extract_coords(link)

    nupp = soup.select_one("div.b-single__info-text")

    metrix_link = nupp.find('a', href=True)['href']

    return [koordinaadid, metrix_link]


def extract_coords(link):
    lat = link[(link.rfind('/') + 1):(link.rfind('/') + 7)]
    lon = link[(link.rfind(',') + 1):(link.rfind(',') + 7)]

    return [lat, lon]


def leia_layoutid(driver, metrix_link):
    soup = tee_supp(driver, metrix_link)

    buttons = soup.select_one("div.button-group.button-group-inline")

    layouts = []
    if buttons is not None:
        for layout in buttons.find_all('a', href=True):
            layouts.append("https://discgolfmetrix.com" + layout['href'])
    else:
        layouts.append(metrix_link)


    comps = []
    for layout in layouts:
        comps += leia_raja_voistlused(driver, layout)

    return comps



def leia_raja_voistlused(driver, metrix_link):

    soup = tee_supp(driver, metrix_link)

    heading = soup.find('h2', string="Upcoming events")

    # Get the next table after the heading
    table = heading.find_next("table") if heading else None

    comps = []
    if table:
        for row in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if cols[0].startswith(datetime.today().strftime('%Y-%m-%d')):
                comps.append(cols)
    else:
        print("Table not found")

    return comps


def main():

    otsing = input("Sisesta otsing: ")

    driver = init_driver()

    rajad = otsi_rada(otsing)

    print("Leitud rajad:")
    for rada in rajad:
        print(rada[0])

    if len(rajad) > 1:
        valik = input("\nMillist rada neist soovid: ")
        for i in range(len(rajad) - 1, -1, -1):
            if valik not in rajad[i][0]:
                rajad.pop(i)

    if len(rajad) == 0:
        print("Sellise nimetusega radu pole.")
        driver.quit()
        return
    elif len(rajad) > 1:
        print("Ei täpsustanud piisavalt.")
        driver.quit()
        return

    print("Valitud rada: " + rajad[0][0])

    print("Otsin võistluseid.")

    info = raja_info(driver, rajad[0][1])
    voistlused = leia_layoutid(driver, info[1])
    print("Siin on soovitud raja tänane ilmateade:")
    print(weather_data(info[0][0], info[0][1]))

    if len(voistlused) == 0:
        print("Sellel rajal täna võistlusi pole")
    else:
        print("Sellel rajal toimub täna võistlus:")
        print(voistlused)

    driver.quit()


#scrape_metrix()
#otsi_rada("kohila")
#print(leia_layoutid("https://discgolfmetrix.com/course/40801"))
if __name__ == '__main__':
    main()
