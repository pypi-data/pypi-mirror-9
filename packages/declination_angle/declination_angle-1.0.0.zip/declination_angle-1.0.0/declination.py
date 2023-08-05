# -*- coding: utf-8 -*-
#Firstly indicated that we are going to use UTF-8 format
import math #Imported the math module
def declination_angle(n): #Defined a function for declination angle
    angle = 23.45*math.sin(360*n/365) #Defined the formula
    return angle

def month(n):#Defined a function to seperate the month on the basis of day number
    if n>=1 and n<=31:
        return "January"#31 days
    elif n>31 and n<=59:
        return "February"#28 days
    elif n>59 and n<=90:
        return "March"#31 days
    elif n>90 and n<=120:
        return "April"#30 days
    elif n>120 and n<=151:
        return "May"#31 days
    elif n>151 and n<=181:
        return "June"#30 days
    elif n>181 and n<=212:
        return "July"#31 days
    elif n>212 and n<=243:
        return "August"#31 days
    elif n>243 and n<=273:
        return "September"#30 days
    elif n>273 and n<=304:
        return "October"#31 days
    elif n>304 and n<=334:
        return "November"#30 days
    elif n>334 and n<=365:
        return "December"#31 days
    
def day(n):#Function to make the day number to month number
    #For example n = 53 will become 22(53-31)
    if n>=1 and n<=31:#Number of days before the month are indicated
        return n#0 days before January
    elif n>31 and n<=59:
        return n-31#31 days before February
    elif n>59 and n<=90:
        return n-59#59 days days before March
    elif n>90 and n<=120:
        return n-90#90 days before April
    elif n>120 and n<=151:
        return n-120#120 days before May
    elif n>151 and n<=181:
        return n-151#151 days before June
    elif n>181 and n<=212:
        return n-181#181 days before July
    elif n>212 and n<=243:
        return n-212#212 days before August
    elif n>243 and n<=273:
        return n-243#243 days before September
    elif n>273 and n<=304:
        return n-273#273 days before October
    elif n>304 and n<=334:
        return n-304#304 days before November
    elif n>334 and n<=365:
        return n-334#334 days before December

def declination(n):
    angle = declination_angle(n)
    mon = month(n)
    day_month = day(n)
    return str(u"The Declination angle(δ) on",day_month,"of",mon,"is",angle)
