from pathlib import Path
import re
import scrapy
import json
import datetime



class WinSpider(scrapy.Spider):
    name = "winamax"

    def start_requests(self):
        urls = [
            "https://www.winamax.fr/paris-sportifs/sports/1/1/1",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

#this block outputs the structured information from a page
    def parse(self, response):
        javascript_block = response.xpath('//script[contains(., "PRELOADED_STATE")]/text()').get()
        json_match = re.search(r'var PRELOADED_STATE = (\{.*?\});', javascript_block)

        if json_match:
            json_data = json_match.group(1)
            data_dict = json.loads(json_data)
        else:
            raise error
        
        
        main_bet_to_title_dict = {str(data_dict["matches"][key]["mainBetId"]): [data_dict["matches"][key]["title"],data_dict["matches"][key]["matchStart"]]  for key in data_dict["matches"]}
        bets_list = [data_dict["bets"][key]["outcomes"] for key in sorted(data_dict["bets"].keys())]# for outcomes in sorted(data_dict["bets"][key].keys())]
        bets_keys_list = sorted(data_dict["bets"].keys())
        match_dict = {}
        for m in range(len(bets_list)):
            interm_dict = {}
            for i in bets_list[m]:
                try:
                    percent_distribution = data_dict["outcomes"][str(i)]["percentDistribution"]
                except KeyError:
                    percent_distribution = None

                interm_dict[data_dict["outcomes"][str(i)]["label"] + " odd"] = data_dict["odds"][str(i)]
                interm_dict[data_dict["outcomes"][str(i)]["label"] + " percentage"] = percent_distribution
                timestamp = main_bet_to_title_dict[bets_keys_list[m]][1]
                dt_object = datetime.datetime.utcfromtimestamp(timestamp)
                formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                interm_dict["time"] = timestamp
                interm_dict["formated_time"] = formatted_date
            match_dict[main_bet_to_title_dict[bets_keys_list[m]][0]] = interm_dict

        print(match_dict)
        with open('betsWinamax.json', 'w') as json_file:
            json.dump(match_dict, json_file, indent=2)

#this block gets the raw information used by the javascript on the page
"""    def parse(self, response):
        javascript_block = response.xpath('//script[contains(., "PRELOADED_STATE")]/text()').get()
        json_match = re.search(r'var PRELOADED_STATE = (\{.*?\});', javascript_block)

        if json_match:
            json_data = json_match.group(1)
            parsed_data = json.loads(json_data)
            with open('outputWinamax.json', 'w') as json_file:
                json.dump(parsed_data, json_file, indent=2)"""


# This blocks gets the page and saves it in html format
"""    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")"""
