# -*- coding:utf-8 -*-
# from pyICSParser import pyiCalendar
import pyiCalendar
import datetime
mycal = pyiCalendar.iCalendar()
print "pyICSParser iCalendar object version:%s"%(mycal.version)

def testLoader():
    rscpath="../rsc/"
    icsfile = "/Users/chevrier/Dropbox/entolusis/1-annum/www/ics/Moon_New_Paris_2006_2016.ics"
#     mycal.local_load(rscpath+"SO22545231.ics")
    mycal.local_load(icsfile)
    dtstart = "20140101"
    dtend = "20150131"
#     mycal.isCalendarFileCompliant(iCalendarFile=icsfile,_ReportNonConformance = True)
    dates = mycal.get_event_instances(dtstart,dtend)
    print dates
#     icsfile2 = "/Users/chevrier/Dropbox/entolusis/1-annum/www/ics/mcv_birthdays_v2014_.ics"
#     mycal.local_load(icsfile2)
#     dates = mycal.get_event_instances(dtstart,dtend)
#     print dates
    """
                    mycal.local_load(self.defaultpath+cal["ical"])
                    dates = mycal.get_event_instances(new_dtstart,new_dtend)
    
    """

def testGenerator():
    """ test for the generator"""
    sICalendar = "VOID"
    calGen = pyiCalendar.iCalendar()
#     calGen.dVCALENDAR={}
    listDates = [datetime.datetime(2014,8,1),datetime.datetime(2014,9,9),datetime.datetime(2014,10,8)]
    calGen.events=[{"DESCRIPTION":"test","RDATE":listDates}]
    sICalendar = calGen.Gen_iCalendar()
    print sICalendar
    return sICalendar

testLoader()