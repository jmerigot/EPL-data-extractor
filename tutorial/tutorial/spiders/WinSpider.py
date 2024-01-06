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
            return
        
        
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
                    percent_distribution = 0

                interm_dict[data_dict["outcomes"][str(i)]["label"] + " odd"] = data_dict["odds"][str(i)]
                interm_dict[data_dict["outcomes"][str(i)]["label"] + " percentage"] = percent_distribution
                timestamp = main_bet_to_title_dict[bets_keys_list[m]][1]
                dt_object = datetime.datetime.utcfromtimestamp(timestamp)
                formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                interm_dict["time"] = timestamp
                interm_dict["formated_time"] = formatted_date
            match_dict[main_bet_to_title_dict[bets_keys_list[m]][0]] = interm_dict

        with open('betsWinamax.json', 'w') as json_file:
            json.dump(match_dict, json_file, indent=2)

        base_url = "https://www.winamax.fr/paris-sportifs/match/"
        matches_keys = [str(key) for key in data_dict["matches"].keys()]
        for key in matches_keys:
            try:
                yield response.follow(base_url+key, callback=self.parse_match, cb_kwargs={'match_id': key})
            except Exception as e:
                print(f"Error following link for key {key}: {e}")
            

    def parse_match(self, response, **kwargs):
        match_id = str(kwargs.get('match_id'))
        javascript_block = response.xpath('//script[contains(., "PRELOADED_STATE")]/text()').get()
        json_match = re.search(r'var PRELOADED_STATE = (\{.*?\});', javascript_block)

        if json_match:
            json_data = json_match.group(1)
            data_dict = json.loads(json_data)
        else:
            return

        match_title = data_dict["matches"][str(match_id)]["title"]
        bets = data_dict["matches"][str(match_id)]["bets"]
        match_dict = {}
        for bet in bets:
            outcomes = data_dict["bets"][str(bet)]["outcomes"]
            bet_name = data_dict["bets"][str(bet)]["betTitle"]
            match_dict[bet_name]={}
            for outcome in outcomes:
                out_label = data_dict["outcomes"][str(outcome)]["label"]
                try:
                    out_percentage = data_dict["outcomes"][str(outcome)]["percentDistribution"]
                except KeyError:
                    out_percentage = 0
                out_odd = data_dict["odds"][str(outcome)]
                match_dict[bet_name][out_label] = {
                    "percentage" : out_percentage,
                    "odds" : out_odd
                }

        cleaned_title = re.sub(r'[^a-zA-Z0-9]', '', match_title) 
        cleaned_title = re.sub(r'\s+', '', cleaned_title)
        match_filename = cleaned_title + 'Winamax.json'
        with open(match_filename, 'w') as json_file:
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
