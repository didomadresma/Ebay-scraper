import argparse
import os
import urllib2

import time
from bs4 import BeautifulSoup
import requests
import re
import json



def parse_ebay(page_num=1):
    r = requests.get(
        'http://www.ebay.com/sch/iPads-Tablets-eBook-Readers/171485/i.html?LH_BIN=1&_dcat=171485&rt=nc&LH_ItemCondition=1000')
    price_title = {}
    next_page_link = ''
    for _ in range(page_num):
        if next_page_link:
            r = requests.get(next_page_link)
        data = r.text
        soup = BeautifulSoup(data)
        for elem in soup.find_all('li', attrs={'class':'sresult lvresult clearfix li shic'}):
            title = elem.find('h3', attrs={'class': 'lvtitle'}).text.encode('utf-8')
            price = elem.find('li', attrs={'class': 'lvprice prc'}).text
            price = re.findall("\d+\.\d+", price)
            if len(price) != 1:
                price_title[title] = price[1]
            else:
                price_title[title] = price[0]
        # print price_title
        next_page_link = soup.find('a', attrs={'class': 'gspr next'}).get('href')
        # print next_page_link.get('href')
    with open('./output/results.txt', 'w') as outfile:
        json.dump(price_title, outfile)
    return price_title


def parse_amazon(titles_prices):
    for title, e_price in titles_prices.iteritems():
        r = requests.get('http://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords='+title.replace("\"", ""))
        data = r.text
        soup = BeautifulSoup(data)
        if soup.find('li', attrs={'class': 's-result-item celwidget'}) is not None:
            if soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}) is not None:
                # print soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}).text
                a_price = soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}).text
                a_price = re.findall("\d+\.\d+", a_price)
                print ("Ebay price: '%s' ----------------> Amazon price: '%s'" % (e_price, a_price[0]))
                if float(a_price[0]) > float(e_price):
                    print a_price

            # print soup.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'}).text
        # print len(soup.find_all('h2', attrs={'class': 'a-size-medium a-color-null s-inline  s-access-title  a-text-normal'}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run parser')
    # parser.add_argument("--ebay_link", dest="ebay_link", required=True,
    #                     help="Ebay link to parse", metavar="")
    parser.add_argument("--page_num", dest="page_num", required=True,
                        help="Page numbers to parse", metavar="")
    args = parser.parse_args()
    ebay_results = parse_ebay(page_num=int(args.page_num))
    parse_amazon(ebay_results)