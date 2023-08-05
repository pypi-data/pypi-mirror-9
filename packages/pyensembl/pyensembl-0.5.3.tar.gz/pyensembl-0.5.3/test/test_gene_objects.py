from test_common import test_ensembl_releases
from data import TP53_gene_id

@test_ensembl_releases()
def test_TP53_gene_object_by_id(release):
    # when we look up TP53 by its gene ID, we should get the
    # correct gene back
    gene = release.gene_by_id(TP53_gene_id)
    assert gene.name == "TP53", \
        "Incorrect gene name %s for gene ID %s in %s" % (
            gene.name, gene_id, release)
    assert gene.contig == "17", \
        "Incorrect gene contig %s for gene ID %s in %s" % (
            gene.contig, gene_id, release)

@test_ensembl_releases()
def test_TP53_gene_object_by_name(release):
    genes = release.genes_by_name("TP53")
    # we should only have one TP53 gene (there aren't any copies)
    assert len(genes) == 1, \
        "Expected only one gene with name TP53, got %s" % (genes,)
    # make sure it has the correct gene ID
    assert genes[0].id == TP53_gene_id, \
        "Expected gene to have ID %s, got %s" % (TP53_gene_id, genes[0].id)
