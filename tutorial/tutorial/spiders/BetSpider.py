from pathlib import Path
import re
import scrapy
import json


class BetSpider(scrapy.Spider):
    name = "betclic"

    def start_requests(self):
        urls = [
            "https://www.betclic.fr/football-s1/angl-premier-league-c3",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        # Extracting all dates from the page
        results = {}
        scoreboards = response.css('a.cardEvent')
        for scoreboard in scoreboards:
            contestant_1 = scoreboard.css('div.scoreboard_contestant-1 div.scoreboard_contestantLabel::text').get(default='').strip()
            contestant_2 = scoreboard.css('div.scoreboard_contestant-2 div.scoreboard_contestantLabel::text').get(default='').strip()
            match_time = scoreboard.css('div.event_infoTime::text').get(default='').strip()
            odds = scoreboard.css('span.oddValue::text').getall()
            bet_percentage = scoreboard.css('div.progressBar_fill::attr(style)').re(r'width: (\d+)%')


            results[f"{contestant_1} - {contestant_2}"] = { 'match_time': match_time,
                'odds': odds,
                'bet_percentage': bet_percentage,
            }
        
        with open('betsBetclic.json', 'w') as json_file:
            json.dump(results, json_file, indent=2)

        next_page_links = response.css('a.cardEvent::attr(href)').getall()
        print(next_page_links)

        for next_page in next_page_links:
            yield response.follow(next_page, callback=self.parse_match)

    def parse_match(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
        raise error


"""    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")"""
