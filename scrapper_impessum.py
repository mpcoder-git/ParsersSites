import requests
import  fake_useragent
import re
import csv
from bs4 import BeautifulSoup

links = []
list_emails = []

#проверка доступности сайта
def check_website(url):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectTimeout:
        return False
    except requests.ConnectionError:
        return False
    except requests.exceptions.RequestException as e:
        print('Error: ', e)

#извлечение почты
def extract_emails(url):
    ua = fake_useragent.UserAgent()
    headers = {"user-agent": ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.ConnectTimeout:
        print(url +" Error coonect: time out.")
        return
    except requests.exceptions.RequestException as e:
        print('Error: ', e)

    if (response.status_code == 200):
        print(url + ' OK')
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
        unique_emails = list(set(emails))

    return unique_emails


#
def return_impressum(url,domain):
    substr = "impressum"
    print('extract all links for ' + url)
    try:
        response = requests.get(url, timeout=3)
    except requests.exceptions.ConnectTimeout:
        return None
    except requests.ConnectionError:
        return None
    except requests.exceptions.RequestException as e:
        print('Error: ', e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    links_impr = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('#'):
            index_href = href.find(domain)
            if index_href != -1:
                links_impr.append(href)
            else:
                links_impr.append(url + href)
    if len(links_impr) > 0:
        for i in range(0, len(links_impr)):
            s = links_impr[i]
            index = s.find(substr)
            if index != -1:
                return links_impr[i]
    else:
        return None


#генерация списка ссылок на парсинг
def txt_to_list():
    try:
        file = open("alllinks.txt", "r")
    except OSError as e:
        print("file alllinks.txt not found! create file and add links to scan")
        return
    for word in file.read().split():
        # print(word)
        if len(word) == 0:
            continue

        lnk1 = 'http://' + word
        lnk2 = 'https://' + word
        result1 = check_website(lnk1)
        result2 = check_website(lnk2)
        corrected_link = ''

        if (result1 == True and result2 == False):
            impressum_page = return_impressum('http://' + word, word)
            if impressum_page:
                if impressum_page != '':
                    corrected_link = impressum_page
        if (result1 == False and result2 == True):
            impressum_page = return_impressum('https://' + word, word)
            if impressum_page:
                if impressum_page != '':
                    corrected_link = impressum_page
        if (result1 == False and result2 == False):
            print(word + ' domain not available!')
        if (result1 == True and result2 == True):
            impressum_page = return_impressum('http://' + word, word)
            if impressum_page:
                if impressum_page != '':
                    corrected_link = impressum_page
        if corrected_link != '':
            links.append(corrected_link)


def printmails():
    res = []
    c = int(input("\nExtraction Complete  ||   Enter 0 to print output, 1 to save file & 2 for both  & 3 save to csv: "))
    if c==1:
        with open('mails_out.txt', 'w') as f:
            for i in list_emails:
                if i not in res:
                    f.write("%s\n" % i)
    elif c==0:
        for i in list_emails:
            if i not in res:
                print(i)
                res.append(i)
    elif c==2:
        with open('mails_out.txt', 'w') as f:
            for i in list_emails:
                if i not in res:
                    print(i)
                    f.write("%s\n" % i)
                    res.append(i)
    elif c == 3:
        with open("info.csv", mode="w", encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=";", lineterminator="\r")
            #file_writer.writerow(["Имя", "Класс", "Возраст"])
            file_writer.writerow(["Email"])
            for email in list_emails:
                file_writer.writerow([email])

    else:
        print("[!] Invalid Input")


def main():
    txt_to_list()
    if len(links) > 0:
        print("Scanning:-")
        for lnk in links:
            try:
                emails = extract_emails(lnk)
                for email in emails:
                    list_emails.append(email)
            except Exception as e:
                continue
        printmails()


main()


