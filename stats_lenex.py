from datetime import date
import json
import random
import lenexpy
from lenexpy.models.agegroup import AgeGroup
from lenexpy.models.constructor import Constructor
from lenexpy.models.course import Course
from lenexpy.models.event import Event
from lenexpy.models.gender import Gender
from lenexpy.models.lenex import Lenex
from lenexpy.models.meet import Meet
from lenexpy.models.pool import Pool, TypePool
from lenexpy.models.session import Session
from lenexpy.models.swimstyle import SwimStyle
from lenexpy.models.club import Club
from lenexpy.models.athelete import Athlete
from lenexpy.models.result import Result
from lenexpy.models.swimtime import SwimTime
from lenexpy.models.ranking import Ranking

path_input = r"C:\Users\2008d\Downloads\swim.lxf"
path_output = r"output.lxf"
lenex = lenexpy.fromfile(path_input)
event_ids = {}


def parse_event(order, stroke, distance, gender):
    event_ids[(stroke, distance, gender)] = 100+order
    return Event(
        eventid=100+order,
        number=order,
        order=order,
        preveventid=-1,
        gender=Gender(gender) if gender else None,
        swimstyle=SwimStyle(
            distance=distance,
            relaycount=1,
            stroke=stroke,
            swimstyleid=order
        ),
        agegroups=[AgeGroup(
            id=order+100_000,
            agemin=-1,
            agemax=-1,
            gender=Gender(gender) if gender else None,
            rankings=[]
        )],
    )


with open("output/2_itogi.json", "rb") as file:
    athletes = json.load(file)
with open('output/2_distances.json', 'rb') as file:
    distances = json.load(file)

session = Session(
    number=1,
    date=date.today(),
    events=[parse_event(order, ev[0], ev[1], ev[2])
            for order, ev in enumerate(distances, start=1)]
)
lenex.meet.sessions = [session]
rankings = {}

clubs = {}
for athl in athletes:
    club, city = athl.get('team'), athl['city']
    if club:
        clubname = f'{club} ({city})'
    else:
        clubname = city
    club_obj = clubs.get(clubname)
    if club_obj is None:
        club_obj = Club(name=clubname, athletes=[])
        clubs[clubname] = club_obj
    athlete = Athlete(
        random.randint(1_000, 1_000_000),
        firstname=athl['first_name'],
        lastname=athl['last_name'],
        birthdate=date.fromisoformat(f"{athl['birth_year']}-01-01"),
        gender=athl['gender'],
        results=[],
        license=athl['rank']
    )
    club_obj.athletes.append(athlete)
    for res in athl['results']:
        resultid = random.randint(1_000, 1_000_000)
        result = Result(
            eventid=event_ids[(
                res['stroke'], res['distance'], athl['gender'])],
            swimTime='00:'+res['result'] if res['result'] else None,
            resultid=resultid,
            points=res['points'])
        athlete.results.append(result)

        key = (res['stroke'], res['distance'], athl['gender'])
        dist_rank = rankings.setdefault(key, {})
        dist_rank[resultid] = int(res['place']) if res['place'] else -1

for event in lenex.meet.sessions[0].events:
    agegroup = event.agegroups[0]
    ranks = rankings.get((event.swimstyle.stroke,
                          event.swimstyle.distance, event.gender))
    if not ranks:
        continue
    ranks = sorted(ranks.items(), key=lambda item: item[1])
    for resid, place in ranks:
        agegroup.rankings.append(
            Ranking(order=place, place=place, result_id=resid))
lenex.meet.clubs = list(clubs.values())
print(lenex.meet.clubs)

lenexpy.tofile(lenex, path_output)
