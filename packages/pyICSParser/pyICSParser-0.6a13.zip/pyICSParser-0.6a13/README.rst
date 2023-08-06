==============================
pyICSParser - ICALENDAR Parser
==============================

pyICSParser is an icalendar parser (parser for .ics or ical parser files) as defined 
by RFC5545 (previously RFC2445) into typed structure and returns 
json structure with explicit dates [[dates, description, uid]] for each instance


Usage
-----
* Enumerator of iCalendar file::

    mycal = icalendar.ics()\n
    mycal.local_load(icsfile)\n
    dates = mycal.get_event_instances(start,end)\n
    #dates will contain the json with all explicit dates of the events spec'ed by the iCalendar file\n

* Validator::

    mycal = icalendar.ics()\n
    perfect = mycal.isCalendarFileCompliant(icsfile) \n
    #When the file does not show any deviance from RFC5545, perfect will hold True \n
    #Console will display all non-conformance per lines

Versions
=========

* Pre-alpha
	-v0.0.1: first pre-alpha
	
	-v0.0.27: fixed the dtstart to dtend problem for holiday

* alpha
	-0.4.x: first fully tested handling days - remains to be done is handling of
	time of events (test vectors are actual icalendar files)
	
	-0.5.x: added support for EXDATE
	
	-0.6.x: added support for DURATION and when DTEND no present
	
Future developments
--------------------
1. handle of datetime (currently only handles date)
2. handle of multiple EXRULE,  RRULE as per icalendar spec

Thanks
-------
* http://www.tele3.cz/jbar/rest/rest.html: reST to HTML & reST validator
* http://guide.python-distribute.org/contributing.html: registering a package on pypi and password information
* http://guide.python-distribute.org/creation.html: uploading a package to pypi
* http://blog.msbbc.co.uk/2007/06/using-googles-free-svn-repository-with.html: how to use google codes, subclipse and eclipse
