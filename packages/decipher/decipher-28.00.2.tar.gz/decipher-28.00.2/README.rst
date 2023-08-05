This packages permits easier access to FocusVision's Decipher tools REST API.

If you are a Decipher user, you can use the API to read and write your survey data, provision users, create surveys
and many other tasks.

If you are not a FocusVision client, visit http://ww2.focusvision.com/products/decipher  to learn more about our services.

Documentation
-------------

For an introduction to using the API, see this Knowledge Base article: http://kb.decipherinc.com/index.php?View=entry&EntryID=1717

For current API reference documentation, see https://v2.decipherinc.com/s/local/beacon.html.

Quick Examples
--------------

Install the package::

  sudo pip install decipher
  
You have three  options to authenticate against the API:

Using an **API Key**:  visit the Research Hub, and from the User Links menu (click on your picture in the upper right
corner), select API Keys. Here you can provision a new API key for yourself or another user created just for API usage.

API keys last until revoked or rekeyed. This is the preferrable method if you are using the API for automation.

If you only expect to use the API from the command line, you do not have to create an API key but can login to the
system just as if you had logged into the user interface (thus it will expire after anywhere between 15 minutes to 24
hours depending on your company's security settings). Here's an example session::

  $ beacon login

  If you are using the Beacon API for automation, you should generate and enter
  an API key. If you only need temporary access, to e.g. upload/download files
  you can enter your username/password below

  How do you want to authenticate?
  1. Enter the 64-character API key (valid until deactivated)
  2. Enter your username/password (temporary)
  3. Enter a long code (visible on the API key page)
  q. Quit
  Select 1, 2, 3 or q: x

If you select option 1::

    Enter your API key
    See http://kb.decipherinc.com/index.php?View=entry&EntryID=1717

    API KEY: **p84443bmg06skt6ceawpq4xa9qxyx8jucuxk0fz5mxuwp1v4**

    Enter your host, or press Enter for the default v2.decipherinc.com
    Host:  **yourprivatehost.decipherinc.com**

    Testing your new settings...
    Looks good. Settings were saved to the file /home/youruser/.config/decipher

If you select option 2::

    Enter your full username (email address)
    Username: ***you@company.com***

    Enter your password
    Password: **password, not shown**

    Enter your host, or press Enter for the default v2.decipherinc.com
    Host: **yourprivatehost.decipherinc.com**

    Testing your new settings...
    Acquired a temporary session key. It will be expire after 1439 minutes of idle time.
    Looks good. Settings were saved to the file /home/youruser/.config/decipher

If you select option 3::

    Visit https://v2.decipherinc.com/apps/api/keys (or private server equivalent)
    Select 'generate temporary key' then paste it below

    Temporary Key: **NDJiZD.....**

    Testing your new settings...
    Looks good. Settings were saved to the file /home/youruser/.config/decipher


The "login" action saves your API information in the file ~/.config/decipher.

From the command line you can now run the "beacon" script which lets you quickly run an API call::

  beacon -t get rh/users select=id,email,fullname,last_login_from sort=-last_login_when limit=10

The above illustrates:
 * An API call with method GET
 * Targetting the "users" resource, which will be at /api/v1/rh/users
 * Using the "projection" feature to select only 4 fields (id, email, full name and IP of last login)
 * Using the "sorting" feature to order the response by descending time of last login
 * Using the "pagination" feature to limit output to 10 first entries
 * Using the -t option to output the data as a formattet text table, rather than JSON.

If you replace the -t option with -p you will see the Python code needed for that same call:

.. code-block:: python

 from decipher.beacon import api
 users = api.get("rh/users", select="id,email,fullname,last_login_from",
  sort="-last_login_when", limit=10)
 for user in users:
    print "User #{id} <{email}> logged in last from {last_login_from}".format(user)
    

Authentication
--------------

You need an API key to use the API if you are not using a temporary, time limited login. You can supply this key
in 3 ways when connecting remotely:

By specifying it in the ~/.config/decipher file which has this format:

.. code-block:: ini

 [main]
 apikey=p84443bmg06skt6ceawpq4xa9qxyx8jucuxk0fz5mxuwp1v4
 host=v2.decipherinc.com
 
The "main" section is default, but you can select any other by using `beacon -sothersection` or
setting `api.section = "section"` before calling any API functions.

By setting an environment variable::

    export BEACON_API=1234567890abcdef1234567890abcdef
    export BEACON_HOST=v2.decipherinc.com
  
Be aware that environment variables on most UNIX systems are visible to other programs running on the same machine.

By explicitly initializing the API with login information:

.. code-block:: python

    from decipher.beacon import api
    api.login("1234567890abcdef1234567890abcdef", "v2.decipherinc.com") 
  

API Versioning
--------------

Current API uses version 1. This package will only ever do version 1 calls. To opt-in to a newer version of the API,
run (prior to doing any calls):

.. code-block:: python

 from decipher.beacon import api
 api.version = 2


We do not expect to increase the API to version 2 any time soon unless new functionality cannot be added without using
parameters with default values.

Type hints
----------

The data returned from the API is serialized as JSON. However the API also provides a "type hint" for the real object
type. This is transmitted in the `x-typehint` header which is a JSON dictionary mapping field name to type.

Unless you disable it by using `api.typehint = False`, the API will turn some of the returned objects into "enriched"
objects, and convert some types. For example, the `rh/apikeys` API returns an object containing a field named created_on which
is an ISO8601 / RFC3329 string. The typehint header tells the API client that "created_on" is a "datetime" and the API turns
this serialized datetime into an actual datetime object.

The enriched object contain methods that correspond to what you can do to this type of resource in the API as well
as easier access to build another API call to the resource for methods not wrapped by this current library version.

Command line options
--------------------

The command line script has the following options::

   beacon [options] <verb> <resource> [arg=value...]
    Verb is one of:
     get    -- list resources
     post   -- create new resource
     put    -- update existing resource
     delete -- delete or retire existing resource

     login  -- interactively define an API key and host
     rekey  -- rekey your current secret key and update the config file

    Extra arguments are decoded as JSON objects/arrays if they start with { or [ or are null

    Options:
     -v verbose (show headers sent & received))
     -t display output as an aligned text table
     -x display output as IBM JSON XML
     -p display Python code required to make the call
     -s <section> use a different section in the /home/youruser/.config/decipher file than 'main'
     -V <version> use a different API version

For example, to create a new API key for user bob@company.com, restricted only to the 8.8.8.8 IP address run::

    beacon post rh/apikeys user=bob@company.com 'restrictions={"networks":["8.8.8.8"]}'

NOTE: Because of the way the shell manages quoting, you should surround parameters which are to be sent as objects with
single quotes.

Data can be read from files rather than supplied on the command line. Use param=@filename to read the entire contents
of the file "filename". You can convert a tab-delimited file to a an array of JSON object using the syntax:
@filename@json. For example, if "data.txt" contains some data you want to upload into a survey, you can do::

    beacon post surveys/your-survey/data/edit key=source data=@data.txt@json

Which will send along the contents of the tab-delimited data.txt but convert it into an array of JSON objects first.


Meta-API
--------

APIs like the `distribute/email http://v2.decipherinc.com/s/local/beacon.html#distribution-email` let you take output of
one API call and feed it into another API. Using distribute/email you can e.g. generate one or more data files and
feed the result into distribute/email which will send the results via email as an attachment.

The beacon script provides a shortcut to compose this from the command line, using the -m option. Calling beacon -m will,
rather than performing the call, output the target and arguments in the object form consumed by meta-APIs like distribute/email.

Example composition with shell script::

    DATAMAP=$(beacon -m get surveys/demo/report/tables/datamap format=html)
    beacon post distribute/email sources=${DATAMAP}, recipients=joe@example.com, subject="Your daily datamap"

Here, the beacon -m option is used to put the string::

    {"api": "/api/v1/surveys/demo/report/tables/datamap", "method": "GET", "args": {"format": "html"}}

into the $DATAMAP shell variable, which is then passed into a call to distribute/email.

Note there are some convenience features to create arrays used above: if a SIMPLE command line argument contains or
ends with a comma, then it's assumed to be a comma-separated list of strings. This works for something like "3,4,5" or
"user@decipherinc.com,".

If it starts with {} (like the content of the DATAMAP variable) and ends with a comma it's also wrapped in an array. Here
we only look for comma at the end of the argument -- if we looked anywhere, splitting would likely destroy the JSON object.


The corresponding Python code would be::

    from decipher.beacon import api

    datamap = api.get('surveys/demo/report/tables/datamap', format='html', meta=True)
    print api.post('distribute/email', sources=[datamap],
        recipients=["joe@example.com"], subject="Your daily datamap")


Note the meta=True argument to the normal api.get call, which will not perform the call but return the meta-dictionary.

Using on a Beacon installation
------------------------------
You can use this script when logged into a Beacon instance, in which case authentication happens locally and
automatically. While in a survey directory, use "beacon ./datamap format=html" -- the ./ will be replaced with
surveys/your/survey/path/ automatically.

