Stock production location
=========================

Tryton production orders by default take inputs from the storage
zone of the warehouse where the production is happening. On assigning
the production order tries to pick the inputs from any sublocation of
the storage zone of the warehouse where the product is available.

While this feature is handy, there are businesses which have clearly
defined processes having the inventory in designated areas for designated
purposes. It might be crucial to limit access to the ``from location``
from where inputs could be picked and the ``to location`` to which the
output could be sent to.

Features
--------

1. Ability to configure default input and output zones for production
   locations of a warehouse. For example, production location ``assembly``
   could have the default input location as ``ready to finish`` and the
   output location as ``Finished Goods``.
2. Ability to limit the locations from where the production order should
   look for inventory for inputs instead of the whole warehouse.

I don't like what this module does! 
-----------------------------------

Don't use it :-)
