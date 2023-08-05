Pipedrive Python
================

A Python library to interact with the Pipedrive REST API.


Other libs were available, but they tend to be very thing wrappers, basically json in and out.

While this works, as the integration grows the lack of structure and models will make using the API harder and take longer.

This lib aims to have rich types for all resources.

Design Goals
-------------

We are aiming at:

* Rich models and schema. All properties listed and full fledged when possible.
* Good test coverage, partly why models and resources are separated.
* Good hooks for logging and metrics.

Usage
-----

Sample usage:

  from pipedrive import PipedriveAPI
  api = PipedriveAPI('your api token')
  print api.deal.detail(200).user.email # someone@example.com


Creating an activity:

  from activity import Activity
  activity = Activity(raw_data={'subject': "Do something", 'type': "Call me!"})
  created_activity = api.activity.create(activity)
  print created_activity.id


Current Status
--------------

The API is pretty big, and has tons of resources and each one has tons of fields.
We have to be pragmatic: we're only creating the models and resources for the objects we are currently using.

This means that right now very few entities are actually supported. It is, however, awfully easy to add new ones. See for example the activity.Activity model and activity.ActivityResource for a pointer.


TODO
----

Major points:

* Implement errors and normalized response for objects
* Implement metrics and logging callbacks




I needed this, so I made this.

Arthur Debert <arthur@loggi.com>Topic :: Software Development :: Libraries :: Python Modules

