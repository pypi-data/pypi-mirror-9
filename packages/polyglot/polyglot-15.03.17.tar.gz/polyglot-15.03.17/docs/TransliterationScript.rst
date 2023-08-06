
.. code:: python

    import sys
    import os.path as p
    from io import open
    import pickle
    import os
    import glob
    import tarfile
    from tempfile import NamedTemporaryFile
.. code:: python

    %%bash
    cd /media/data/code/polyglot/notebooks/Transliterationtable/
    mkdir -p trasnliteration2
.. code:: python

    os.chdir("/media/data/code/polyglot/notebooks/Transliterationtable/")
.. code:: python

    from transliteration import transliterate_string, transliterate_phrase
.. code:: python

    bz2file = tarfile.open("trasnliteration2/fr/transliteration.fr.tar.bz2")
    file_ = bz2file.extractfile(bz2file.next())
    #print(file_)
    weights = pickle.load(file_)
.. code:: python

    weights.keys()



.. parsed-literal::

    dict_keys(['decoder', 'encoder'])



.. code:: python

    print(transliterate_string("street", weights["decoder"], 2, 2))

.. parsed-literal::

    street


Writing Script
--------------

.. code:: python

    for f in glob.glob("*_en.pkl"):
      lang = f.rsplit("_en.pkl", 1)[0]
      weight_decoder = pickle.load(open('./en_{}.pkl'.format(lang), 'rb'))
      weight_encoder = pickle.load(open('./{}_en.pkl'.format(lang), 'rb'))
      weights = {"decoder": weight_decoder, "encoder": weight_encoder}
      dir_ = "trasnliteration2/{}".format(lang)
      os.makedirs(dir_, exist_ok=True)
      blob = pickle.dumps(weights, 2)
      tmp_file_ = NamedTemporaryFile(delete=False)
      tmp_file_.write(blob)
      tmp_file_.close()
      bz2file = tarfile.open(p.join(dir_, "transliteration.{}.tar.bz2".format(lang)), 'w:bz2')
      bz2file.add(tmp_file_.name)
      bz2file.close()
      os.remove(tmp_file_.name)