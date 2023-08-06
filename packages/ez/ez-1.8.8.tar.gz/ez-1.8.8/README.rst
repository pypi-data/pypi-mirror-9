This module is for easy interaction with linux, Mac OS X, Windows shell.
=============================================
jerryzhujian9_at_gmail.com
Tested under python 2.7
To see your python version
in terminal: python -V
or in python: import sys; print (sys.version)
=============================================
Install:
https://pypi.python.org/pypi/ez
pip install ez

Almost all commands support the usage of '~', '..', '.', '?', '*' in path (ls,fls only support regular expression).
Symbolic link itself is the target of file operations; the actual file should be safe.

debug(1/0)
    # 0 = everything will be actually executed
    # 1 = simulate operations of cp, mv, execute; other commands will be actually performed.
          will print out simulated commands, useful for debugging and for counting files when necessary.
error(msg)

fullpath(path)
pwd() or cwd()  # Returns current working director.
csd(), csf()   # Returns current script directory, i.e. the directory where the running script is.
parentdir(path) # Returns the parent directory of a path.
joinpath(path1[, path2[, ...]])   # Returns the joined path. Supports vectorization.
splitpath(path) # Returns a list of path elements: [path, file, ext]. Supports vectorization.
cd(path)    # Changes to a new working directory.

join(sep,string1,string2), join(sep,array) # Glues together strings with sep. Supports vectorization.
sort(array)
replace(theList,theItem,replacement), remove(theList,theItem)

ls([path[, regex]], full=True)    # Returns a list of all (including hidden) files with their full paths in path, filtered by regular expression.
lsd([path[, regex]], full=True)
fls([path[, regex]])   # Returns a list of files with their full paths in flattened path (i.e. walk each subdirectory).
# the filter only works for short file name not for full file name, i.e. the file name itself not its full path
# regular expression is case-sensitive
# usage: ls(); ls(cwd()); ls(cwd(), "\.py$")

mkdir("path/to/a/directory")    # Makes a directory (also any one of the "path", "to", "a" directories if not exits).
rn(old, new) # Renames old to new.
exists(path)    # Returns the existence of path (0 or 1).
rm(path)    # Deletes a file or folder. Supports wildcards, vectorization.
cp(source, destination)  # Copies source file(s) or folder to destination. Supports wildcards, vectorization.
mv(source, destination)  # Moves source file(s) or folder to destination. Supports wildcards, vectorization.

execute(cmd, output=True)    # Executes a bash command with or without capturing shell output
with nooutput():
    print 'this is will not be printed in stdout'
pprint() # Pretty prints.
beep()  # Beeps to notify user.
which(name) # Prints where a module is and in which module a function is. which('python') returns which python is being used.
help(name)/doc(name) # name is a string, Prints the doc string of a module/class/function
    when write a module, add:
    __doc__ = three double quotes blabla three double quotes         <-----this is module's docstring, use explicit

    when write a function/class:
    def function(arg):
        three double quotes Returns, blabla three double quotes      <-----this is function's doctoring, use implicit
        return sth
ver(package_name) version(package_name), see a package's version.  package_name could be 'python'
whos(name),whos() list imported functions/packages

log(file="log.txt", mode='a', status=True)
    status=True (default) Prints output to both terminal and a file (log.txt, default name) globally.
    status=False Prints output only to terminal
    mode: a=append; w=overwrite
    Note: use this function carefully, because it changes the sys.stdout globally.

tree([path[, forest=True]) # Prints a directory tree structure. 
    forest=True (default) prints only folders, i.e., print less to show the big forest
    forest=False prints files plus folders

[starts, ends] = regexp(string, pattern); regexp(string, pattern, method='split/match'), regexpi
regexprep(string, pattern, replace, count=0), regexprepi

sprintf(formatString, *args)
iff(expression, result1, result2)
clear(module, recursive=False)

num(string)
isempty(s)
Randomize(x), randomize(x) # Sets a randomization seed.
RandomizeArray(list=[])   randomizearray(list=[])  # Shuffles a list in place.
Random(a,b) random(a,b) # Returns a random integer N such that a <= N <= b.
RandomChoice(seq), randomchoice(seq) # Returns a random element from sequence
Permute(iterable=[]) permute(iterable=[]) # Returns permutations in a list

unique(seq), union(seq1,seq2), intersect(seq1,seq2), setdiff(seq1,seq2) in original order
    note: setdiff(seq1,seq2) may not be equal to setdiff(seq2,seq1)
            >>> unique('abracadaba')
            ['a', 'b', 'r', 'c', 'd']
            >>> unique('simsalabim')
            ['s', 'i', 'm', 'a', 'l', 'b']
            >>>
            >>> setdiff('abracadaba','simsalabim')
            ['r', 'c', 'd']
            >>> setdiff('simsalabim','abracadaba')
            ['s', 'i', 'm', 'l']
duplicate(seq) # returns a list of duplicated elements in original order

JDict() # Jerry's dictionary, customized ordered dictionary class with convient attributes and methods, see help(JDict)
Moment(timezone)    # Generates the current datetime in specified timezone, or local naive datetime if omitted.

SetClip(content), setclip(content)   # Copy/Write something to current clipboard
content = GetClip(), content = getclip()   # Read out content from current clipboard and assign to a variable

lines(path='.', pattern='\.py$|.ini$|\.c$|\.h$|\.m$', recursive=True) # Counts lines of codes, counting empty lines as well.
keygen(length=8, complexity=3)  # generate a random key
hashes(filename): # Calculate/Print a file's md5 32; sha1 32; can handle big files in a memory efficient way

isemailvalid(email) # True or False, isEmailValid, IsEmailValid
export(input,output,options,**kwargs): # Convert url, file (html, txt), string to a single pdf





To avoid typing email password each time, place a file named pygmailconfig.py with
EMAIL = 'someone@gmail.com'
PASSWORD = 'abcdefghik'
in the site-packages/ez folder
The functions will no longer need email/password and become like this
Mail(to, subject, body, attach=None), AddEvent(event), Sheet(fileName)

Mail([EMAIL, PASSWORD, ] to, subject, body, attachment=None, bcc=None, cc=None, reply_to=None)
        to/bcc/cc: ['a@a.com','b@b.com'] or 'a@a.com, b@b.com'
        reply_to: 'a@a.com'
        attachment: 'file_in_working_dir.txt' or ['a.txt','b.py','c.pdf']
AddEvent([EMAIL, PASSWORD, ] event)     on DATE at TIME for DURATION in PLACE

Sheet([EMAIL, PASSWORD, ] fileName)
    returns a sheet object representing "Sheet 1"

    your google account doesn't have to the owner of this sheet, as long as you can edit it.
    but you need to initialize/create this sheet and maybe the header by hand to begin with
    the header could have spaces, ? etc, and when they are used as the keywords of dictionary, they are all converted to lowercase and all illegal characters are removed e.g. Delayed Test_date?  --> delayedtestdate

    fileName should be unique, can have spaces


GetRows(query=None, order_by=None,
        reverse=None, filter_func=None)
    :param query:
        A string structured query on the full text in the worksheet.
          [columnName][binaryOperator][value]
          Supported binaryOperators are:
          - (), for overriding order of operations
          - = or ==, for strict equality
          - <> or !=, for strict inequality
          - and or &&, for boolean and
          - or or ||, for boolean or.
    :param order_by:
        A string which specifies what column to use in ordering the
        entries in the feed. By position (the default): 'position' returns
        rows in the order in which they appear in the GUI. Row 1, then
        row 2, then row 3, and so on. By column:
        'column:columnName' sorts rows in ascending order based on the
        values in the column with the given columnName, where
        columnName is the value in the header row for that column.
    :param reverse:
        A string which specifies whether to sort in descending or ascending
        order.Reverses default sort order: 'true' results in a descending
        sort; 'false' (the default) results in an ascending sort.
    :param filter_func:
        A lambda function which applied to each row, Gets a row dict as
        argument and returns True or False. Used for filtering rows in
        memory (as opposed to query which filters on the service side).
    :return:
        A list of row dictionaries.


UpdateRow(row_data):
    Update Row (By ID).

    Only the fields supplied will be updated.
    :param row_data:
        A dictionary containing row data. The row will be updated according
        to the value in the ID_FIELD.
    :return:
        The updated row.


UpdateRowByIndex(index, row_data):
    Update Row By Index

    :param index:
        An integer designating the index of a row to update (zero based).
        Index is relative to the returned result set, not to the original
        spreadseet.
    :param row_data:
        A dictionary containing row data.
    :return:
        The updated row.


InsertRow(row_data):
    Append Row at the end

    :param row_data:
        A dictionary containing row data.
    :return:
        A row dictionary for the inserted row.


DeleteRow(row):
    Delete Row (By ID).

    Requires that the given row dictionary contains an ID_FIELD.
    :param row:
        A row dictionary to delete.


DeleteRowByIndex(index):
    Delete Row By Index

    :param index:
        A row index. Index is relative to the returned result set, not to
        the original spreadsheet.


DeleteAllRows():
    Delete All Rows





Attributes:
    name
    url
    html    # html code
Methods:
    __init__(source, render=False, name=None)
        # source could be url or string code
        # render requires wx/webkit to parse html
        # internally update the scraper object's attributes (e.g. url, html)
    xpath(xpath, first=False)    # first=False returns all matched as a list; first=True, first matched as string

Examples:
    / = root, // = all, [] = constriction, @ = attributes

    s = Scraper('<div>abc<a class="link">LINK 1</a><div><a>LINK 2</a>def</div>abc</div>ghi<div><a>LINK 3</a>jkl</div>')
    
    print s.xpath('/div/a')
    # ['LINK 1', 'LINK 3']

    print s.xpath('/div/a[@class="link"]')
    # ['LINK 1']

    print s.xpath('/div[1]//a')
    # ['LINK 1', 'LINK 2']

    print s.xpath('/div/a/@class')
    # ['link', '']

    print s.xpath('/div[-1]/a')
    # ['LINK 3']

    s = Scraper(u'<a href="http://www.google.com" class="flink">google</a>')
    print s.xpath('//a[@class="flink"]', 1)
    # 'google'

    # test finding just the first instance for a large amount of content
    s = Scraper('<div><span>content</span></div>' * 10000)
    print s.xpath('//span', 1)
    # 'content'

    # test extracting attribute of self closing tag
    s = Scraper('<div><img src="img.png"></div>')
    print s.xpath('/div/img/@src', 1)
    # 'img.png'

    # test extracting attribute after self closing tag
    s = Scraper('<div><br><p>content</p></div>')
    print s.xpath('/div/p')
    # 'content'

Sample:
    import time
    COL_NAME = "Words_And_Idioms"

    output = open(COL_NAME+".txt", 'w')

    for i in range(1,2):
        first = Scraper("http://www.51voa.com/"+COL_NAME+"_"+str(i)+".html")
        time.sleep(1)
        lists = first.xpath("//li")
        for item in lists:
            if "/Voa_English_Learning/" in item:
                temp = Scraper(item)
                time.sleep(1)
                link = "http://www.51voa.com"+temp.xpath("/@href",1)
                second = Scraper(link)
                time.sleep(1)
                try:
                    download = re.search("/.*/.*mp3", second.html).group(0)
                except:
                    download = "missing"
                print >> output, "http://stream.51voa.com"+download
                output.flush()
