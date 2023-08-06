Friendly Sam is a software toolbox for optimization-based modelling and simulation
====================================================================================

Friendly Sam is a toolbox developed to formulate and solve optimization-based models of energy systems, but it could be used for many other systems too. Friendly Sam is designed to produce readable and understandable model specifications. It is developed with the Python ecosystem of scientific tools in mind and can be used together with numpy, pandas, matplotlib and many of your other favorite tools.

Friendly Sam is friendly in a number of ways:
----------------------------------------------

Flows of resources
    The **frien** in friendly stands for flows of resources in energy system networks. With Friendly Sam, we model power plants, energy storages, consumers and other components as nodes in a network, interconnected by flows of “resources”. Resources is a common name for all the different flows you could model: district heating and cooling, electric power, fuels, etc. 

User-friendly
    Friendly Sam is user-friendly. Instead of a global namespace with variable names like ``VHSTOLOADT``, we use object-oriented code with descriptive names like ``model[“Heat storage A”].accumulation(42)``. Your model becomes easier to write, understand and maintain.

Open source
    Friendly Sam is open source software, because we think it’s friendly and smart to collaborate. Friendly Sam is released under `LGPL v3 <https://www.gnu.org/licenses/lgpl.html>`_ license. The source code is on `GitHub <https://github.com/sp-etx/friendlysam>`_.

Install it
-------------
To install the latest release from PyPI, just do::

    pip install friendlysam

The latest version is always on `GitHub <https://github.com/sp-etx/friendlysam>`_.

Documentation
---------------------------------
`Documentation at ReadTheDocs <http://friendly-sam.readthedocs.org/en/latest/>`_.

Source code
---------------------
Source code at `GitHub <https://github.com/sp-etx/friendlysam>`_.

Contribute
---------------
Pull requests are most welcome.

