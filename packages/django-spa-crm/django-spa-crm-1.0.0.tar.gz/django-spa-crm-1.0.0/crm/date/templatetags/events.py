from django import template
import warnings

warnings.warn("To complex! Cleanup this f*** mess!", PendingDeprecationWarning)

register = template.Library()

MONDAY = "poniedziałek"
TUESDAY = "wtorek"
WEDNESDAY = "środa"
THURSDAY = "czwartek"
FRIDAY = "piątek"
SATURDAY = "sobota"
SUNDAY = "niedziela"

MONDAY = 1
TUESDAY = 2
WEDNESDAY = 3
THURSDAY = 4
FRIDAY = 5
SATURDAY = 6
SUNDAY = 7

JAN = "Styczeń"
FEB = "Luty"
MAR = "Marzec"
APR = "Kwiecień"
MAY = "Maj"
JUN = "Czerwiec"
JUL = "Lipiec"
AUG = "Sierpień"
SEP = "Wrzesień"
OCT = "Październik"
NOV = "Listopad"
DEC = "Grudzień"

JAN = 1
FEB = 2
MAR = 3
APR = 4
MAY = 5
JUN = 6
JUL = 7
AUG = 8
SEP = 9
OCT = 10
NOV = 11
DEC = 12

DATES = {
    2013: {
        MONDAY: {
            SEP: [2, 9, 16, 23, 30],
            OCT: [7, 14, 21, 28],
            NOV: [4, 18, 25],
            DEC: [2, 9, 16, 23, 30],
            JAN: [13, 20, 27],
            FEB: [3, 10, 17, 24],
            MAR: [3, 10, 17, 24, 31],
            APR: [7, 14, 28],
            MAY: [5, 12, 19, 26],
            JUN: [2, 9, 16, 23, 30],
            JUL: [],
            AUG: [],
        },
        TUESDAY: {
            SEP: [3, 10, 17, 24],
            OCT: [1, 8, 15, 22, 29],
            NOV: [5, 12, 19, 26],
            DEC: [3, 10, 17],
            JAN: [7, 14, 21, 28],
            FEB: [4, 11, 18, 25],
            MAR: [4, 11, 18, 25],
            APR: [1, 8, 15, 22, 29],
            MAY: [6, 13, 20, 27],
            JUN: [3, 10, 17, 24],
            JUL: [],
            AUG: [],
        },
        WEDNESDAY: {
            SEP: [4, 11, 18, 25],
            OCT: [2, 9, 16, 23, 30],
            NOV: [6, 13, 20, 27],
            DEC: [4, 11, 18],
            JAN: [8, 15, 22, 29],
            FEB: [5, 12, 19, 26],
            MAR: [5, 12, 19, 26],
            APR: [2, 9, 16, 23, 30],
            MAY: [7, 14, 21, 28],
            JUN: [4, 11, 18, 25],
            JUL: [],
            AUG: [],
        },
        THURSDAY: {
            SEP: [5, 12, 19, 26],
            OCT: [3, 10, 17, 24, 31],
            NOV: [7, 14, 21, 28],
            DEC: [5, 12, 19],
            JAN: [2, 9, 16, 23, 30],
            FEB: [6, 13, 20, 27],
            MAR: [6, 13, 20, 27],
            APR: [3, 10, 17, 24],
            MAY: [8, 15, 22, 29],
            JUN: [5, 12, 19, 26],
            JUL: [],
            AUG: [],
        },
        FRIDAY: {
            SEP: [6, 13, 20, 27],
            OCT: [4, 11, 18, 25],
            NOV: [8, 15, 22, 29],
            DEC: [6, 13, 20, 27],
            JAN: [3, 10, 17, 24, 31],
            FEB: [7, 14, 21, 28],
            MAR: [7, 14, 21, 28],
            APR: [4, 11, 18, 25],
            MAY: [9, 16, 23, 30],
            JUN: [6, 13, 20, 27],
            JUL: [],
            AUG: [],
        },
        SATURDAY: {
            SEP: [7, 14, 21, 28],
            OCT: [5, 12, 19, 26],
            NOV: [2, 9, 16, 23, 30],
            DEC: [7, 14, 21, 28],
            JAN: [4, 11, 18, 25],
            FEB: [1, 8, 15, 22],
            MAR: [1, 8, 15, 22, 29],
            APR: [5, 12, 26],
            MAY: [10, 17, 24, 31],
            JUN: [7, 14, 21, 28],
            JUL: [],
            AUG: [],
        },
        SUNDAY: {
            SEP: [8, 15, 22, 29],
            OCT: [6, 13, 20, 27],
            NOV: [3, 10, 17, 24],
            DEC: [1, 8, 15, 22, 29],
            JAN: [5, 12, 19, 26],
            FEB: [2, 9, 16, 23],
            MAR: [2, 9, 16, 23, 30],
            APR: [6, 13, 27],
            MAY: [11, 18, 25],
            JUN: [1, 8, 15, 22, 29],
            JUL: [],
            AUG: [],
        }
    },

    2014: {
        MONDAY: {
            SEP: [8, 15, 22, 29],
            OCT: [6, 13, 20, 27],
            NOV: [3, 10, 17, 24],
            DEC: [1, 8, 15, 22, 29],
            JAN: [5, 12, 19, 26],
            FEB: [2, 9, 16, 23],
            MAR: [2, 9, 16, 23, 30],
            APR: [6, 13, 20, 27],
            MAY: [4, 11, 18, 25],
            JUN: [1, 8, 15, 22, 29],
            JUL: [],
            AUG: [],
        },
        TUESDAY: {
            SEP: [2, 9, 16, 23, 30],
            OCT: [7, 14, 21, 28],
            NOV: [4, 18, 25],
            DEC: [2, 9, 16, 23, 30],
            JAN: [13, 20, 27],
            FEB: [3, 10, 17, 24],
            MAR: [3, 10, 17, 24, 31],
            APR: [7, 14, 21, 28],
            MAY: [5, 12, 19, 26],
            JUN: [2, 9, 16, 23, 30],
            JUL: [],
            AUG: [],
        },
        WEDNESDAY: {
            SEP: [3, 10, 17, 24],
            OCT: [1, 8, 15, 22, 29],
            NOV: [5, 12, 19, 26],
            DEC: [3, 10, 17, 31],
            JAN: [7, 14, 21, 28],
            FEB: [4, 11, 18, 25],
            MAR: [4, 11, 18, 25],
            APR: [1, 8, 15, 22, 29],
            MAY: [6, 13, 20, 27],
            JUN: [3, 10, 17, 24],
            JUL: [],
            AUG: [],
        },
        THURSDAY: {
            SEP: [4, 11, 18, 25],
            OCT: [2, 9, 16, 23, 30],
            NOV: [6, 13, 20, 27],
            DEC: [4, 11, 18],
            JAN: [1, 8, 15, 22, 29],
            FEB: [5, 12, 19, 26],
            MAR: [5, 12, 19, 26],
            APR: [2, 9, 16, 23, 30],
            MAY: [7, 14, 21, 28],
            JUN: [4, 11, 18, 25],
            JUL: [],
            AUG: [],
        },
        FRIDAY: {
            SEP: [5, 12, 19, 26],
            OCT: [3, 10, 17, 24, 31],
            NOV: [7, 14, 21, 28],
            DEC: [5, 12, 19, 26],
            JAN: [2, 9, 16, 23, 30],
            FEB: [6, 13, 20, 27],
            MAR: [6, 13, 20, 27],
            APR: [3, 10, 17, 24],
            MAY: [8, 15, 22, 29],
            JUN: [5, 12, 19, 26],
            JUL: [],
            AUG: [],
        },
        SATURDAY: {
            SEP: [6, 13, 20, 27],
            OCT: [4, 11, 18, 25],
            NOV: [1, 8, 15, 22, 29],
            DEC: [6, 13, 20, 27],
            JAN: [3, 10, 17, 24, 31],
            FEB: [7, 14, 21, 28],
            MAR: [7, 14, 21, 28],
            APR: [11, 18, 25],
            MAY: [2, 9, 16, 23, 30],
            JUN: [6, 13, 20, 27],
            JUL: [],
            AUG: [],
        },
        SUNDAY: {
            SEP: [7, 14, 21, 28],
            OCT: [5, 12, 19, 26],
            NOV: [2, 9, 16, 23, 30],
            DEC: [7, 14, 21, 28],
            JAN: [4, 11, 18, 25],
            FEB: [1, 8, 15, 22],
            MAR: [1, 8, 15, 22, 29],
            APR: [12, 19, 26],
            MAY: [3, 10, 17, 24, 31],
            JUN: [7, 14, 21, 28],
            JUL: [],
            AUG: [],
        }
    }}


@register.simple_tag
def event(weekday, month, year):
    ret = ""
    for a in DATES[year][weekday][month]:
        ret += "%s, " % a
    return ret[:-2]


@register.simple_tag
def event_count(weekday, month, year=2013):
    return len(DATES[year][weekday][month])


@register.simple_tag
def cost(group, which):
    warnings.warn("Magic numbers - to delete", DeprecationWarning)

    if group in (232, 230, 201, 231, 200, 226, 234, 206, 233, 208, 202, 237,
                 238, 211, 204, 239, 235, 205, 240, 241, 218, 212, 242, 236,
                 203, 207):  # ozw, np
        if which == "full":
            return 2100
        if which == "wpisowe":
            return 200
        if which == "jednorazowo":
            return 1350
        if which == "month":
            return 190
        if which == "discount":
            return 140
    elif group in (198, 217, 219, 199, 213, 210, 214, 216, 217):  # aqua
        if which == "full":
            return 1512
        if which == "wpisowe":
            return 162
        if which == "jednorazowo":
            return 850
        if which == "month":
            return 140
        if which == "discount":
            return 90
    elif group in (223, 220):  # dorosli
        if which == "full":
            return 1050
        if which == "wpisowe":
            return 100
        if which == "jednorazowo":
            return 750
        if which == "month":
            return 190
        if which == "discount":
            return 160
    else:
        return "............"


@register.simple_tag
def count(gid):
    return 42
