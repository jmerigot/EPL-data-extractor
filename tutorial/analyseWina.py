import json
import datetime


with open("outputWinamax.json", 'r') as json_file:
    data_dict = json.load(json_file)
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

            interm_dict[data_dict["outcomes"][str(i)]["label"]] = [data_dict["odds"][str(i)],percent_distribution]
            timestamp = main_bet_to_title_dict[bets_keys_list[m]][1]
            dt_object = datetime.datetime.utcfromtimestamp(timestamp)
            formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            interm_dict["time"] = timestamp
            interm_dict["formated_time"] = formatted_date
        match_dict[main_bet_to_title_dict[bets_keys_list[m]][0]] = interm_dict

print(match_dict)
with open('betsWinamax.json', 'w') as json_file:
    json.dump(match_dict, json_file, indent=2)

