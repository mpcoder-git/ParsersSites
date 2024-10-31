import requests
from bs4 import BeautifulSoup
import  fake_useragent
import time
import json
import re

#parser https://www.autoscout24.de/

#def get_links(text):
def get_links():
    links_forscan = []
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f"https://www.autoscout24.de/lst?atype=C&cy=D&page=2&search_id=zsmpps7bvq&source=listpage_pagination",
        headers={"user-agent":ua.random}
    )
    #print(data.content)
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")
    # получаем количество страниц
    #page_count = int(soup.find("div",attrs={"class":"ListPage_pagination__4Vw9q"}).find_all("li", recursive=False)[-1].find("button").text))
    #test_content = soup.find("div", attrs={"class": "ListPage_pagination__4Vw9q"}).find("ul", recursive=True).find_all("button", recursive=True)[-2].text
    #print(test_content)
    try:
        page_count = int(soup.find("div", attrs={"class": "ListPage_pagination__4Vw9q"}).find("ul", recursive=True).find_all("button", recursive=True)[-2].text)
    except:
        return
    print(f"finding {page_count} pages. processing...")
    #цикл по всем страницам
    for page in range(page_count):
        try:
            data_page = requests.get(
                url=f"https://www.autoscout24.de/lst?atype=C&cy=D&desc=0&ocs_listing=include&page={page+1}&search_id=pdn7a7zqsx&sort=standard&source=listpage_pagination&ustate=N%2CU",
                headers={"user-agent": ua.random}
            )
            print(page+1)

            if data_page.status_code != 200:
                return

            #извлекаем страницу с объявлениями

            if data_page.status_code != 200:
                continue
            soup_page = BeautifulSoup(data_page.content, "lxml")
            #извлечение целевых ссылок на объявление
            for a in soup_page.find_all("a", attrs={"class": "ListItem_title__ndA4s ListItem_title_new_design__QIU2b Link_link__Ajn7I"}):
                #обрезка ссылки, если есть параметры после ?
                #print(f"https://www.autoscout24.de{a.attrs['href'].split('?')[0]}")
                #print (f"https://www.autoscout24.de{a.attrs['href']}")
                #links_forscan.append(f"https://www.autoscout24.de{a.attrs['href']}")
                link_toaadd = get_link_to_scan(f"https://www.autoscout24.de{a.attrs['href']}")
                links_forscan.append(link_toaadd)

        except Exception as e:
            print(f"{e}")
        #пауза чтобы не грузить сервер
        time.sleep(1)
    return links_forscan



def get_link_to_scan(link):
    ua = fake_useragent.UserAgent()
    try:
        data = requests.get(
            url=link,
            headers={"user-agent": ua.random}
        )
        # print(data.content)
        if data.status_code != 200:
            return
        soup = BeautifulSoup(data.content, "lxml")
        lnk = soup.find_all("a", attrs={"class": "scr-link DealerLinks_bold__urWLL"})[-1]
        link_to_contact = f"{lnk.attrs['href']}"
        return link_to_contact
    except Exception as e:
        print(f"{e}")
        return



def extract_emails(url):
    response = requests.get(url)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
    unique_emails = list(set(emails))
    return unique_emails


if __name__ == "__main__":
    list_emails = []
    links_s = get_links()
    #links_s = get_links("python")
    for lnke in links_s:
        #print(a)
        emails = extract_emails(lnke)
        for email in emails:
            #print(email)
            list_emails.append(email)
    unique_emails_list = list(set(list_emails))
    #for email in list_emails:
    #    print(email)
    with open('emails.txt', 'w') as file:
        for eml in unique_emails_list:
            file.write(str(eml) + '\n')
    print("emails saved to file!!!")

