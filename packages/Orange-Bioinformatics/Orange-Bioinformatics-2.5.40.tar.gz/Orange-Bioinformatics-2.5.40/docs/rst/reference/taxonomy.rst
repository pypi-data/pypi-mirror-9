===================================
Organism Taxonomy (:mod:`taxonomy`)
===================================

.. py:currentmodule:: Orange.bio.taxonomy

This module provides access to the `NCBI's organism taxonomy information
<http://www.ncbi.nlm.nih.gov/Taxonomy/>`_ and organism name unification
across different modules.

.. autofunction:: Orange.bio.taxonomy.name(taxid)

.. autofunction:: Orange.bio.taxonomy.other_names(taxid)

.. autofunction:: Orange.bio.taxonomy.search(string, onlySpecies=True, exact=False)

.. autofunction:: Orange.bio.taxonomy.lineage(taxid)
   
..
   ..autofunction:: Orange.bio.taxonomy.to_taxid

.. autofunction:: Orange.bio.taxonomy.taxids

.. autofunction:: Orange.bio.taxonomy.common_taxids

.. autofunction:: Orange.bio.taxonomy.essential_taxids

Examples
--------

The following script takes the list of taxonomy IDs and prints out their name:

.. literalinclude:: code/taxonomy1.py

The output of the script is::

    3702   Arabidopsis thaliana
    9913   Bos taurus
    6239   Caenorhabditis elegans
    3055   Chlamydomonas reinhardtii
    7955   Danio rerio
    352472 Dictyostelium discoideum AX4
    7227   Drosophila melanogaster
    562    Escherichia coli
    11103  Hepatitis C virus
    9606   Homo sapiens
    10090  Mus musculus
    2104   Mycoplasma pneumoniae
    4530   Oryza sativa
    5833   Plasmodium falciparum
    4754   Pneumocystis carinii
    10116  Rattus norvegicus
    4932   Saccharomyces cerevisiae
    4896   Schizosaccharomyces pombe
    31033  Takifugu rubripes
    8355   Xenopus laevis
    4577   Zea mays


