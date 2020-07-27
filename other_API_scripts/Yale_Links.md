# Yale ArchivesSpace Python Scripts

### Links to Github Repos

[Yale ArchivesSpace Committee Data Cleanup Workgroup](https://github.com/YaleArchivesSpace/data_cleanup_workgroup)

A handful of scripts and queries written for Yale's ArchivesSpace PUI implementation project. Includes scripts to update
publication status, machine-actionable restrictions, notes, subrecords, and more.

[apispace](https://github.com/ucancallmealicia/apispace)

Partially-finished Python package with numerous functions which use CSVs to interact with the API. The most complete
portion is the description.py submodule. Most of the apispace functions, as well as info about the overall design of the package, 
are documented in the (in-progress) apispace README. 

Note: During testing the login info was hard-coded into the config.py file. The current config file setup, which uses a
JSON file to set login variables in the config.py file, has not been thoroughly tested and is probably _not_ the best 
approach.

[archivesspace-api](https://github.com/ucancallmealicia/archivesspace-api-public)

Assortment of one-off scripts written for metadata projects at Yale. Includes scripts to update enumeration value positions,
link top containers to archival objects, create and update notes, update locations, add container types, audit barcodes,
and more. Some scripts are old and in need of updating.

[archivesspace-collection-control-toolbox](https://github.com/ucancallmealicia/archivesspace-collection-control-toolbox)

Toolbox of container, location, and restriction-related functions written for the ArchivesSpace member forum in 
July 2017. Also includes a test GUI for creating collection control data. Needs to be updated.
