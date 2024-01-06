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

        for next_page in next_page_links:
            yield response.follow(next_page, callback=self.parse_match)

    def parse_match(self, response):
        team_1 = response.css('div.scoreboard_contestant-1 div.scoreboard_contestantLabel::text').get(default='').strip()
        team_2 = response.css('div.scoreboard_contestant-2 div.scoreboard_contestantLabel::text').get(default='').strip()
        concatenated_teams = team_1+team_2
        OddBoards = response.css('div.marketBox')
        match_odds = {}
        for board in OddBoards:
            odd_class = board.css('h2.marketBox_headTitle::text').get(default='').strip()
            oddTypes = board.css('div.marketBox_lineSelection')
            match_odds[str(odd_class)] = {}
            for oddT in oddTypes:
                odd_Name = oddT.css('p.marketBox_label::text').get(default='').strip()
                odd_value = oddT.css('span.oddValue::text').get(default='').strip()
                match_odds[str(odd_class)][str(odd_Name)] = odd_value
        cleaned_title = re.sub(r'[^a-zA-Z0-9]', '', concatenated_teams) 
        cleaned_title = re.sub(r'\s+', '', cleaned_title)
        match_filename = cleaned_title + 'Betclic.json'
        with open(match_filename, 'w') as json_file:
            json.dump(match_odds, json_file, indent=2)




"""    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")"""
