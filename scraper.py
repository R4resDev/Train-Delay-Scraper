import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

urls = ["https://mersultrenurilor.infofer.ro/ro-RO/Rute-trenuri/Targoviste/Bucuresti-Nord", "https://mersultrenurilor.infofer.ro/ro-RO/Rute-trenuri/Bucuresti-Nord/Targoviste"]
for url in urls:
    departureStationName = url.split("/")[-2]
    arrivalStationName = url.split("/")[-1]

    current_date = datetime.now().strftime("%Y-%m-%d")
    departureDate = datetime.now().strftime("%d.%m.%Y 0:00:00")

    # https://curlconverter.com/
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5,de;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://mersultrenurilor.infofer.ro',
        'Referer': url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    session = requests.Session()
    response_get = session.get(
        url,
        headers=headers
    )

    soup_get = BeautifulSoup(response_get.text, "html.parser")
    confirmationKey = soup_get.find("input", attrs={"name" : "ConfirmationKey"})["value"]
    requestVerificationToken = soup_get.find("input", attrs={"name" : "__RequestVerificationToken"})["value"]

    data = {
        'ArrivalStationName': arrivalStationName,
        'ArrivalTrainRunningNumber': '',
        'ChangeStationName': '',
        'ConnectionsTypeId': '1',
        'DepartureDate': departureDate,
        'DepartureStationName': departureStationName,
        'DepartureTrainRunningNumber': '',
        'MinutesInDay': '0',
        'OrderingTypeId': '0',
        'TimeSelectionId': '0',
        'ReCaptcha': '',
        'ConfirmationKey': confirmationKey,
        'IsBikesServiceRequired': 'False',
        'IsOnlineBuyingRequired': 'False',
        'IsBarRestaurantServiceRequired': 'False',
        'IsSleeperCouchetteServiceRequired': 'False',
        'BetweenTrainsMinimumMinutes': '',
        'IsSearchWanted': 'False',
        'IsReCaptchaFailed': 'False',
        '__RequestVerificationToken': requestVerificationToken,
    }

    response = session.post(
        'https://mersultrenurilor.infofer.ro/ro-RO/Itineraries/GetItineraries',
        headers=headers,
        data=data,
    )

    soup = BeautifulSoup(response.text, "html.parser")
    all_lists = soup.find_all("li")
    trains = []
    for li in all_lists:
        if li.has_attr("id") and li["id"].startswith("li-itinerary-"):
            trains.append(li)

    csv_file = f"data_{departureStationName}_{arrivalStationName}.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("Date, Train ID, Departure Time, Arrival Time, Delay\n")

        for idx in range(len(trains)):
            train_id = trains[idx].find("a")
            if train_id:
                train_id = train_id.text.strip()
                times = trains[idx].find_all("span", class_ = "text-1-4rem")
                if len(times) > 1:
                    departure = times[0].text.strip()
                    arrival = times[1].text.strip()
                else:
                    departure, arrival = None, None
                delay = trains[idx].find("span", class_ = "color-firebrick")
                if delay:
                    delay = delay.text.strip()
                else:
                    delay = "0 min"
                f.write(f"{current_date}, {train_id}, {departure}, {arrival}, {delay}\n")