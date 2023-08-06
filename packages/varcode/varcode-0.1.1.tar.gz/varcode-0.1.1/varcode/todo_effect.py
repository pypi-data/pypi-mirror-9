

class Effect(object):
    def __init__(
            self,
            variant,
            gene=None,
            transcript=None,
            changes_coding_sequence=False,
            changes_splicing,
            frameshift=False,):

    @property
    def number_amino_acids_removed(self):
        return 0

    @property
    def number_new_amino_acids(self):
        return 0

class MutationEffect(object):
    """Base class for mutation effects which don't overlap a transcript"""

    def __init__(self, variant):
        self.variant = variant

    def __str__(self):
        raise ValueError(
            "No __str__ method implemented for base class MutationEffect")

    def __repr__(self):
        return str(self)

    def short_description(self):
        raise ValueError(
            "Method short_description() not implemented for %s" % self)

    def gene_name(self):
        return None

    def gene_id(self):
        return None

    @property
    def old_nucleotide_sequence(self):
        return None

    @property
    def original_protein_sequence(self):
        return None

    @property
    def mutant_protein_sequence(self):
        return None

    @property
    def modifies_coding_sequence(self):
        """It's convenient to have a property which tells us:
            1) is this a variant effect overlapping a transcript?
            2) does that transcript have a coding sequence?
            3) does the variant affect the coding sequence?
        """
        return False

    @property
    def priority(self):
        # TODO: come up with rules so that we preserve the ordering
        # in effect_ordering
        flags = [
            self.overlaps_gene,
            self.overlaps_transcript,
            self.changes_coding_sequence,
            self.number_codons_added > 0,
            self.number_codons_removed > 0,
            self.number_codons_added > 1,
            self.number_codons_removed > 1,
            self.number_codons_removed > 2,
            self.number_codons_removed > 2,
            self.changes_splicing,
        ]
        total = 0
        for i, flag in enumerate(flags):
            weight = 2 ** i
            total += weight * flag
        return total