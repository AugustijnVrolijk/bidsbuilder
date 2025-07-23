Getting Started
===============

bidsbuilder needs to be clone from the github repo before installing locally:

.. code-block:: bash

   pip install -e .

this is a test of the docs and me figuring out how it works

.. code-block:: python

   from bidsbuilder import BidsDataset
   myData = BidsDataset()
   myData.build()