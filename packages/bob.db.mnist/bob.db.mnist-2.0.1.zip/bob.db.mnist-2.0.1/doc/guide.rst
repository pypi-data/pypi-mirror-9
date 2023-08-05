.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

After launching the python interpreter (assuming that the environment is properly set up), you could get the training set as follows:

.. code-block:: py

  >>> import bob.db.mnist
  >>> db = bob.db.mnist.Database('PATH_TO_DATA_FROM_YANN_LECUN_WEBSITE') # 4 binary .gz compressed files
  >>> images, labels = db.data(groups='train', labels=[0,1,2,3,4,5,6,7,8,9])

In this case, this should return two :py:class:`numpy.ndarray`\s:

1. `images` contain the raw data (60,000 samples of dimension 784 [28x28 pixels images])

2. `labels` are the corresponding classes (digits 0 to 9) for each of the 60,000 samples


If you don't have the data installed on your machine, you can also use the following set of commands that will:

1. first look for the database in the ``bob/db/mnist`` subdirectory and use it if is available

2. automatically download it from Yann Lecun's website into a temporary folder that will be erased when the destructor of the :py:class:`bob.db.mnist.Database` is called.

3. automatically download it into the provided directory that will **not** be deleted.

.. code-block:: py

  >>> import bob.db.mnist
  >>> db = bob.db.mnist.Database() # Check for the data files locally, and download them if required
  >>> images, labels = db.data(groups='train', labels=[0,1,2,3,4,5,6,7,8,9])
  >>> del db # delete the temporary downloaded files if any

or:

.. code-block:: py

  >>> db = bob.db.mnist.Database("Directory") # Persistently downloads files into the folder "Directory"
  >>> images, labels = db.data(groups='train', labels=[0,1,2,3,4,5,6,7,8,9])
  >>> del db # The download directory stays

.. todo::
   Write users guide.
