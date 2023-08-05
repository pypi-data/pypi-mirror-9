SeedMe Python Client/Module
===========================

SeedMe module provides convenient utilities to interact with `web
services at SeedMe.org <https://www.seedme.org/documentation>`__. This
module provides methods for programmatic access as well as command line
interface. It performs extensive input data sanity checks to speed up
integration, interaction and testing without implementing your own REST
client for SeedMe.org. Usage information about this module is provided
below

A. `Files Provided <#markdown-header-a-files-provided_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

B. `Requirements <#markdown-header-b-requirements_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

C. `Terminology <#markdown-header-c-terminology_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

D. `Supported File Types <#markdown-header-d-supported-file-types_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

E. `Module Usage <#markdown-header-e-module-usage_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

F. `Command Line Usage <#markdown-header-f-command-line-usage_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

G. `Questions and Feedback <#markdown-header-g-questions-and-feedback_1>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

--------------

A. Files Provided
-----------------

-  `demo.py <https://bitbucket.org/seedme/seedme-python-client/src/master/demo.py?at=master>`__:
   Demonstration of using the SeedMe client/module. You must `download
   sample
   files <https://www.seedme.org/sites/seedme.org/files/downloads/sample.zip>`__
   to make use of demo.py. The sample files contains files, plots,
   sequences and videos.
-  `LICENSE.txt <https://bitbucket.org/seedme/seedme-python-client/src/master/LICENSE.txt?at=master>`__:
   License information for this module
-  `NOTICE.txt <https://bitbucket.org/seedme/seedme-python-client/src/master/NOTICE.txt?at=master>`__:
   Combined license information for thirdparty modules
-  `seedme.html <https://bitbucket.org/seedme/seedme-python-client/src/master/seedme.html?at=master>`__:
   Documentation of methods available in SeedMe Module
-  `seedme.py <https://bitbucket.org/seedme/seedme-python-client/src/master/seedme.py?at=master>`__:
   SeedMe module and command line utility
-  `setup.py <https://bitbucket.org/seedme/seedme-python-client/src/master/setup.py?at=master>`__:
   Set up file for installing SeedMe module
-  `thirdparty <https://bitbucket.org/seedme/seedme-python-client/src/master/thirdparty?at=master>`__:
   This folder contains third-party modules listed below, they are only
   used when not found on user's system

   -  thirdparty/argeparse.py : argparse module for Python 2.6
   -  thirdparty/ez\_setup.py : ez\_setup module for aiding installation
   -  thirdparty/requests : requests module if not available in user's
      Python
   -  thirdparty/simplejson : json module for Python2.6

`Top <#markdown-header-seedme-module>`__

--------------

B. Requirements
---------------

-  **Account at SeedMe.org**
-  Python 2.6 (works, but not well tested)
-  **Python 2.7 (Recommended)**
-  Python 3.x (works, but not well tested)
-  Curl executable (Optional): By default this module uses python
   requests to upload content, however it could use curl executable in
   user's environment path or a specified path.
-  `Download sample
   files <https://www.seedme.org/sites/seedme.org/files/downloads/sample.zip>`__
   containing files, plots, sequences and videos. Unzip and move this
   folder inside the module folder

`Top <#markdown-header-seedme-module>`__

--------------

C. Terminology
--------------

**Collection** is a container for any of the following elements

-  **collection\_id:** Each collection is automatically assigned a
   unique numeric identifier
-  **METADATA:** Title, Description, Key-Value Pairs, Credits, License
   for the collection
-  **FILES:** These could be files, images, videos
-  **SEQUENCES:** Set of related images
-  **TICKERS:** Short text string (128 chars) useful for monitoring
   progress `View the filetypes supported
   online <https://www.seedme.org/documentation/filetypes>`__

   **`Refer documentation <https://www.seedme.org/documentation>`__**
   for detailed description of SeedMe components and its REST like
   interface

`Top <#markdown-header-seedme-module>`__

--------------

D. Module Usage
---------------

**Who should use this method?** Power users and application integrators

1. `**Download latest SeedMe
   module** <https://bitbucket.org/seedme/seedme-python-client/get/master.zip>`__

2. **`Signup <https://www.seedme.org/user/register>`__ at seedme.org**
   Fetch your authorization credentials: username and apikey

   **Note:** apikey is different than password

3. **Download your authorization file** `Download web services
   authorization file <https://www.seedme.org/user>`__ from your
   account. After downloading move this file to your home folder

   +---------------------------------------+-----------------------------------------------------------------------------+
   | Operating System                      | Home Folder Location                                                        |
   +=======================================+=============================================================================+
   | Microsoft Windows 2000, XP and 2003   | C:and Settings<username>                                                    |
   +---------------------------------------+-----------------------------------------------------------------------------+
   | Microsoft Windows Vista, 7 and 8      | C:<username>                                                                |
   +---------------------------------------+-----------------------------------------------------------------------------+
   | Mac OS X                              | /Users/                                                                     |
   +---------------------------------------+-----------------------------------------------------------------------------+
   | Unix-Based                            | Varies, check in terminal as follows ``% echo $HOME`` OR ``% cd ~ ; pwd``   |
   +---------------------------------------+-----------------------------------------------------------------------------+

   The authorization file is a text file in json format shown below

   ``{ "username" : "YourUserName", "apikey" : "YourApiKey" }``

   **Linux and Mac Power Users**

   -  Restrict the file read privileges to yourself by issuing the
      following commands on the terminal ``% chmod 600 seedme.txt``
   -  Rename "seedme.txt" file to ".seedme" and move it to your home
      folder

4. **View available methods** See available methods in **seedme.html**
   or by running

   ``% pydoc seedme``

5. **`Download sample
   files <https://www.seedme.org/sites/seedme.org/files/downloads/sample.zip>`__**
   containing files, plots, sequences and videos. Unzip and move this
   folder inside the module folder for use with demo.py

6. **Review code provided in demo.py**

   The
   `demo.py <https://bitbucket.org/seedme/seedme-python-client/src/master/demo.py?at=master>`__
   file demonstrates how to use this module programmatically. To run the
   demo.py execute the following

   ``% python demo.py``

`Top <#markdown-header-seedme-module>`__

--------------

E. Command Line Usage
---------------------

Alternative to information below, you may use the `quick start
guide <https://www.seedme.org/quick-start>`__ on the website which
provides video and text information to get started using web browser &
command line interface

**Who should use this method?** Beginners and others who need or prefer
command line interface

1.  `**Download latest SeedMe
    module** <https://bitbucket.org/seedme/seedme-python-client/get/master.zip>`__
    - Knowledge of Python is not required

2.  **`Download sample
    files <https://www.seedme.org/sites/seedme.org/files/downloads/sample.zip>`__**
    containing files, plots, sequences and videos. Unzip and move this
    folder inside the module folder.

3.  **`Signup <https://www.seedme.org/user/register>`__ at seedme.org**
    Fetch your authorization credentials: username and apikey

    **Note:** apikey is different than password

4.  **Download your authorization file** `Download web services
    authorization file <https://www.seedme.org/user>`__ from your
    account. After downloading move this file to your home folder

    +---------------------------------------+-----------------------------------------------------------------------------+
    | Operating System                      | Home Folder Location                                                        |
    +=======================================+=============================================================================+
    | Microsoft Windows 2000, XP and 2003   | C:and Settings<username>                                                    |
    +---------------------------------------+-----------------------------------------------------------------------------+
    | Microsoft Windows Vista, 7 and 8      | C:<username>                                                                |
    +---------------------------------------+-----------------------------------------------------------------------------+
    | Mac OS X                              | /Users/                                                                     |
    +---------------------------------------+-----------------------------------------------------------------------------+
    | Unix-Based                            | Varies, check in terminal as follows ``% echo $HOME`` OR ``% cd ~ ; pwd``   |
    +---------------------------------------+-----------------------------------------------------------------------------+

    The authorization file is a text file in json format shown below

    ``{ "username" : "YourUserName", "apikey" : "YourApiKey" }``

5.  **Help**

    View all available options, usage examples and shortcuts

    ``% python seedme.py -help``

6.  **Linux and Mac Power Users**

    A. Restrict the file read privileges to yourself by issuing the
    following commands on the terminal

    ::

            % chmod 600 seedme.txt

    B. Provide execute privilege to seedme.py as follows

    ::

            % chmod u+x seedme.py

    Now seedme.py may be executed like a shell script without requiring
    python prefix.

    ::

            % ./seedme.py -help

    C. Rename "seedme.txt" file to ".seedme" and move it to your home
    folder

    D. Add the dir containing seedme.py temporarily to your environment
    path as follows

    **bash shell**

    ::

            cur_dir=`pwd`; export PATH=$PATH:$cur_dir; echo $cur_dir "added to path";

    **cshell, tcsh**

    ::

            set cur_dir=`pwd`; set path=($path $cur_dir); echo $cur_dir "added to path";

    Now seedme.py may be executed without requiring ./ prefix.

    ::

            % seedme.py -help

7.  **Command Line Shortcuts** `Top <#markdown-header-seedme-module>`__

    ::

        .------------------.-----------------.------------------.--------------------.
        | Authorization (R)| Metadata        | State            | Misc               |
        |------------------|-----------------|------------------|--------------------|
        | -ap authfile path| -c credits ^    | -cmd see curl cmd| -ca SSL cert path  |
        |  OR              | -d description ^| -CMD auth in -cmd| -cp curl path      |
        | -u username      | -kv keyvalue &^ | -dry dryrun      | -lf log file path  |
        | -a apikey        | -lic license ^  | -h help          | -post curl/requests|
        |                  | -t title #^     | -o overwrite     | -url alt REST url  |
        |                  | -tag text +&    | -s silent        | -v verbosity : INFO|
        |                  |                 | -k disable SSL   |      WARNING, ERROR|
        |                  |                 | -V see api ver   |     CRITICAL, DEBUG|
        .------------------.-----------------.------------------.--------------------.


        .------------------.------------------------------.--------------------------.
        | Privacy/Sharing +| Query Collection(s)          | Update Collection        |
        |------------------|------------------------------|--------------------------|
        |-p permission     | Query All Collections        | -up collection ID        |
        |-e email &        | -q returns id and title      |                          |
        |-n notify users   |    for all collections       |                          |
        |   with whom      | -kv keyvalue returns         |                          |
        |   collection is  |     id and title of          |                          |
        |   shared         |     collections where        |                          |
        |                  |     keyvalue is found        |                          |
        |                  |     (Requires -q option)     |                          |
        |                  |                              |                          |
        |                  | Query One Collection         |                          |
        |                  | -q ID, collection to query   |                          |
        |                  | -l list content choose one   |                          |
        |                  |    [all, kv, tic, url]       |                          |
        |                  |    (Requires -q ID option)   |                          |
        |                  | -ta tail n items, must be    |                          |
        |                  |     used in conjunction      |                          |
        |                  |     (Requires -l option)     |                          |
        .------------------.------------------------------.--------------------------.


        .------------------.------------------------------.--------------------------.
        | Ticker +         | File +                       |  Sequence +              |
        |------------------|------------------------------|--------------------------|
        | -tic ticker &    | -fd file desc ^              | -sd seq desc ^           |
        |                  | -fo file overwrite           | -se seq encode           |
        |                  | -fp file path (R)            | -so seq overwrite        |
        |                  | -ft file title ^             | -sp dir path OR path     |
        |                  |                              |     with '*' wildcard (R)|
        |                  | Options for videos only      | -spp seq poster path     |
        |                  | -fr video rate^              | -sr seq rate/fps         |
        |                  | -fe video transcode          | -st seq title #          |
        |                  | -fn video dont transcode     |                          |
        |                  | -fpp video poster path       |                          |
        |                  |                              |                          |
        |                  | Upload multiple files        |                          |
        |                  | -fp dir path OR path         |                          |
        |                  |     with * wildcard (R)      |                          |
        |                  | Must omit other options      |                          |
        .------------------.------------------------------.--------------------------.
         R Required
         + Multiple allowed in collection
         & Multiple allowed in command line
         ^ Overwrites existing
         # Recommended to be set by user
        ------------------------------------------------------------------------------

8.  **Create collection examples**
    `Top <#markdown-header-seedme-module>`__

    **A. Create a private collection**

    ``% python seedme.py -t "My Collection Title"``

    The result of this command will be similar to following, the last
    line contains a JSON string array indicating status and
    collection\_id

    ::

        Uploading chunk 1 of 1
        Attempting to create a new collection
        Success: Collection created at collection id 30858
        {"collection_id":"30858","status":"success"}

    **Note**: Here the authorization is read from file stored at default
    location ("~/seedme.txt" or "~/.seedme")

    **B. Create collection, using authorization file from custom path**

    ``% python seedme.py -ap "/custompath/my_auth_file" -t "My Title"``

    **C. Create a private collection with explicit username and
    apikey.** (Not recommended)

    ``% python seedme.py -u YourUsername -a YourApiKey -t "My Title"``

    **D. Create a public collection with title and key value pair.**

    ::

        % python seedme.py -p public \
            -t "My collection title" -d "Description of my collection" \
            -kv "magnitude:6.5" -kv "latitude:34.21° N" -kv "longitude:118.55° W"

    **Note**: Here authorization info is automatically read from
    "~/seedme.txt" or "~/.seedme"

    **E. Create a public collection with several fields.**

    The authorization info is automatically read from "~/seedme.txt" or
    "~/.seedme"

    ::

        % python seedme.py \
          -p "public" \
          -e "test1@seedme.org" -e "test2@seedme.org" \
          -t "CLI Test" \
          -d "Using CLI to interact with SeedMe.org" \
          -c "John Doe, University of Alpha Centuri" \
          -lic "CC-BY, Share alike by attribution" \
          -kv "pressure:10pa" -kv "temperature:300K" \
          -ti "t1 is 5%" -ti "t2 is 10%" \
          -sp "sample/sequences/plume_boundary" -st "seq title" -sd "desc of seq" \
          -fp "sample/videos/air.mp4" -ft "video title" -fd "desc of video" -fr 15 

    **Note**: -sp option is a dir path, which non-recursively scans for
    files and uploads them

    **Note**: -se option will trigger video creation from the uploaded
    sequence. The sequence itself is not automatically deleted from the
    collection.

    **Note**: Videos are automatically transcoded, use -fn option to
    supress transcoding

9.  **Append/Update collection examples**
    `Top <#markdown-header-seedme-module>`__

    Recall from above steps, that when a collection is created we
    receive a unique **collection\_id** as output. We will now use that
    id to update or append other items to this collection. In case you
    don't know the collection\_id, you may login to seedme.org and
    identify the collection\_id for amendment

    **A. Add/Update title to collection id 666.**

    The authorization info is automatically read from "~/seedme.txt" or
    "~/.seedme"

    ``% python seedme.py -up 666 -t "New Title"``

    **Note: Update Collection\_ID -up 666 option is required to update a
    collection.** If this is not provided a new collection will be
    created.

    **B. Change privacy of a collection with id 666 to group.**

    The authorization info is read from "~/seedme.txt" or "~/.seedme"

    ``% python seedme.py -up 666 -p group``

    **C. Notify users with whom we shared the collection during
    creation**

    The authorization info is automatically read from "~/seedme.txt" or
    "~/.seedme"

    % python seedme.py -up 666 -n

    **Note: Notification is NOT automatic**. You decide when share
    notification should be sent

    **D. Add file to collection id 666.**

    The authorization info is automatically read from "~/seedme.txt" or
    "~/.seedme"

    ``% python seedme.py -up 666 -fp "sample/files/doc.pdf"``

    **E. Append image to a sequence at collection id 666.**

    The authorization info is automatically read from "~/seedme.txt" or
    "~/.seedme"

    ``% python seedme.py -up 666 -st "my sequence title" -sp "sample/sequence/steam/steam_rotation0360.png"``

    **Note:** Sequence title -st "my sequence title" is required\*\* to
    append to a sequence, as we need to identify the sequence where the
    image should be appended. If the sequence title is not provided a
    new sequence will be created.

10. **Query all collection examples**
    `Top <#markdown-header-seedme-module>`__

    **A. Query to list all your collections**.

    List all your collections ``% python seedme.py -q``

    Add '-tail 5' to restrict items to last 5

    **Note:** Only the collections you own are returned.

    **B. Query to find collections that match all specified key value
    pairs**

    ``% python seedme.py -q -kv "ssid:expt11"``

    Add '-tail 5' to restrict items to last 5

    **Notes:** Only the collections you own are searched. Key value pair
    search is not case sensitive.

    Add '-tail 5' to restrict the returned items to last 5

11. **Query one collection examples**
    `Top <#markdown-header-seedme-module>`__

    **A. Query to list all contents for a specified collection**

    ``% python seedme.py -q 666``

    Above is same as ``% python seedme.py -q 666 -l all``

    **Notes:** Any collections that you own or shared or public can be
    queried. **Limitations:**\ Urls are only listed for public
    collections. Query omits sequence information at present (Under
    development).

    **B. Query to list key value pairs for a specified collection**

    ``% python seedme.py -q 666 -l kv``

    Add '-tail 5' to restrict items to last 5

    **Notes:** Any collections that you own or shared or public can be
    queried.

    **C. Query to list file urls for a specified collection**

    ``% python seedme.py -q 666 -l url``

    Add '-tail 5' to restrict items to last 5

    **Notes:** Any collections that you own or shared or public can be
    queried. **Limitations:**\ Urls are only listed for public
    collections. Query omits sequence information at present (Under
    development).

    **D. Query to list last 5 tickers for a specified collection**

    ``% python seedme.py -q 666 -l tic -ta 5``

    **Note:** Any collections that you own or shared or public can be
    queried.

12. **Download files from specified collection**

    **A. Download all files from a specified collection**
    ``% python seedme.py -dl 666 all``

    **Notes:** Only public collection content can be downloaded.
    Sequence file download not supported at present (Under development).
    Default download location is "~/Downloads". By default existing
    files are incremented not overwritten, to overwrite add option -o

    **B. Download files with wild card string from a specified
    collection** ``% python seedme.py -dl 666 *png``

    **Notes:** Only public collection content can be downloaded.
    Sequence file download not supported at present (Under development).
    Default download location is "~/Downloads". By default existing
    files are incremented not overwritten, to overwrite add option -o

    **C. Download video files from a specified collection**
    ``% python seedme.py -dl 666 video``

    **Notes:** Only public collection content can be downloaded. Default
    download location is "~/Downloads". By default existing files are
    incremented not overwritten, to overwrite add option -o

13. **Dry Run** `Top <#markdown-header-seedme-module>`__

    Perform input validation test of all options provided. The
    validation is run locally.

    ``% python seedme.py -dry -up 666 -fp "sample/files/how_it_works.pdf"``

    **Note**: collection\_id -1 is used to mock updates to a
    non-existent collection

14. **Show curl commands with and without authorization information**

    Show corresponding curl commands for a given input **without
    uploading. The authorization information is hidden.**

    ``% python seedme.py -cmd -dry -up 666 -fp "sample/files/how_it_works.pdf"``

    To unhide username and apikey use **-CMD flag** Note: upper case

    ``% python seedme.py -CMD -dry -up 666 -fp "sample/files/how_it_works.pdf"``

    **Note**: Removing -dry above will upload the content using curl and
    and show curl command options as well.

15. **Log output to a file**

    ``% python seedme.py -cmd -dry -lf log.txt``

    **Note**: Just including **-lf log.txt** will write the output to
    log.txt file, but will still display output on the terminal

    ``% python seedme.py -cmd -dry -lf log.txt -s``

    **Note**: For complete silence on the terminal **include -s flag**.
    **Caution**: Using -s during collection creation is not recommended
    as you will not be able to get the collection id in command line.
    You may still fetch it by logging it via web browser.

16. **Show web api version and service url**

    ``% python seedme.py -V``

`Top <#markdown-header-seedme-module>`__

--------------

F. Questions and Feedback
-------------------------

Send your comments via the Contact-Us online form at
http://www.seedme.org/contact

`Top <#markdown-header-seedme-module>`__
