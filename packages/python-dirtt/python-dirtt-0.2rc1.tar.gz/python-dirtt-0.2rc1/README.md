# python-dirtt - Directory Tree Templater



## Status and License

python-dirtt was written by [Rob Moggach](http://github.com/robmoggach)
and is  maintained by a [group of developers](https://github.com/robmoggach/python-dirtt/AUTHORS.md).
It is licensed under an [MIT-style permissive license](https://github.com/robmoggach/python-dirtt/LICENSE.md).

You can install it with ``easy_install dirtt``.

(c) 2015 Robert Moggach and contributors.

Licensed under the [MIT license](http://www.opensource.org/licenses/mit-license.php).


## What It Does

**Dirtt** is a standalone tool and library used to generate directory and file structures from xml templates that describe repeatedly used filesystem layouts such as complex project structures.

The general problem being tackled is one of inconsistent directory structures for visual effects projects, from a lack of industry standards, resulting in
lost assets, security risks, and most importantly wasted resources from inefficient production.

**Dirtt** doesn't solve that problem as a whole. It provides a command-line tool and python library that allow for quick creation of complex structures from XML templates that define directory, file and link structures as well as filesystem attributes and can reference Cheetah templates for static file customizations. The specifics of how it gets used as a tool are generic enough that it can be used for any similar task.

The package doesn't supply specific tools to do this but does include a simple example python shell script called `mkdirt`. It's basic usage is:

    mkdirt --template file:///path/to/xmls/TEMPLATE.xml --verbose --interactive

The templates that are included with **Dirtt** provide one generic example of how to use the tools. They use a simple template language that is part of the package to create a solution that is quick to customize and rapid to deploy. These can easily be edited to create working templates tailored to your needs.


## Contributing

All kinds of contributions are welcome - code, tests, documentation, bug reports, ideas, etc.

Currently we need to implement the following:

* better testing
* better error checking of values and process
* modular exceptions
* better documentation

## Forking through GitHub

First of all, you need to fork from the official repository, which is [https://github.com/robmoggach/python-dirtt](https://github.com/robmoggach/python-dirtt).

Log in to GitHub, go to the python-dirtt repository page, follow the fork link,
wait for GitHub to copy the repository and then clone your fork, like:

    git clone https://github.com/YOUR_USER_NAME/python-dirtt

Now you can change whatever you want, commit, push to your fork and when your contribution is done, follow the pull request link and send us a pull request explaining what you did and why.


## Running the tests

Dirtt's test suite is small and not comprehensive, but it does accomplish what we need it to do. Let us know if we're missing something so we can add that to the list of fixes and tests.


## Documentation

The following is a somewhat brief documentation for what is an internal tool we really should document a bit better.

In general, it should be understood that python-dirtt doesn't validate your input data and error checking is not nearly as robust as it should be. It's a pretty simple tool by design so that it can be generically used for different front ends that do all their checks and balances first. Eventually I'm sure we'll add exceptions and handling thereof but for now it does what we need it to do and we're aware of the limitations in it's exception handling.

### Installation

Once downloaded it should be as easy as typing:

    python setup.py install

and then to get the example templates and needed dtd locally:

    python setup.py install_data

Try it out in a python-virtualenv environment to play around and it should make sense quickly.

If you want to install to a custom location here's how I do it:

    pip install --install-option="--install-dir=/studio/tools/lib/python2.7/site-packages" \
    -e git+git@github.com:robmoggach/python-dirtt.git#egg=python-dirtt``

That will download and do the package build as necessary.


### XML Schema & Templates

Whether using the library, the command line tool, or customizing that same tool for your own purposes, the first thing to do is move the dirtt.dtd somewhere the python xml libraries can access. *(you can use the html link in the sample templates but it will be slow given the validation that
happens)* A shared mount makes sense.

Next as you customize the templates you'll need to change the reference to this file using urllib style references. Eg.

    file:///shared/drive/dtds/dirtt.dtd

or

    http:///intranet/dtds/dirtt.dtd

Now write your template using one of the samples. The variables you can define are below:

`name`:
	This sounds important but does basically nothing. It's a human readable name for the XML markup.
	The more important `basename` variable is described below.

`id`:
	you can assign a static id to an element in your template and then refer to it to create symbolic links using the `idref` variable.

`idref`
	Use this to reference an id in the same document and create a symbolic link. This value supersedes a dirname/basename combination when creating symbolic links. I prefer the latter though as I can see a little more clearly what the link is I'm creating. It might make sense in some situations to use IDs if you alot of links defined programatically.

`basename`:
	this is the directory or file to be created. It's the relative path or filename.
	Eg. `subdir/folder` or `default.mel`

`dirname`:
	this is the absolute path to the parent directory. For the top-level dirtt element it's required; for all others it's optional. It's useful for creating one off elements outside of the tree.

`perms`:
	This is the posix style permission string that defaults to `02775`

`username`:
	This is the owner `username` locally that will programatically be converted to `uid`.
	This allows for flexible gids based on a static name if necessary.
	(My testing environment is different so this makes it easier for local testing)

`group`:
	This is the `groupname` locally that will programatically be converted to `gid`.

Look at the examples and even try them out locally in your own test environment.

The template placeholders are defined using enclosing double curly braces.
Eg.

    {{placeholder}}

The base class does take template variables as a python dictionary but this is something you'll need to explicitly define in your python code. The sample command line tool shows a slightly crude way of doing this by prompting for values from the user. This is again to make it as generic as possible. I prefer to have the logic and error-checking in the front end as there's a ton
of different scenarios that this could be used for.

The templating class is a direct lift from PasteScript, a much bigger python package and really only in there because I didn't want to have dependencies to Cheetah or need them really.

The sample templates represent a pipeline tree derived from a number of different studios I've worked at. I've been a part of many directory tree debates over the years so it's only an example. Don't ask me for an opinion. For some reason, it's a topic of conversation that becomes very personal with supervisors, artists, TDs, engineers, etc. and because everyone has their own way of doing things, there's really no **best practice** model aside from having some system and sticking to it and focusing on automation so the
end user interaction becomes a transparent, search-free experience. Some people like `products`, others like `show/shot`, others even like to just focus mundane things like `CamelCase`, `UPPERCASE` or `lowercase`.


## Command Line Tool

The command line tool was written more to test the library itself but there's no reason it can't be used as it is. It doesn't have alot of the error checking it probably should have.

The basic usage is:

    mkdirt --template file:///path/to/xmls/TEMPLATE.xml --verbose --interactive

This command will parse the template file which needs to be defined using a urllib style string. It can be a file accessible locally or a url. So the template itself could be something that is static data or dynamically generated. The output will be verbose with the verbose flag. Interactive output as well with the interactive flag so if you create your templates using the built-in template language this tool will ask you for values to replace the placeholders.


## Links

Here's the links:

* [GitHub](https://github.com/robmoggach/python-dirtt)
* Report [Issues](https://github.com/robmoggach/python-dirtt/issues)

