Salvage
=======

.. include:: ../../README.rst


Choosing Parameters
-------------------

Salvage is designed to accomplish two somewhat competing goals: to minimize the
risk both of disclosing and of losing some piece of information. The risk of
accidental disclosure :math:`p_{disc}` can be calculated as :math:`1 - (1 -
p^t)^\binom{n}{t}` where :math:`n` is the number of participants, :math:`t` is
the recovery threshold, and :math:`p` is the probability of any given share
being disclosed. Substitute :math:`t' = n - t + 1` for :math:`t` to calculate
the risk of irretrievable data loss :math:`p_{loss}` (where :math:`p` is now the
probability of a share being lost).

High ratios of :math:`n/t` will give you a very low :math:`p_{loss}`, but
:math:`p_{disc}` could easily exceed :math:`p` itself. Very low ratios of
:math:`n/t` will do the reverse. Unless you're far more concerned with one over
the other, :math:`t` should probably be 40-60% of :math:`n`.


Practical Considerations
------------------------

The risks of disclosure and loss can never be entirely eliminated, but there are
several things that can be done to further reduce them.


Avoiding Disclosure
~~~~~~~~~~~~~~~~~~~

This is the easier one, as all of the usual rules apply. Each share of a salvage
kit should be handled as if it were the raw data. Ideally, it will only exist on
physical media and be stored like any other valuable and sensitive document. You
can always apply extra protection to each share, such as encrypting it with the
public key of the intended recipient.

Depending on your level of paranoia, you might also give some thought to how you
prepare the kit. In order to create it, you need to have the original
information assembled in the clear. If you're doing this on a normal
internet-connected machine, the data may be compromised before you've even
protected it.

Consider using a clean air-gapped machine or booting from a read-only operating
system such as `Tails <https://tails.boum.org/>`_. You might also assemble the
sensitive data in a RAM disk to avoid committing it to any persistent storage.
Similarly, when a new kit is created, all of the pieces are stored together.
Consider where these are being written and try to separate them as soon as
possible.


Avoiding Loss
~~~~~~~~~~~~~

Salvage itself takes several steps to minimize the risk that a kit will become
unrecoverable:

* Every share in a salvage kit includes a full copy of the program that created
  it. It is not necessary to download or install any Python packages in order to
  run the main script.

* Every share also includes a README with detailed instructions for using
  salvage.py. This includes instructions for OS X and Windows users who are not
  accustomed to running Python scripts.

* The README in each share also includes detailed instructions for manually
  reconstructing the master key and decrypting the data, in case the Python
  script can not be run for any reason.

Here are a few additional recommendations for minimizing the risk of ultimate
data loss:

* Store the data well. No digital media lasts forever, but do some research on
  the current state of the art. If burning to optical media, buy high quality
  media designed for archiving. It's also a good idea to print everything out on
  acid-free paper. Ink on paper lasts quite a while and OCR scanners are easy to
  come by.

* Refresh salvage kits periodically. Consider how long your storage media is
  expected to last and regenerate the kit well before that. This is also a good
  way to audit the previous kit and make sure none of the shares have gone
  missing.

* Test the recovery process. You don't necessarily need to do this with the real
  data. Create a sample recovery kit with a nonce and give it to the same people
  who hold the real thing. Make sure they can successfully reassemble the test
  kit without assistance. Add your own documentation if the standard README is
  not sufficient for your needs. (This mainly applies when your audience is not
  especially technical).


Technical Details
-----------------

This section has a quick technical description of how salvage works. The
cryptography involved is pretty trivial, so the bulk of the code is concerned
with packaging and logistics. Following is the general procedure followed to
create a new salvage kit. This is for a kit with ``n`` participants and a
threshold of ``t``.

#. The source data is archived, compressed, and encrypted with a random 128-bit
   key (rendered to a string for `gpg`_). We also use the key to generate a
   SHA-256-HMAC of the unencrypted archive.

#. For every unique set of ``t`` participants (``n choose t``), ``t - 1`` random
   keys are generated. These are combined with the master key by xoring the
   bytes to produce a final random key. We now have ``t`` partial keys that xor
   to the master key. This can be visualized as a partially filled table of key
   material, one row for each ``t``-sized subset of ``n`` and one column for
   each participant (``[0-n}``). The values in each row xor to the same master
   key.

#. ``n`` directories are created, each representing one share. Each share gets
   its own identical copy of the encrypted archive, plus some metadata in a json
   file. The metadata includes:

   * A version.
   * A common UUID identifying the kit as a whole.
   * The index of that particular share.
   * The HMAC value.
   * The values of ``n`` and ``t``.
   * A table of key material.

   The key material is essentially one column of the full key table: all of the
   partial keys that belong to this share, associated with a subgroup. In other
   words, it says "to combine shares 0, 1, and 2, use k1; else to combine shares
   0, 1, and 3, use k2; ...".

When ``t`` shares are brought together, one row of the key table can be fully
reassembled, which means the master key can be recovered and the archive
decrypted.


Changes
-------

.. include:: ../../CHANGES


LICENSE
-------

.. include:: ../../LICENSE
