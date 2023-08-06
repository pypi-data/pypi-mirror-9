NaremitCMS DocImport
====================

An application for NaremitCMS. NaremitCMS isn't ready just yet, but when it is...

## What it does

Import markdown or reStructured Text files directly into the CMS. Use it for documentation (ala Sphinx) or for complete websites, very much like Jekyll. Combine this with NaremitCMS exporter functionality for a complete, out-of-the-box Jekyll-like experience from Django.

## Installation

After installing Django and NaremitCMS, install this application:

    pip install django-naremitcms-docimport

Add `naremitcms_docimport` to your INSTALLED_APPS setting then run `python manage.py migrate`. By default this app uses markdown so you will need to install that too:

    pip install markdown

If you prefer reStructured Text, install that instead:

    pip install docutils

## Create your application(s)

Next, create and register a NaremitCMS application (docs coming soon). Here is an example:

```
from naremitcms_docimport.docimport import DocImportApplication

class MyDocumentation(DocImportApplication):
    DATA_DIR = '/path/to/markdown/files'
```

There are three settings to add:

1. `DATA_DIR` (required). The directory the text files live in.
1. `MARKUP` (optional). Either "markdown" or "rest".
1. `TEMPLATE` (optional). Set this to be the rtemplate file you wish to use. An example is included.

## File Format

Each text file should be named in the following manner:

1. Tree number, i.e. "1" depicting the first document, "1.1" being the first child of the first document, "1.2" being the second child of the first document, etc.
1. " - ", i.e. a space, followed by a hyphen, by space
1. Document title text
1. Filename suffix, e.g. ".txt" or ".md"

Example names:
```
1 - Getting Started.txt
1.1 - What it does.txt
1.2 - Installaton.txt
1.3 - Create your applications.txt
2 - Data Files.txt
2.1 - File Format.txt
2.1.1 - Example File.txt
```
The benefit here is that the text files are shown in the correct order in your files list, and it is obvious to both humans and this application the structure the documents should be formatted in. The tree structure can go any number of levels deep.

## Usage

Finally, run `python manage.py docimport` to import the documents for each DocImport application you have defined in your project.

## Todo

Complete the sitemap functionality (not ready in NaremitCMS itself yet)
