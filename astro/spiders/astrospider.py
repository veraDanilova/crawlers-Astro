# -*- coding: utf-8 -*-

import datefinder
import datetime

import re
import io
import json
import os
import codecs

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import scrapy
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

"""examine page code"""
#scrapy shell web adress
#view(response)
#from scrapy.selector import Selector
#sel = Selector(response)

"""parse txt, ods"""
#import pkgutil
# data = pkgutil.get_data("astro", "resources/obj_names.txt")
# obj_names = data.decode('utf-8').splitlines()

# extract obj_names from .ods
# import pyexcel_ods3
# from pyexcel_ods3 import get_data

# ROOT_DIR = os.path.abspath(os.curdir)
# ROOT_DIR = os.path.dirname(__file__)
# print ROOT_DIR 

#data = get_data("/Users/Nami/Desktop/astro/astro/resources/Obj_Coords.ods")
# data = get_data(os.path.join(os.path.dirname(os.path.abspath(os.pardir)), "astro/resources/Obj_Coords.ods"))

# objects_json_string = json.dumps(data)
# objectsFormat = json.loads(objects_json_string)
# obj_list = objectsFormat[u'\u041b\u0438\u0441\u04421'][1:]#Лист1
# obj_names = [item[0] for item in obj_list if len(item) > 0 and len(item[0]) > 0] #and len(item[0]) > 0

obj_names = ["BS Tri", "HU Aqr", "V2301 Oph", "WW Hor", "V808 Aur", "DP Leo", "UZ For", "EP Dra", "V895 Cen", "HS Cam", "V379 Vir", "V1007 Her", "V1309 Ori", "V379 Tel", "J0227+1306", "VV Pup", "HY Eri", "J0545+0221", "J1927+4447", "EX Dra", "IP Peg", "V1239 Her", "J1006+2337", "GY Cnc", "J0750+1411"]


"""decode strings with mixed encoding, currently not used"""
#last_position = -1

# def mixed_decoder(unicode_error):
#     global last_position
#     string = unicode_error[1]
#     position = unicode_error.start
#     print(position, last_position)
#     if position <= last_position:
#         position = last_position + 1
#     last_position = position
#     new_char = string[position].decode("cp1252")
#     #new_char = u"_"
#     return new_char, position + 1

# codecs.register_error("mixed", mixed_decoder)


def find_all_substrings(string, sub):#осн фун для поиска ключ слов
    """

http://code.activestate.com/recipes/499314-find-all-indices-of-a-substring-in-a-given-string/

    """
    import re #regex
    starts = [match.start() for match in re.finditer(re.escape(sub), string)]
    return starts
#re.escape(sub)
#на вход два параметра string и sub. импорт regex. re.finditer(pattern, string, flags=0)
#match.start - вернуть index of the start of the substring matched by a group, in this case the whole matched substring
#функция ищет индекс начала подстроки для всех совпадений re.escape(pattern) в строке string
# Escape all the characters in pattern except ASCII letters and numbers. This is useful if you want to match an arbitrary literal string that may have regular expression metacharacters in it.

"""SPIDERS"""

class AstrospiderSpider(scrapy.Spider):
    name = 'astrospider'
    allowed_domains = ['cbastro.org']
    start_urls = ['https://cbastro.org/var/index.data-all.html']

    def parse(self, response):

        records = response.xpath('//li/text()').extract()
        
        #records = [r.encode("utf-8") for r in records]

        f = io.open(os.path.join(os.path.dirname(os.path.abspath(os.pardir)), "crawling_results/cbastro")+'.txt', "w", encoding = 'utf-8')#datetime.date.today().isoformat()
        f.write(u'website\t\tobject\t\tdate\t\tentry\n')
        

        for r in records:
            for kw in obj_names:
                mention = find_all_substrings(r, kw)
                if len(mention) > 0:
                    dateInR = datefinder.find_dates(r)#, strict = True)
                    dateInR = [d for d in dateInR]
                    #f.write(str(dateInR)+"\n")
                    norm_date = []
                    trigger = False
                    if len(dateInR) > 0:
                        for date in dateInR:
                            #if date.year <=  datetime.date.today().year:
                            if date <= datetime.datetime.today() and date.year >= 2020:
                                d = date.date()
                                norm_date.append(d)
                                trigger = False
                            else:
                                trigger = True         
                    #norm_date = list(filter(("Other").__ne__, norm_date))
                    if len(dateInR) == 0:
                        norm_date.append("None")
                    if trigger == False:  
                        for d in norm_date:
                            if d == "None":
                                dataline = "'cbastro.org'\t\t%s\t\t%s\t\t%s\n" % (str(kw), "None", str(r))
                                f.write(dataline)#.decode('utf8', "mixed"))
                            else:
                                dataline = "'cbastro.org'\t\t%s\t\t%s\t\t%s\n" % (str(kw), str([d.isoformat() for d in norm_date]), str(r))
                                f.write(dataline)#.decode('utf8', "mixed"))
                else:
                    pass
        f.close()



class FilterGraphSpider(scrapy.Spider):
    name = 'filtergraphspider'
    allowed_domains = ['filtergraph.com']
    start_urls = ['https://filtergraph.com/aavso?ac=on&settype=true']

    def parse(self, response):

        basenodes = response.xpath('//tbody/tr')
        datalines = []

        
        f = io.open(os.path.join(os.path.dirname(os.path.abspath(os.pardir)), "crawling_results/filtergraph")+'.txt', "w", encoding = 'utf-8')
        #+str(datetime.date.today().isoformat())
        f.write(u'website\t\tobject\t\tdate\t\tmin_mag\t\tmax_mag\n')
        for index, node in enumerate(basenodes):
            time_norm = False

            #time
            if node.xpath('td/span/@title'):
                #record
                record = node.xpath('td/a/text()').extract() 
                record = [r.encode("utf-8") for r in record]
                #magnitudes
                magnitudes = node.xpath('td/p/text()').extract()
                min_mag = magnitudes[0].encode("utf-8")
                max_mag = magnitudes[1].encode("utf-8")
                #time_normalize
                time = node.xpath('td/span/@title').extract()
                dateInR = datefinder.find_dates(str(time))
                dateInR = [d for d in dateInR]
                
                for date in dateInR:
                    #week_before = datetime.datetime.today().date() - datetime.timedelta(days = 7)
                    #if date.date() <= datetime.datetime.today().date() and date.date() >= week_before:
                    if date.year >= 2020:
                        time_norm = date.date()
                    else:
                        pass
                if time_norm:
                    args = (record, time_norm, min_mag, max_mag)
                    dataline = "'filtergraph.com'\t\t%s\t\t%s\t\t%s\t\t%s" % args
                    #print "'filtergraph.com': ", dataline
                    datalines.append(dataline)
                else:
                    pass

            else:
                pass
        
        for line in datalines:
            for kw in obj_names:
                mention = find_all_substrings(line, kw)
                if len(mention) > 0:
                    f.write(line + "\n")#line.decode('utf8', "mixed")
                    
                    
        f.close()
        


class KusastroSpider(scrapy.Spider):
    name = 'kusastroSpider'
    #allowed_domains = ['ooruri.kusastro.kyoto-u.ac.jp/']
    start_urls = ['http://ooruri.kusastro.kyoto-u.ac.jp/pipermail/vsnet-alert/']

    def parse(self, response):

        basenodes = response.xpath('//table/tr')
        links = []

        for index, node in enumerate(basenodes):

            #check month and year, month == month_now, year == year_now
            #then extract links from the corresponding thread and enter it
            time_and_link_parts = node.xpath('td/a/@href').extract_first()
            #print(time_and_link_parts)
            
            dateInR = datefinder.find_dates(str(time_and_link_parts))
            dateInR = [d for d in dateInR]
            #print(dateInR)
            if dateInR:
                #if dateInR[0].month == datetime.date.today().month and dateInR[0].year == datetime.date.today().year:
                if dateInR[0].year >= 2020: #datetime.date.today().year:
                    links.append(time_and_link_parts)
                else:
                    pass
            else:
                pass
            print(links)
        #follow pagination links
        for link in links:
            f = io.open(os.path.join(os.path.dirname(os.path.abspath(os.pardir)), "crawling_results/kusastro")+'.txt', "w", encoding = 'utf-8')#+str(datetime.date.today().isoformat())
            f.write(u'website\t\tobject\t\tdate\t\tentry\n')
            if link:
                next_url = link.encode('utf-8')
                #base_url = u"http://ooruri.kusastro.kyoto-u.ac.jp/pipermail/vsnet-alert/"
                #next_page_url_joined = base_url + next_url
                next_page_url_joined = response.urljoin(link)
                print(next_page_url_joined)
                yield scrapy.Request(url=next_page_url_joined, callback = self.check_key_objects, meta={'archivo': f})
    
    def check_key_objects(self, response):
        f = response.meta['archivo']

        entries = response.xpath('//li/a[@href]/text()').extract()
        #entries = [e.encode('utf-8') for e in entries]

        dateInR = datefinder.find_dates(str(response.xpath('//p/i').extract()[-1]))
        dateInR = [d for d in dateInR]
        
        for entry in entries:
            for kw in obj_names:
                
                mention = find_all_substrings(entry, kw)
                if len(mention) > 0:
                    last_position = -1
                    #entry.decode("utf-8", "mixed")
                    args = ("'ooruri.kusastro.kyoto-u.ac.jp/': ", kw, [d.isoformat() for d in dateInR], entry)
                    try:
                        dataline = "%s\t\t%s\t\t%s\t\t%s\n" % args
                    except UnicodeDecodeError:
                        print("ERROR", args)

                    
                    f.write(dataline)
        f.close()

"""-----------------------------------------------"""
# def schedule_next_crawl(null):#, hour, minute):
#     print("\n\n\nHELLO I M HERE CHECKING\n\n\n")
#     # tomorrow = (
#     #     datetime.datetime.now() + datetime.timedelta(days=1)
#     #     ).replace(hour=hour, minute=minute, second=0, microsecond=0)
#     # sleep_time = (tomorrow - datetime.datetime.now()).total_seconds()
#     reactor.callLater(10, crawl)

# def crawl():
    #     d = crawl_job()
    #     #reactor.run()
    #     # crawl everyday at 1pm
    #     #d.addCallback(schedule_next_crawl)#, hour=11, minute=30)

if __name__ == "__main__":

    def crawl_job():
        """
        Job to start spiders.
        Return Deferred, which will execute after crawl has completed.
        """
        configure_logging()
        runner = CrawlerRunner()
        runner.crawl(AstrospiderSpider)
        runner.crawl(FilterGraphSpider)
        runner.crawl(KusastroSpider)
        d = runner.join()
        #d.addBoth(lambda _: reactor.stop())
        return d

    task = LoopingCall(lambda: crawl_job())
    task.start(60*60*24)# * 10)
    reactor.run()


#It's better to schedule the next crawl using callbacks from runner.crawl()
"""snippets to run spiders together without schedule"""
    # process = CrawlerProcess({
    #         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    #     })
    # process.crawl(AstrospiderSpider)
    # process.crawl(FilterGraphSpider)
    # process.crawl(KusastroSpider)
    #process.start(stop_after_crawl=False) # the script will block here until all crawling jobs are finished
    # configure_logging()
    # runner = CrawlerRunner()
    # runner.crawl(AstrospiderSpider)
    # runner.crawl(FilterGraphSpider)
    # runner.crawl(KusastroSpider)
    # d = runner.join()
    # d.addBoth(lambda _: reactor.stop())

    # reactor.run() # the script will block here until all crawling jobs are finished


#to run from other scripts
# if __name__ == "__main__":
#     process = CrawlerProcess({
#         'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
#     })
#     process.crawl(AstrospiderSpider)
#     process.start()

"""# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler

from Demo.spiders.baidu import YourSpider

process = CrawlerProcess(get_project_settings())
scheduler = TwistedScheduler()
scheduler.add_job(process.crawl, 'interval', args=[YourSpider], seconds=10)
scheduler.start()
process.start(False)
"""


"""from twisted.internet import reactor
from quotesbot.spiders.quotes import QuotesSpider
from scrapy.crawler import CrawlerRunner

def run_crawl():
    
    runner = CrawlerRunner({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        })
    deferred = runner.crawl(QuotesSpider)
    # you can use reactor.callLater or task.deferLater to schedule a function
    deferred.addCallback(reactor.callLater, 5, run_crawl)
    return deferred

run_crawl()
reactor.run()   # you have to run the reactor yourself
"""
