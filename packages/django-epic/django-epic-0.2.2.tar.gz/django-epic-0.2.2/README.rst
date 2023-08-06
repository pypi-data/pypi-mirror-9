====
EPIC
====

EPIC stands for Electronics Parts Inventory Center and is a Django app
to track and order parts needed during Printed Circuit Boards (PCBs)
assembly.

Features:
	- automatically generate parts orders based on ordered PCBs and
          current stock at warehouses

	- parts orders take into account expected losses during assembly
	  via overage-percentage and orders are rounded up to standard-package
	  size (e.g., 10,000 parts for reels)

	- track life-time status of parts (preview, active,
          deprecated, or obsolete) and manage substitute parts

	- track shipments of parts and PCBs from vendor to destination
	  warehouse or shipments from one warehouse to another

	- view stock of each warehouse or of all warehouses together
	  for any date, e.g., for tax reporting purposes

	- see any orders that are overdue or close to being overdue

	- automatically track actual parts costs vs. expected (target) cost
	  both for individual parts and entire PCBs

	- each part links to Octopart search and can link to its data-sheet

	- each part may have one or more vendors, with automatic link to
	  vendor's page (e.g., DigiKey, Mouser, or Arrow)

	- autocompletion for part numbers, PCB footprints, orders, etc.

	- automatically generate BOM from, e.g., KiCad schematics

	- export orders, shipments, inventories and current stock to Excel

	- for KiCad users, automatically assign footprints for KiCad designs

Typical workflow:

1) Enter vendors from which you order parts and at least
   one vendor from which you order PCBs (i.e., your assembly house).

2) Enter warehouses to which parts should be shipped.  You must
   create a warehouse for each assembly house since it must receive
   parts before it can assembly them into a PCB.

3) Enter the parts you plan on using in EPIC.  For example, you'd
   enter the parts value (e.g., 1k), it's footprint, standard-package
   size (e.g., 10,000 pieces/reel), minimum overage, price, and the
   vendor(s) you're purchasing it from.

4) Design a PCB with your favorite EDA tool, for example KiCad
   (http://www.kicad-pcb.org/).

5) Export the Bill-of-Materials (BOM) from the EDA tool to EPIC.  For
   KiCad, we include a program called kicad-to-epic-bom.  This can be
   used as an Eeschema BOM-generator.  When used in this fashion,
   kicad-to-epic-bom takes care of automatically exporting a BOM to EPIC.
   It also creates a BOM in a traditional CSV text-file format.

6) Create a purchase-order for your favorite assembly-house for
   a certain quantity of your newly designed PCB.

7) EPIC uses the BOM and parts information to create one or more
   parts orders.  You can export these orders as Excel files and
   submit them to your parts vendor(s).

8) Parts get shipped from the vendor to your favorite assembly house.
   You enter these shipments into EPIC as they happen.

9) At any time, you can see if all the parts required for a PCB have
   arrived at the assembly-house.

10) Once all the parts have arrived, the assembly house builds the PCBs
    and ships the finished goods to you.  Again, you enter these shipments
    into EPIC, which will then subtract the parts used for those PCBs
    (including any overages).

11) Rinse and repeat.

Detailed documentation is in the "docs" directory.

Quick start
-----------

The quickest way to get a feel for how EPIC works is to install the
django-epic-sample package.

After installing it, cd to the installation directory and the run
the Django test server with the command:

	$ python epic-sample/manage.py runserver

Once this is running, you can point to your web-browser at:

	http://localhost:8000/epic/

and start playing around.  This sample project has a couple of sample
parts, an assembly (PCB) and some parts orders and shipments, to
hopefully give you a good idea of what working with EPIC looks like.
The look-and-feel is minimalistic, since this is intended to be the
most minimal amount of code to get a fully working EPIC.

Setup Instructions
------------------

1. Apart from the standard Django apps, ensure "epic" and its
   pre-requisites are mentioned in INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize',
        'autocomplete_light',
        'crispy_forms',
        'bootstrap3_datetime',
        'epic',
	...
    )

2. Add these to the URLconf in your project urls.py::

    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^epic/', include('epic.urls'), namespace='epic'),

3. Make sure you have a base template called 'base.html'.  EPIC expects
   this template to define two blocks: "extrahead" and "content".  The
   former must be inside the <head> tag and is used to add style-sheets
   javascript code and other pre-requisites.  The latter must be inside
   a <body> and is used to insert the actual web content.

   base.html also must include jquery and bootstrap Javascript as well
   as bootstrap css.  This can be accomplished like with these lines::

    <script type="text/javascript"
	  src="{{ STATIC_URL }}jquery/js/jquery-2.1.3.min.js"></script>
    <script type="text/javascript"
	  src="{{ STATIC_URL }}bootstrap/js/bootstrap.min.js"></script>
    <link rel="stylesheet" type="text/css"
	href="{{ STATIC_URL }}bootstrap/css/bootstrap.min.css" />

3. Run `python manage.py migrate` to create the EPIC models.

4. Visit http://127.0.0.1:8000/epic/ to start using EPIC.
