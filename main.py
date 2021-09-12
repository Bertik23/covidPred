import requests
import requests_cache
import datetime
import calendar

# SETTINGS
simulateDays = 150
deathRate = 30413/1683179
population = 10_650_000
infectionTime = 7
# END SETTINGS

# TEMPERATURES
temperatures = {
    1: -2,
    2: -0.6,
    3: 3.1,
    4: 7.9,
    5: 12.9,
    6: 16,
    7: 17.6,
    8: 17.7,
    9: 13.3,
    10: 8.2,
    11: 2.9,
    12: -0.5,
    13: -2
}
# END TEMPERATURES

requests_cache.install_cache()

covidData = requests.get(
    "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19"
    "/nakazeni-vyleceni-umrti-testy.json"
).json()
ockoData = requests.get(
    "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19"
    "/ockovani.json"
).json()

ockoConcatData = {}
for item in ockoData["data"]:
    if not item["datum"] in ockoConcatData:
        ockoConcatData[item["datum"]] = {}
    ockoConcatData[item["datum"]]["prvnich_davek"] = ockoConcatData[
        item["datum"]].get("prvnich_davek", 0) + item["prvnich_davek"]
    ockoConcatData[item["datum"]]["druhych_davek"] = ockoConcatData[
        item["datum"]].get("druhych_davek", 0) + item["druhych_davek"]
    ockoConcatData[item["datum"]]["celkem_davek"] = ockoConcatData[
        item["datum"]].get("celkem_davek", 0) + item["celkem_davek"]

modCovidData = {}
for item in covidData["data"]:
    modCovidData[item["datum"]] = item


def lerp(val1, val2, t):
    return val1 + (val2-val1)*t


def linstep(val, start, stop):
    return (val - start)/(stop - start)


def getR(date):
    date = str(date)
    week1 = 0
    week2 = 0
    for dayDelta in range(-7, 0):
        week1 += modCovidData[
            str(
                datetime.date.fromisoformat(date)
                + datetime.timedelta(days=dayDelta)
            )
        ]["prirustkovy_pocet_nakazenych"]
    i = 0
    for dayDelta in range(-12, -5):
        week2 += modCovidData[
            str(
                datetime.date.fromisoformat(date)
                + datetime.timedelta(days=dayDelta)
            )
        ]["prirustkovy_pocet_nakazenych"]
    return week1/week2


def predR(date):
    return R(date-datetime.timedelta(days=1)) * (1 + (0.03*(
        getTemp(date-datetime.timedelta(days=1))
        - getTemp(date)
    )))


def getTemp(date: datetime.date):
    p = linstep(
        date,
        date.replace(day=1),
        date.replace(day=calendar.monthrange(date.year, date.month)[1])
    )
    return lerp(temperatures[date.month], temperatures[date.month+1], p)


def R(date):
    if date <= datetime.date.today():
        return getR(date)
    else:
        return predR(date)


thisDay = datetime.date.today() - datetime.timedelta(days=infectionTime+1)
simulatedDays = []
for day in range(simulateDays):
    simulatedDays.append(thisDay)
    thisDay += datetime.timedelta(days=1)
    r = R(thisDay)
    # print(thisDay, r)
    predDay = thisDay+datetime.timedelta(days=infectionTime)
    # print(predDay)
    modCovidData[str(predDay)] = {}
    modCovidData[
        str(predDay)
    ]["prirustkovy_pocet_nakazenych"] = modCovidData[
        str(thisDay)
    ]["prirustkovy_pocet_nakazenych"] * r
    print(
        predDay, R(predDay),
        modCovidData[
            str(thisDay)
        ]["prirustkovy_pocet_nakazenych"] * r
    )


print(getTemp(datetime.date.today()))
