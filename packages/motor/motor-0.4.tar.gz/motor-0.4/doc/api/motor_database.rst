:class:`MotorDatabase`
======================

.. currentmodule:: motor

.. autoclass:: motor.MotorDatabase
  :members:

  .. describe:: db[collection_name] || db.collection_name

     Get the `collection_name` :class:`MotorCollection` of
     :class:`MotorDatabase` `db`.

     Raises :class:`~pymongo.errors.InvalidName` if an invalid collection name is used.
