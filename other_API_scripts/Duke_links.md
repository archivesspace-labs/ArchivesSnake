[All Duke AS Python scripts](https://github.com/duke-libraries/archivesspace-duke-scripts/tree/master/python)

Many of these scripts make use of CSV files to perform batch operations in ASpace. Most are not very function-based. Scripts are typically commented with more detailed explanation of functionality. Authentication methods vary. Standard disclaimers apply.

# Batch export EADs

[Batch export all EAD in repository based on finding aid status, use ead_id value as filename](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/asEADexport_public.py)
Python script to batch export all EADs from a specified repository where finding_aid_status=published and save those EADs to a specified location using the ead_id value as the filename. Can configure export parameters (include DAOs, unpublished, etc.). 

[Batch publish and export EAD based on ead_id input](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/asEADpublish_and_export_eadid_input.py)
Python script that exports EADs based on eadid input. Prompts for list of eadid values separated with commas. Checks to see if a resource's finding aid status is set to 'published'. If so, it exports the EAD to a speficied location, if not, it sets the finding aid status to "published" AND publishes the resource and all components. Then, it exports the modified EAD. See comments in script for more details.

[Batch publish and export EAD based on resource ID input](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/asEADpublish_and_export_rlid_input.py)
Same as above, but takes list of resource IDs as input

# Batch operations on digital objects

[Batch update Digital objects from CSV](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_digital_objects.py)
This script is used to batch update metadata for digital objects in ASpace using CSV input

[Batch create Digital objects from CSV, link as instances of existing Archival Objects](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_archival_object.py)
Python script that reads CSV file containing ArchivesSpace archival object ref_IDs, digital object identifiers, URLs, and file_version_use_statements and batch creates digital object records and links them as instances to existing archival object records based on the archival object's refID value. Script also outputs a CSV file including all the info in the input CSV and the URIs of the created digital objects and updated archival object records. The script prompts for the ASpace backend URL, login credentials, location of input and output CSV, and whether or not the created digital objects should be published.

[Batch update DO file version URIs based on AO refID input](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/asUpdateDAOs.py)
This script is used to update Digital Object file version URIs in ASpace based on an input CSV containing refIDs of the linked Archival Object. The 5 column CSV should look like this (without column headers):
old file version use statement, old file version URI, new file version URI, ASpace ref_id, ark identifier in repository (e.g. ark:/87924/r34j0b091)

[Batch create Archival Objects and Digital objects from CSV](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_create_ao_and_do.py)
Starting with an input CSV, this script will use the ArchivesSpace API to batch create archival object records in ASpace as children of a specified archival object parent (e.g. a series/subseries/file). The script will then create digital object records and link them as instances of the newly created archival objects. Finally, the script will write out a CSV containing the same information as the starting CSV plus the refIDs and URIs for the created archival objects and the the URIs for the created digital objects. The 9 column input csv should include a header row and be formatted with the columns identified on line 72.

[Batch create Digital Objects from CSV, using AO URIs](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_create_do_from_ao_uri.py)
Starting with an input CSV, this script will use the ArchivesSpace API to batch create digital object records and link them as instances of specified archival objects.

[Batch delete digital objects by ASpace ID](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/as-batch-delete-archival-objects.py)

[Batch delete digital objects by digital object ID](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/as-batch-delete-digital-objects-by-identifier.py)
Warning: may delete digital objects, but not digital object instances linked to archival objects

# Batch operations on archival objects

[Batch update AO titles and dates from CSV](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_ao_titles_and_dates.py)
Only updates date expression

[Batch add repository processing note from CSV, ref_ID input](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_archival_object_metadata_adder.py)

[Batch delete archival objects from CSV of IDs](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/as-batch-delete-archival-objects.py)
IDs can be obtained by querying backend database

# Batch update accessions

[Batch update single field in accession record from CSV input with accession ID](https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/python/duke_update_accessions.py)
Currently updates a user defined field. Easily modify script to target other fields
