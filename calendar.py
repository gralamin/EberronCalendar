#!/usr/bin/env python
#-*- mode:  python; fill-column: 80; comment-column: 80; -*-
import json
import sys
import argparse
import random
import math

random.seed(727)

NEW_MOON_SYMBOL = "&#8226;"
FULL_MOON_SYMBOL = "&#186;"

def printSkipDays(skippingDays):
    if skippingDays == 1:
        print "... Skipping 1 day ..."
    else:
        print "... Skipping %d days ..." % skippingDays

class Day:
    def __init__(self, name):
        self.name = name

class Month:
    def __init__(self, name, length):
        self.length = int(length)
        self.name = name

class Season:
    def __init__(self, month, day, name):
        self.month = month
        self.day = int(day)
        self.name = name

    def isStarting(self, month, day):
        return self.month == month and self.day == day

    def __str__(self):
        return self.name

class Event(object):
    def __init__(self, month, day, name, notes):
        self.month = month
        self.day = int(day)
        self.name = name
        self.notes = notes
        super(Event, self).__init__()

    def isOnDate(self, monthName, day):
        return monthName == self.month.name and day == self.day

    def __str__(self):
        return "[OOC=\"%s\"]%s[/OOC]" % (self.name, self.notes)

class Festival(Event):
    def __str__(self):
        return "[OOC=\"Festival: %s\"]%s[/OOC]" % (self.name, self.notes)

class Calendar:
    def __init__(self, inFile):
        f = json.load(inFile)
        self.name = f["name"]
        self.designation = f["designation"]
        self.abbreviation = f["abbreviation"]
        self.months = []
        for i in f["months"]:
            self.months.append(Month(i["name"], i["days"]))
        self.seasons = []
        for i in f["seasons"]:
            self.seasons.append(Season(self.months[i["month"] - 1], i["day"],
                                       i["name"]))
        self.days = []
        for i in f["days"]:
            self.days.append(Day(i))
        self.events = []
        for i in f["events"]:
            if i["type"] == "festival":
                self.events.append(Festival(self.months[i["month"] - 1],
                                            i["day"], i["name"], i["notes"]))
            else:
                self.events.append(Event(self.months[i["month"] - 1],
                                         i["day"], i["name"], i["notes"]))
        self.yearLength = sum([a.length for a in self.months])
        self.startDate = f["startDate"]
        self.startWeekDay = f["startWeekDay"] - 1
        self.startYear = f["startYear"]
        inFile.seek(0)

    def getDayOfYear(self, day, month):
        return self.months.index(month) * 28 + day

    def display(self, moons=None, planes=None, numYears=1):
        firstDay = self.startDate
        firstWeekDay = self.startWeekDay
        daysSkipped = 0
        if (numYears == 1):
            print "[size=5]%s Calendar %d %s (%s)[/size]" % (self.name,
                                                             self.startYear,
                                                             self.designation,
                                                             self.abbreviation)
        else:
            finalYear = self.startYear + numYears - 1
            print "[size=5]%s Calendar %d-%d %s (%s)[/size]" % \
                (self.name, self.startYear, finalYear, self.designation,
                 self.abbreviation)
        for i in range(0, numYears):
            dayOfYear = 0
            curYear = self.startYear + i
            for month in self.months:
                print ""
                print "[size=3]%s[/size]" % month.name
                if planes:
                    planeList = []
                    for plane in planes:
                        v, i = plane.getPlaneAtDate(dayOfYear, curYear, self)
                        if (v == "Coterminous"):
                            planeList.append("[u]%s:[/u] [color=Red]Coterminous[/color] for %d days" % \
                                             (plane.name, i))
                        elif (v == "Remote"):
                            if "Dal Quor" in plane.name:
                                planeList.append("Dal Quor is still remote")
                                continue
                            planeList.append("[u]%s:[/u] [color=Green]Remote[/color] for %d days" % \
                                             (plane.name, i))
                        else:
                            planeList.append("[u]%s:[/u] %s for %d days" % \
                                             (plane.name, v, i))
                    if len(planeList) > 0:
                        print "[spoiler=Planar activity]"
                        for item in planeList:
                            print item
                        print "[/spoiler]"
                day = firstDay
                weekDay = firstWeekDay
                if daysSkipped > 0:
                    printSkipDays(daysSkipped)
                    daysSkipped = 0
                print self._genDateEvents(weekDay, day, month, curYear,
                                          force=True, moons=moons)
                while (day < month.length):
                    day += 1
                    weekDay += 1
                    dayOfYear += 1
                    weekDay = weekDay % len(self.days)
                    check = self._genDateEvents(weekDay, day, month,
                                                curYear, moons=moons)
                    if check is None:
                        daysSkipped += 1
                    if check is not None:
                        if daysSkipped > 0:
                            printSkipDays(daysSkipped)
                        daysSkipped = 0
                        print check
                firstDay = 1
                firstWeekDay = (weekDay + 1) % len(self.days)

    def _genDateEvents(self, weekdayIndex, day, month, year, force=False,
                       moons=None):
        # weekday, date, Month, year
        monthName = month.name
        dateFormat = "[b]%s %d %s %d %s:[/b] %s"
        eventList = [a for a in self.events if a.isOnDate(monthName, day)]
        seasonList = [a for a in self.seasons if a.isStarting(month, day)]
        for i in seasonList:
            eventList.append("Start of %s" % str(i))
        weekday = self.days[weekdayIndex].name
        dayOfYear = 0
        for curMonth in self.months:
            if curMonth == month:
                break
            dayOfYear += curMonth.length
        dayOfYear += day
        if moons:
            for moon in moons:
                v = moon.getMoonStatus(dayOfYear, year, self.yearLength)
                if (v == "Full"):
                    eventList.append("[i]%s:[/i] %s" % (moon.name,
                                                        FULL_MOON_SYMBOL))
                elif (v == "New"):
                    eventList.append("[i]%s:[/i] %s" % (moon.name,
                                                        NEW_MOON_SYMBOL))
        if force or len(eventList) > 0:
            eventString = ""
            for item in eventList:
                eventString += str(item)
                if item != eventList[-1]:
                    eventString += ", "
            return dateFormat % (weekday, day, monthName, year,
                                 self.abbreviation, eventString)
        return None

class Moon:
    def __init__(self, name, period, firstFullDay, startingYear):
        self.name = name
        self.period = period
        self.firstFullDay = firstFullDay
        self.startingYear = startingYear

    def getMoonStatus(self, dayOfYear, year, yearLength):
        numDays = (year - self.startingYear) * yearLength + dayOfYear - \
                  self.firstFullDay
        daysIntoPeriod = numDays % self.period
        if daysIntoPeriod < 0:
            daysIntoPeriod += self.period + 1
            # -5 with a period of 23 actually means 19
        # Some assumptions: 1/28 period = Full, 1/28 = New. 13/28 waning, 13/28
        #waxing.
        if daysIntoPeriod < self.period / 28:
            return "Full"
        elif daysIntoPeriod < self.period * 14 / 28:
            return "Waning"
        elif daysIntoPeriod < self.period * 15 / 28:
            return "New"
        else:
            return "Waxing"


def genMoons(inFile):
    f = json.load(inFile)
    moons = []
    for i in f["satellites"]:
        moons.append(Moon(i["name"], i["period"], i["full"], f["startYear"]))
    inFile.seek(0)
    return moons

class Plane(object):
    def __init__(self, name, coterminousMonth, coterminousDay, daysConterminous,
                 daysRemote, daysWaning, daysWaxing, planeStartYear):
        self.name = name
        self.coterminousDay = int(coterminousDay)
        self.coterminousMonth = coterminousMonth
        self.coterStart = 0
        self.coterEnd = daysConterminous - 1
        self.waneStart = self.coterEnd + 1
        self.waneEnd = self.waneStart + daysWaning - 1
        self.remoteStart = self.waneEnd + 1
        self.remoteEnd = self.remoteStart + daysRemote - 1
        self.waxStart = self.remoteEnd + 1
        self.waxEnd = self.waxStart + daysWaxing - 1
        self.planeStartYear = planeStartYear

    def getPlaneAtDate(self, dayOfYear, year, calendar):
        effectiveDay = (year - self.planeStartYear) * calendar.yearLength
        coterminousMod = 0
        for month in calendar.months:
            if month == self.coterminousMonth:
                break
            coterminousMod += month.length
        coterminousMod += self.coterminousDay
        effectiveDay += dayOfYear + 1 - coterminousMod
        effectiveDay = effectiveDay % (self.waxEnd + 1)
        if effectiveDay <= self.coterEnd:
            return "Coterminous", self.coterEnd - effectiveDay + 1
        elif effectiveDay <= self.waneEnd:
            return "Waning", self.waneEnd - effectiveDay + 1
        elif effectiveDay <= self.remoteEnd:
            return "Remote", self.remoteEnd - effectiveDay + 1
        else:
            return "Waxing", self.waxEnd - effectiveDay + 1

    def getYearCount(self, calendar):
        return int(math.ceil((self.waxEnd + 1) / float(calendar.yearLength)))

class RandomPlane(object):
    def __init__(self, dayCLow, dayCHigh, dayCDist, dayRLow, dayRHigh,
                 dayRDist, dayWaLow, dayWaHigh, dayWaDist, dayWxLow,
                 dayWxHigh, dayWxDist, name):
        self.dayCLow = int(dayCLow)
        self.dayCHigh = int(dayCHigh)
        self.dayCDist = dayCDist
        self.dayRLow = int(dayRLow)
        self.dayRHigh = int(dayRHigh)
        self.dayRDist = dayRDist
        self.dayWaLow = int(dayWaLow)
        self.dayWaHigh = int(dayWaHigh)
        self.dayWaDist = dayWaDist
        self.dayWxLow = int(dayWxLow)
        self.dayWxHigh = int(dayWxHigh)
        self.dayWxDist = dayWxDist
        self.yearMap = {}
        self.name = name

    def pregen(self, planeStartYear, startYear, calendar):
        for i in range(planeStartYear, startYear + 1):
            if i not in self.yearMap:
                self.generateForYear(i, calendar)

    def generateForYear(self, year, calendar):
        while True:
            daysConterminous = getattr(self, self.dayCDist)(self.dayCLow,
                                                            self.dayCHigh)
            daysRemote = getattr(self, self.dayRDist)(self.dayRLow,
                                                      self.dayRHigh)
            daysWaning = getattr(self, self.dayWaDist)(self.dayWaLow,
                                                       self.dayWaHigh)
            daysWaxing = getattr(self, self.dayWaDist)(self.dayWxLow,
                                                       self.dayWxHigh)
            orbit = Plane(self.name, random.choice(calendar.months),
                          random.uniform(1, calendar.yearLength),
                          daysConterminous, daysRemote, daysWaning, daysWaxing,
                          year)
            for i in range(year, year + orbit.getYearCount(calendar)):
                if i in self.yearMap:
                    for j in range(year, i):
                        del self.yearMap[j]
                    break
                self.yearMap[i] = orbit
            else:
                break

    def linear(self, a, b):
        return random.uniform(a, b)

    def normal(self, a, b):
        mu = (a + b) / 2
        aCutOff = 1.0015 * a
        bCutOff = (1 - 0.0015) * b
        sigma = (bCutOff - aCutOff) / 7.0
        return random.normalvariate(mu, sigma)

    def getPlaneAtDate(self, dayOfYear, year, calendar):
        if year not in self.yearMap:
            self.pregen(year, year, calendar)
        return self.yearMap[year].getPlaneAtDate(dayOfYear, year, calendar)

def genPlanes(inFile, calendar):
    f = json.load(inFile)
    planes = []
    for i in f["planes"]:
        if "rand" in i:
            planes.append(RandomPlane(i["daysCoterminousLowerBound"],
                                      i["daysCoterminousUpperBound"],
                                      i["coterminousDist"],
                                      i["daysRemoteLowerBound"],
                                      i["daysRemoteUpperBound"],
                                      i["remoteDist"],
                                      i["daysCoterminousToRemoteLowerBound"],
                                      i["daysCoterminousToRemoteUpperBound"],
                                      i["waningDist"],
                                      i["daysRemoteToCoterminousLowerBound"],
                                      i["daysRemoteToCoterminousUpperBound"],
                                      i["waxingDist"],
                                      i["name"]
                                  ))
            planes[-1].pregen(f["planeStartYear"], f["startYear"], calendar)
        else:
            month = calendar.months[i["coterminousMonth"] - 1]
            planes.append(Plane(i["name"], month,
                                i["coterminousDay"], i["daysCoterminous"],
                                i["daysRemote"], i["daysCoterminousToRemote"],
                                i["daysRemoteToCoterminous"],
                                f["planeStartYear"]))
    inFile.seek(0)
    return planes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('calendar', type=argparse.FileType('r'),
                        default=sys.stdin)
    args = parser.parse_args()
    c = Calendar(args.calendar)
    m = genMoons(args.calendar)
    p = genPlanes(args.calendar, c)
    c.display(moons=m, planes=p)
