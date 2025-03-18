# Project brainstorming doc 

This is a scratchboard for project plans.


## 20250124
- pulled observation data for a single station
- to keep things simple, focus just on temperature data. 

- first table in database should be a fact table with all station ids, states,
and locations.
- raw data layer should have raw json data straight from the api.


>[!TODO]
> - [ ] research how geo data is stored in postgres
> - [ ] try making simple geo visuals in superset 
> - [ ] handle pagination in api runner
> - [ ] look into design patterns for API runner


## 20250311 - rethinking project structure

I'm starting to confuse myself with how logic is laid out, so let me just write
everything out here and figure out how to refactor it. 

- Pull data from api
    - have an abstraction that calls the API for me, all I need to do in any one
      function is to specify the url and format the unstructured output with
      metadata about the call
    - check cache: check if this api has already been called

- save the data to raw layer (json cache)

- move data from cache to database- processing the unstructured data accordingly


**files**

- apis.py
- cache.py
- ingestion.py







