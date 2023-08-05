from biotypes import is_valid_biotype
from locus import Locus
from transcript import Transcript

from memoized_property import memoized_property

class Gene(Locus):

    def __init__(self, gene_id, db):
        if not isinstance(gene_id, (unicode, str)):
            raise TypeError(
                "Expected gene ID to be string, got %s : %s" % (
                    gene_id, type(gene_id))
            )

        self.id = gene_id
        self.db = db
        columns = [
            'gene_name',
            'seqname',
            'start',
            'end',
            'strand',
            'gene_biotype'
        ]
        gene_name, contig, start, end, strand, biotype = self.db.query_one(
            columns,
            filter_column='gene_id',
            filter_value=gene_id,
            feature='gene')
        if not gene_name:
            raise ValueError("Missing name for gene with ID = %s" % gene_id)
        self.name = gene_name

        Locus.__init__(self, contig, start, end, strand)

        if not biotype:
            raise ValueError(
                "Missing gene_biotype for gene with ID = %s" % gene_id)
        elif not is_valid_biotype(biotype):
            raise ValueError(
                "Invalid gene_biotype %s for gene with ID = %s" % (
                    biotype, gene_id))
        self.biotype = biotype

    def __str__(self):
        return "Gene(id=%s, name=%s)" % (self.id, self.name)

    def __repr__(self):
        return str(self)

    @memoized_property
    def transcripts(self):
        """
        Property which dynamically construct transcript objects for all
        transcript IDs associated with this gene.
        """
        transcript_ids_query = """
            SELECT transcript_id
            FROM ensembl
            WHERE gene_id = ?
            AND feature = 'transcript'
        """
        cursor = self.db.execute(transcript_ids_query, [self.id])
        results = cursor.fetchall()

        # We're doing a SQL query for each transcript ID to fetch
        # its particular information, might be more efficient if we
        # just get all the columns here, but how do we keep that modular?
        return [
            Transcript(result[0], self.db)
            for result in results
        ]

    @memoized_property
    def exons(self):
        exons_dict = {}
        for transcript in self.transcripts:
            for exon in transcript.exons:
                if exon.id not in exons_dict:
                    exons_dict[exon.id] = exon
        return list(exons_dict.values())

