This package contains Fleming, which contains a set of routines for doing datetime
manipulation. Named after Sandford Fleming, the father of worldwide standard timezones,
this package is meant to aid datetime manipulations with regards to timezones.

Fleming addresses some of the common difficulties with timezones and datetime objects,
such as performing arithmetic and datetime truncation across a Daylight Savings Time
border. It also provides utilities for generating date ranges and getting unix times
with respect to timezones.

A brief description of each function in Fleming is below. For more detailed usage examples
and descriptions, visit https://github.com/ambitioninc/fleming.

- convert_to_tz: Converts a datetime object into a provided timezone.
- add_timedelta: Adds a timedelta to a datetime object.
- floor: Rounds a datetime object down to the previous time interval.
- ceil: Rounds a datetime object up to the next time interval.
- intervals: Gets a range of times at a given timedelta interval.
- unix_time: Returns a unix time stamp of a datetime object.


