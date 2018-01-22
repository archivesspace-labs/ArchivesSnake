Python scripts used to perform various tasks with the ArchivesSpace API developed for the Johns Hopkins University Sherdian Libraries. All scripts and documentation created by Valerie Addonizio, [Eric Hanson](https://github.com/ehanson8), and [Lora Woodford](https://github.com/lorawoodford)

# archivesspace-api

## Authenticating to the API

All of these scripts require a secrets.py file in the same directory that must contain the following text:

	baseURL='[ArchivesSpace API URL]'
	user='[user name]'
	password='[password]'

#### [addBibNumbersAndPost.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/addBibNumbersAndPost.py)
Based on a specified CSV file with URIs and bib numbers, this script posts the specified bib number to the ['user_defined]['real_1'] field for record specified by the URI.

#### [dateCheck.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/dateCheck.py)
Retrieves 'begin,' 'end,' 'expression,' and 'date_type' for all dates associated with all resources in a repository

#### [eadToCsv.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/eadToCsv.py)
Based on a specified file name and a specified file path, this script extracts selected elements from an EAD XML file and prints them to a CSV file.

#### [getAccessionUDFs.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getAccessionUDFs.py)
This GET script retrieves all of the user-defined fields from all of the accessions in the specified repository.

#### [getAccessions.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getAccessions.py)
This GET script retrieves all of the accessions from a particular repository into a JSON file.

#### [getAllArchivalObjectTitles.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getAllArchivalObjectTitles.py)
Retrieves titles from all archival objects in a repository. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectCountByResource.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getArchivalObjectCountByResource.py)
Retrieves a count of archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArchivalObjectsByResource.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getArchivalObjectsByResource.py)
A GET script to extract all of the archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getArrayPropertiesFromAgentsPeopleCSV.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getArrayPropertiesFromAgentsPeopleCSV.py)
This GET script retrieves specific properties, including proprerties that have arrays as values, from the JSON of ArchivesSpace agent_people records. In this example, the 'dates_of existence' property contains an array that must be iterated over. This requires a second level of iteration with 'for j in range (...)' on line 20, which is in addition to the iteration function 'for i in range (...)' on line 19, which was also found in the getPropertiesFromAgentsPeopleCSV.py script. As with the previous script, it also writes the properties' values into a CSV file which is specified in variable 'f' on line 17.

#### [getPropertiesFromAgentsPeopleCSV.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getPropertiesFromAgentsPeopleCSV.py)
This GET script retrieves specific properties from the JSON of ArchivesSpace agent_people records into a CSV file which is specified in variable 'f' on line 17. In this example, the script retrieves the 'uri,' 'sort_name,' 'authority_id,' and 'names' properties from the JSON records by iterating through the JSON records with the function 'for i in range (...)' on line 19. The f.writerow(....) function on line 20 specifies which properties are retrieved from the JSON and the f.writerow(....) on line 18 specifies header row of the CSV file.  

#### [getResources.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getResources.py)
This GET scripts retrieves all of the resources from a particular repository into a JSON file which is specified in variable 'f' on line 16. This GET script can be adapted to other record types by editing the 'endpoint' variable on line 13 (e.g. 'repositories/[repo ID]/accessions' or 'agents/corporate_entities').

#### [getSingleRecord.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getSingleRecord.py)
This GET script retrieves a single ArchivesSpace record based on the record's 'uri,' which is specified in the 'endpoint' variable on line 13.

#### [getTopContainerCountByResource.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getTopContainerCountByResource.py)
Retrieves a count of top containers associated with archival objects associated with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainerCountByResourceNoAOs.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getTopContainerCountByResourceNoAOs.py)
Retrieves a count of top containers directly associated (not through an archival object) with a particular resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [getTopContainers.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getTopContainers.py)
This GET script retrieves all of the top containers from a particular repository into a JSON file.

#### [getUrisAndIds.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/getUrisAndIds.py)
For the specified record type, this script retrieves URI and the 'id_0,' 'id_1,' 'id_2,' 'id_3,' and a concatenated version of all the 'id' fields.

#### [postContainersFromCSV.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/postContainersFromCSV.py)
This script works to create instances (consisting of top_containers) from a separate CSV file. The CSV file should have two columns, indicator and barcode. The directory where this file is stored must match the directory in the filePath variable. The script will prompt you first for the exact name of the CSV file, and then for the exact resource or accession to attach the containers to.

#### [postNew.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/postNew.py)
This POST script will post new records to a generic API endpoint based the record type, 'agents/people' in this example. This script can be modified to accommodate other data types (e.g. 'repositories/[repo ID]/resources' or 'agents/corporate_entities'). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.  

#### [postOverwrite.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/postOverwrite.py)
This POST script will overwrite existing ArchivesSpace records based the 'uri' and can be used with any ArchivesSpace record type (e.g. resource, accession, subject, agent_people, agent_corporate_entity, archival_object, etc.). It requires a properly formatted JSON file (specified where [JSON File] appears in the 'records' variable on line 13) for the particular ArchivesSpace record type you are trying to post.

#### [resourcesWithNoBibNum.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/resourcesWithNoBibNum.py)
Prints the URIs to a CSV file of all resources in a repository without a bib number stored in the ['user_defined']['real_1'] field.

#### [searchForUnassociatedContainers.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/searchForUnassociatedContainers.py)
Prints the URIs to a CSV file of all top containers that are not associated with a resource or archival object.

#### [unpublishArchivalObjectsByResource.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/unpublishArchivalObjectsByResource.py)
This script unpublishes all archival objects associated with the specified resource. Upon running the script, you will be prompted enter the resource ID (just the number, not the full URI).

#### [updateFindingAidData.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/updateFindingAidData.py)

#### [updateResourceWithCSV.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-api/blob/master/updateResourceWithCSV.py)






# spacewalk

#### [spacewalk.py](https://github.com/jhu-archives-and-manuscripts/spacewalk/blob/master/spacewalk.py)
DSpace to ASpace crosswalking for JHU

We have **DSpace** items with bitstreams filenames like:
  * 01_01_22_33.pdf
  
That needed to be matched to **ASpace** archival objects with instance information like:
  * Box 1-1
  * Folder 22
  * Item 33
  
No other possible match point existed between the DSpace digital surrogates and the ASpace archival objects.  This script does the heavy lifting.

While our situation is unique (and, notably, not IDEAL!), the idea of yanking DSpace handles/bitstreams out with the DSpace (in our case v. 5) API, comparing to ASpace archival objects with the ASpace API (for us, v. 1.5.4), and posting new digital objects back in to ASpace with the API is a repurposable activities others may want to investigate.  So, your specifics will vary, but the basics may stay largely the same!





# MARAC_API_Workshop

These are the resources used in the "There's An API for that!" workshops sponsored by the Mid-Atlantic Regional Archives Conference in 2017. Note that these are the scripts used in the workshop itself. For additional scripts and resources referenced in the workshop, navigate to the [_additional resources_](../master//additional%20resources) subfolder, above.

These scripts and this documentation, combined with the workshop itself, are meant to encourage and empower users to run Python scripts at their home institutions. The following details are meant to be understood in order.


## How do I use these?

First, a necessary disclaimer: **We highly recommend AGAINST making any changes or using any of these scripts against your working, or Production, instance of ArchivesSpace and/or with the only copy of existing Production data.** If you do not have a Development version of AS, you can contact us or show the vagrant you used in class as an example of how one might be set up for you. Note that GET scripts are not that risky, so if you cannot or will not have a Dev instance of AS, you can still try GETs as your familiarize yourself with our scripts. If fear of making mistakes is holding you back, and rightly so, you should investigate options for running a Dev or Virtual Machine (VM) of AS. If your institution decides to ramp up its use of APIs, a testing environment is a necessity.

Second, remember the vagrant box that you were provided in the course of the workshop. That box, now stored locally on the laptop you brought to the workshop, is our gift to you. We encourage truly novice users who may be wary to try anything on real data to play in the vagrant virtual environment first. No matter what you do there you cannot break anything, and if you mess up your data, just blast away the vagrant box using the instructions provided in the workshop slides and then `vagrant up` again!

There's very little data in the default box, but once you have it up and running you can:
+ manually enter data just like you would in AS
+ import your own collections via EAD
+ more advanced users can use our GET scripts to pull down resource records from their own institutional instance of AS and POST them to the vagrant (remember that the vagrant endpoint will begin with http://localhost:8089)


## How do I _run_ these?
This is a subtly different question from the above. This section gives practical advice for how to run these scripts, though it still raises more questions than answers. The first thing you need to know is what operating system (OS) you are using to execute these scripts.  The Mac (or Linux, for that matter) terminal is a command line interface that allows for nearly full control of the Unix-based Mac (or Linux) operating system; conversely, the Windows command prompt (that thing you get when you type "Run > cmd.exe") is essentially just an extension of the old text-based MS DOS operating system and is more limited in what it can do natively.  To help even the playing field a bit, we recommend using CygWin, an application that allows you to utilize a Unix-like terminal on a Windows machine.

* *All users*

   Directories really matter. Whatever directory you download a script to is where a) you need to run that script _from_, b) where that script is going to look for other scripts or files if it's a script that needs other resources (like the barcodes script), and c) put the output files, if the script is creating outputs. So if you download a script and leave it in your Downloads folder, all your resulting output files will also write to that folder. Also, you'll need to navigate to where your scripts are from within the command line/terminal, which is a barrier to novice users. Google "how to change directories in [the command line (Windows)] or [terminal (Mac users)] for advice on how to navigate to your script directory if you need to.

* *Windows users*

   Windows users who attended the workshop will recall that we took steps to install _cygwin_, which is a "Linux-like environment for Windows making it possible to port software running on POSIX systems (such as Linux, BSD, and Unix systems) to Windows." Cygwin allows Windows to communicate with Linux-like applications. Please see our presentation slides to walk yourself through installing cygwin and the packages required to run our scripts. Keep the cygwin installer around, it comes in handy (see immediately below).

   Pro-tip: If you ever run a script and cygwin says something along the lines of "pip: command not found" it means you're missing a package (in that example, the missing package is called pip). Try Googling the error message and you will almost certainly find other people with the same problem; use their answers to determine what package you need to install, and then re-run the cgywin installer. When you get to the Install Packages screen, there is where to look for packages. This isn't a easy pro-tip, just an insight on how these programs work. Attendees will also remember that we cloned the fuzzy wuzzy GitHub repo; this is another way of installing necessary packages.

* *Mac users*

   There is a reason why developers love Macs! You don't need a Unix emulator like Cygwin, but, you may not have all the necessary packages installed. Mac users will remember opening the terminal and having to check for XCode (which we checked with `gcc --version`), installing [Homebrew](https://brew.sh), installing Python with `brew install python` and then checking it installed correctly with `python --version`, installing the requests library (`pip install requests`), and cloning the [fuzzy wuzzy](https://github.com/seatgeek/fuzzywuzzy) library. So while the terminal is generally easier to use, remember that you may encounter other scripts that don't run: you're probably missing packages such as those above. Our best advice is to Google the exact error message that pops up (if one does), and chances are you'll find the solution online. Remember to use our slides as a guide to prepping your workstation if you'd like to run our scripts on a different Mac than the one you used in the workshop.

   Pro-tip:  Mac's *do* come with Python installed by default, however we've gone to the effort of walking you through the creation of a development environment on your Mac laptop during this workshop so that we might (hopefully) avoid some potential "gotchas."  Long story short, if you feel like living (only slightly) dangerously, you can bypass these setup steps and see how far you get with the Python natively installed on your computer.  For more really helpful (if somewhat more than beginner-level) advice, see [The Hitchhiker's Guide to Python](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install/osx/).

More FYIs to read  

   1. You'll always need at least two things to run one of our scripts: _the script itself_ and _the secrets.py file_, and they must both be in the same directory.
   2. A brief description of what each script does follows this long introduction. You used each of these scripts in the workshop itself, and so these descriptions will be familiar. These scripts, as opposed to the ones offered in the [_additional resources_](../master//additional%20resources) subfolder, above, are highly specific to the workshop, but if you're interested in learning Python, it may help to look at a script you've already used.


## Authenticating with [secrets.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/secrets.py)
Note: You're only downloading/editing [secrets.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/secrets.py); secrets._pyc_ is created automatically and you do not need to download or edit it.

Several of our scripts used for interacting with the ArchivesSpace API call a separate secrets.py that should be in the following format:

```
backendurl='YOURBACKENDURL'
user='YOURUSER'
password='YOURPASSWORD'
```
This example mimics an institution's instance of AS and a personal username:
```
backendurl='archivesspace.fakelibrary.edu:8089'
user='archivist21'
password='guest1234'
```
For the vagrant:
```
backendurl='localhost:8089'
user='admin'
password='admin'
```
Once you download, remember to change this secrets file as needed (i.e. you can't leave it set to the vagrant default and then try to connect to your instance of AS).


#### [proPublica.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/proPublica.py)
This script creates and saves a separate file called _proPublicaRecord.json_ containing the results of a proPublica search for "animal."

You can run this script by typing `python proPublica.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script is saved, and an output file named _proPublicaRecord.json_ will appear in the same directory.


#### [postContainerProfiles.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/postContainerProfiles.py)
This script sources from [containerProfiles.json](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/containerProfiles.json) to post container profiles into ArchivesSpace. Both files must be downloaded to the same directory for this script to run. You can edit [containerProfiles.json](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/containerProfiles.json) if you'd like to try posting in different profiles.

You can run this script by typing `python postContainerProfiles.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script, the source .json, and [secrets.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/secrets.py) are all saved.

#### [postBarcodes.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/postBarcodes.py)
This script sources from [barcodes.csv](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/barcodes.csv) to post barcodes into ArchivesSpace. Both files must be downloaded to the same directory for this script to run. You can edit [barcodes.csv](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/barcodes.csv) if you'd like to try posting in different barcodes.

You can run this script by typing `python postBarcodes.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script, the source .csv, and [secrets.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/secrets.py) are all saved.

#### [asLinkProfiles.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/asLinkProfiles.py)
This script assigns a single container profile to all the containers in a collection. This can be done in the actual AS interface, but serves as a good example of a more complex script. The first few actions of the script would be a good starting point for any API action that requires identifying all the containers associated with a single collection.

You can run this script by typing `python asLinkProfiles.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script and [secrets.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/secrets.py) are both saved. This script first prompts the user for a resource number, goes and fetches all the containers associated with that resource, then prompts the user for a container profile number, and then creates the link between each container and that profile. Note that there must already be container profiles in AS for this script to work.

#### [viafReconciliationCorporate.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/viafReconciliationCorporate.py)
This script looks for a CSV named _organizations.csv_ and then uses VIAF's "corporateNames" index and retrieves VIAF, Library of Congress, and International Standard Name Identifier (ISNI) URIs for each potential match. These results are written to a new file named _viafCorporateResults.csv_. Credit for this script goes to our friend and colleague [Eric Hanson](https://github.com/ehanson8 "Eric's GitHub").

The format of the  _organizations.csv_ should look like this:

| name          |
| ------------- |
| Apple Inc.    |
| New York Public Library   |
| Library of Congress|


You can run this script by typing `python viafReconciliationPeople.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script and your _organizations.csv_ is saved. An output file named _viafCorporateResults.csv_ will appear in the same directory, which you can post to ASpace using [postVIAFOrganizations.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/postVIAFOrganizations.py).


#### [postVIAFOrganizations.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/postVIAFOrganizations.py)
This script looks for the CSV called _viafCorporateResults.csv_ created by running [viafReconciliationCorporate.py](https://github.com/jhu-archives-and-manuscripts/MARAC_API_Workshop/blob/master/viafReconciliationCorporate.py), converts those reults to JSON on the fly, and then posts the resulting corporate agent records to ArchivesSpace as new records (note: this script does not edit _pre-existing_ agent records, though that is possible with a script that first GETs the agents you have, runs them through the VIAF reconciliation, and then posts them back [saying all that isn't helpful if you don't have a script that does so, but that's how you start to game out what you need]).

You can run this script by typing `python postVIAFOrganizations.py` in cygwin/the Mac terminal. Remember that you need to be running cygwin/the Mac terminal from the directory where the script and your _viafCorporateResults.csv_ is saved.



# python-scripts

#### [asCSV-aos.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/asCSV-aos.py)
Generate a CSV of all AOs from a particular resource using agentarchives.

#### [asCSV-titles.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/asCSV-titles.py)
Generate a CSV of the titles of all AOs from a particular resource using agentarchives.

#### [asLinkProfiles.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/asLinkProfiles.py)
Link a single container profile to all top_containers in a particular resource.

#### [get.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/get.py)
Simple script to get from an endpoint (currently accessions).

#### [post.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/post.py)
Post contents of a jsonfile.

#### [postNew.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/postNew.py)
Post contents of a jsonfile.

#### [suppressSelectEnumerations.py](https://github.com/jhu-archives-and-manuscripts/python_scripts/blob/master/suppressSelectEnumerations.py)
Suppress enumeration values as identified in an external json file.


# archivesspace-skill-share
Scripts used at Beyond the Basics ArchivesSpace Skill Share on Oct. 17

## Sample Files
#### [thecaptains.json](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/thecaptains.json)
A sample file of JSON data that can be used with the [postAgents.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postAgents.py) script to create ArchiveSpace Agent records via the ArchivesSpace API.

## Sample Scripts
#### [postAgents.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postAgents.py)
This script differs from the [postArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postArchivalObjects.py) script because it posts new records to ArchivesSpace rather than overwriting existing records based on their "uri."  This script requires a JSON file of agent data to be placed in the same directory as the script you will be running, in this case, the agent data is contained in "[thecaptains.json](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/thecaptains.json)."  This JSON file contains the minimum number of properties that are required to create an agent record through the API.  If you try POST to a JSON file that does that conform to ArchivesSpace's requirements, the API will provide an error message that details what required properties are missing.

#### [getArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/getArchivalObjects.py)
You can try this easy script (which makes no changes to any data). This script will authenticate with the API and then download all of ArchiveSpace's archival objects to a JSON file called "archival_objects.json." 

Note: The "page_size" is set to 3000, but ArchivesSpace's configuration defaults to 250 .
To set this within the demo, go to Files (looks like a file drawer) > archivesspace > config and look for the lines that say 

\#AppConfig[:default_page_size] = 10

\#AppConfig[:max_page_size] = 250

(Note that a # in this case comments these lines out, so you must remove the # to enable this configuration). 

#### [postArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postArchivalObjects.py)
After downloading the archival objects to a JSON file "archival_objects.json" with the [getArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/getArchivalObjects.py) script, users can edit the JSON file and post the changes back into ArchivesSpace using this [postArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postArchivalObjects.py) script. The "archival_objects.json" file needs to be in the same directory as [postArchivalObjects.py](https://github.com/jhu-archives-and-manuscripts/archivesspace-skill-share/blob/master/postArchivalObjects.py) for the script to work. The script matches each archival object based on the "uri" property and overwrites the current ArchivesSpace archival object record with the archival object record contained in the "archival_objects.json."  The "lock_version" will also need to match between the two archival objects records or the record will not be overwritten. The lock version changes every time you modify the record to prevent users from overwriting new data with old data. This built-in failsafe is a good one, but it is something to remember and plan for.



